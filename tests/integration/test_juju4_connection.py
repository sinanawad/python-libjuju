# Copyright 2025 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import asyncio
import pytest
from juju.model import Model
from juju.controller import Controller
from juju.model.state_updater import PollingUpdater
from .. import base

@base.bootstrapped
@pytest.mark.asyncio
async def test_juju4_connection():
    """
    Test that we can connect to a Juju 4 controller.
    This test assumes the environment is bootstrapped with Juju 4.
    """
    # Test Controller connection first
    controller = Controller()
    await controller.connect()
    try:
        print(f"Connected to Controller version: {controller.connection().info['server-version']}")
        assert controller.is_connected()
    finally:
        await controller.disconnect()

    # Test Model connection
    try:
        async with asyncio.timeout(30):
            async with base.CleanModel() as model:
                try:
                    # Check if we are connected to Juju 4
                    # We can check the agent version from model info
                    version = model.info.agent_version
                    print(f"Connected to Model version: {version}")
                    
                    assert model.is_connected()
                    
                    # Verify we are using PollingUpdater
                    assert isinstance(model._updater, PollingUpdater)
                    
                    # Verify we can access model state
                    assert model.state is not None
                    
                    # Verify we can list applications (even if empty)
                    apps = model.applications
                    assert isinstance(apps, dict)
                finally:
                    # CleanModel handles disconnect, but we can double check or just let it be
                    pass
    except asyncio.TimeoutError:
        pytest.fail("Test timed out connecting to model")
