# Copyright 2025 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import abc
import asyncio
import logging
from typing import TYPE_CHECKING

import websockets

from juju.client import client
from juju.delta import get_entity_delta
from juju.errors import JujuAPIError, JujuError
from juju import utils

from juju.client.overrides import Delta

if TYPE_CHECKING:
    from juju.model import Model

log = logging.getLogger(__name__)


class StateUpdater(abc.ABC):
    """Abstract base class for model state updaters."""

    def __init__(self, model: "Model"):
        self.model = model
        self._stopping = asyncio.Event()
        self._stopped = asyncio.Event()
        self._stopped.set()
        self._task = None

    @abc.abstractmethod
    def start(self):
        """Start the updater task."""
        pass

    async def stop(self):
        """Stop the updater task."""
        if not self._stopped.is_set():
            log.debug("Stopping updater task")
            self._stopping.set()
            if self._task:
                try:
                    # Wait for the task to finish
                    if not self._task.done():
                        await self._stopped.wait()
                    
                    # Check for exceptions
                    if self._task.done() and self._task.exception():
                        # If the exception is CancelledError, we can ignore it
                        if not isinstance(self._task.exception(), asyncio.CancelledError):
                            raise self._task.exception()
                except asyncio.CancelledError:
                    pass
            self._stopping.clear()

    @property
    def task(self):
        return self._task


class AllWatcherUpdater(StateUpdater):
    """Updates model state using the AllWatcher facade (Juju < 4)."""

    def start(self):
        log.debug("Starting AllWatcher updater task")
        self._stopping.clear()
        self._stopped.clear()
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        # First attempt to get the model config so we know what mode the
        # library should be running in.
        try:
            model_config = await self.model.get_config()
            if "mode" in model_config:
                self.model._mode = model_config["mode"]["value"]
        except Exception:
            # If we can't get config, maybe we are not connected or something else.
            # But we should proceed to watch if possible.
            log.warning("Could not get model config before starting watcher", exc_info=True)

        try:
            allwatcher = client.AllWatcherFacade.from_connection(self.model.connection())
            while not self._stopping.is_set():
                try:
                    results = await utils.run_with_interrupt(
                        allwatcher.Next(), self._stopping, log=log
                    )
                except JujuAPIError as e:
                    if "watcher was stopped" not in str(e):
                        raise
                    if self._stopping.is_set():
                        break
                    log.warning("Watcher: watcher stopped, restarting")
                    del allwatcher.Id
                    continue
                except websockets.ConnectionClosed:
                    if self.model.connection().monitor.status == self.model.connection().monitor.ERROR:
                        log.warning("Watcher: connection closed, reopening")
                        await self.model.connection().reconnect()
                        if (
                            self.model.connection().monitor.status
                            != self.model.connection().monitor.CONNECTED
                        ):
                            log.error(
                                "Watcher: automatic reconnect "
                                "failed; stopping watcher"
                            )
                            break
                        del allwatcher.Id
                        continue
                    else:
                        break
                
                if self._stopping.is_set():
                    try:
                        await allwatcher.Stop()
                    except websockets.ConnectionClosed:
                        pass
                    break

                for delta in results.deltas:
                    entity = None
                    try:
                        entity = get_entity_delta(delta)
                    except KeyError:
                        if self.model.strict_mode:
                            raise JujuError(f"unknown delta type '{delta.entity}'")

                    if not self.model.strict_mode and entity is None:
                        continue
                    old_obj, new_obj = self.model.state.apply_delta(entity)
                    await self.model._notify_observers(entity, old_obj, new_obj)
                    self._post_step(new_obj)
                
                self.model._watch_received.set()
        except asyncio.CancelledError:
            pass
        except Exception:
            log.exception("Error in watcher")
            raise
        finally:
            self._stopped.set()

    def _post_step(self, obj):
        # Once we get the model, ensure we're running in the correct state
        # as a post step.
        if obj and obj.entity_type == "model" and obj.safe_data is not None:
            model_config = obj.safe_data["config"]
            if "mode" in model_config:
                self.model._mode = model_config["mode"]

class PollingUpdater(StateUpdater):
    """Updates model state using polling (Juju 4+)."""

    def __init__(self, model: "Model"):
        super().__init__(model)
        self._previous_state = {}

    def start(self):
        log.debug("Starting Polling updater task")
        self._stopping.clear()
        self._stopped.clear()
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        try:
            client_facade = client.ClientFacade.from_connection(self.model.connection())
            while not self._stopping.is_set():
                try:
                    status = await client_facade.FullStatus()
                    await self._update_state(status)
                    self.model._watch_received.set()
                except websockets.ConnectionClosed:
                    if self.model.connection().monitor.status == self.model.connection().monitor.ERROR:
                        log.warning("PollingUpdater: connection closed, reopening")
                        await self.model.connection().reconnect()
                        if (
                            self.model.connection().monitor.status
                            != self.model.connection().monitor.CONNECTED
                        ):
                            log.error(
                                "PollingUpdater: automatic reconnect "
                                "failed; stopping updater"
                            )
                            break
                        # Re-create facade after reconnect
                        client_facade = client.ClientFacade.from_connection(self.model.connection())
                        continue
                    else:
                        break
                except Exception:
                    log.exception("Error in polling updater")
                    # Wait a bit before retrying to avoid tight loop on error
                    await asyncio.sleep(1)
                
                await asyncio.sleep(1) # Poll interval
        except asyncio.CancelledError:
            pass
        finally:
            self._stopped.set()

    async def _update_state(self, status):
        current_state = self._flatten_full_status(status)
        
        deltas = []
        
        # Add/Change
        for key, data in current_state.items():
            entity_type, entity_id = key
            if key not in self._previous_state:
                deltas.append(Delta(deltas=(entity_type, "add", data)))
            elif self._previous_state[key] != data:
                deltas.append(Delta(deltas=(entity_type, "change", data)))
        
        # Remove
        for key in self._previous_state:
            if key not in current_state:
                entity_type, entity_id = key
                # For remove, we typically just need the ID.
                # Construct a minimal data dict with the ID.
                remove_data = {}
                if entity_type == "application":
                    remove_data["name"] = entity_id
                elif entity_type == "unit":
                    remove_data["name"] = entity_id
                elif entity_type == "machine":
                    remove_data["id"] = entity_id
                elif entity_type == "relation":
                    remove_data["id"] = entity_id
                elif entity_type == "model":
                    remove_data["model-uuid"] = entity_id
                
                deltas.append(Delta(deltas=(entity_type, "remove", remove_data)))
        
        self._previous_state = current_state
        
        for delta in deltas:
            try:
                entity = get_entity_delta(delta)
            except KeyError:
                if self.model.strict_mode:
                    raise JujuError(f"unknown delta type '{delta.entity}'")
                continue

            if not self.model.strict_mode and entity is None:
                continue
            
            old_obj, new_obj = self.model.state.apply_delta(entity)
            await self.model._notify_observers(entity, old_obj, new_obj)

    def _flatten_full_status(self, status):
        flat = {}
        
        # Model
        if status.model:
            data = status.model.serialize()
            data["model-uuid"] = self.model.uuid
            flat[("model", self.model.uuid)] = data

        # Applications
        if status.applications:
            for app_name, app_status in status.applications.items():
                data = app_status.serialize()
                data["name"] = app_name
                flat[("application", app_name)] = data
                
                # Units
                if app_status.units:
                    for unit_name, unit_status in app_status.units.items():
                        unit_data = unit_status.serialize()
                        unit_data["name"] = unit_name
                        flat[("unit", unit_name)] = unit_data

        # Machines
        if status.machines:
            for machine_id, machine_status in status.machines.items():
                data = machine_status.serialize()
                data["id"] = machine_id
                flat[("machine", machine_id)] = data

        # Relations
        if status.relations:
            for relation in status.relations:
                rel_id = str(relation.id_)
                data = relation.serialize()
                data["id"] = rel_id
                flat[("relation", rel_id)] = data
        
        return flat
