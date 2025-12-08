# Quickstart: Juju 4 Adaptation

## Connecting to Juju 4

```python
from juju.model import Model

async def main():
    model = Model()
    # Connects to current controller (Juju 4 supported)
    await model.connect()
    
    print(f"Connected to {model.info.agent_version}")
```

## Deploying with Base

```python
# CORRECT (Juju 4)
app = await model.deploy('ubuntu', base='ubuntu@22.04')

# INCORRECT (Juju 4 - will raise Error)
# app = await model.deploy('ubuntu', series='jammy')
```

## Managing Secrets

```python
# Create a secret
secret = await model.add_secret(
    name='db-password',
    data={'password': 'super-secure'}
)

# Grant to an app
await secret.grant('my-app')
```
