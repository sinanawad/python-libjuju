# API Contracts: Juju 4 Adaptation

## Model Class (`juju/model/__init__.py`)

### `deploy`
```python
async def deploy(
    self,
    entity_url: str,
    application_name: str = None,
    base: str = None,  # REQUIRED for Juju 4
    series: str = None, # FORBIDDEN for Juju 4
    # ... other args
) -> Application:
    """
    Deploys a charm.
    
    Raises:
        ValueError: If connected to Juju 4 and `series` is provided.
        ValueError: If connected to Juju 4 and `base` is missing (and cannot be inferred).
    """
```

### `wait_for_idle`
```python
async def wait_for_idle(
    self,
    apps: List[str] = None,
    status: str = None,
    timeout: int = None,
    # ...
):
    """
    Waits for applications to reach a specific state.
    
    Implementation Note:
        - Juju 3: Uses AllWatcher events.
        - Juju 4: Uses Polling/Targeted Watchers.
    """
```

### `add_secret` (New)
```python
async def add_secret(
    self,
    name: str,
    data: Dict[str, str],
    description: str = None,
) -> Secret:
    """
    Creates a new secret.
    """
```

## Secret Class (`juju/secrets.py` - New)

```python
class Secret(Entity):
    async def grant(self, application: str):
        pass

    async def revoke(self, application: str):
        pass

    async def update(self, data: Dict[str, str] = None, label: str = None):
        pass

    async def remove(self):
        pass
```
