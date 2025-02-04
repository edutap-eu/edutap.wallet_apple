# Inegration of 'edutap.walle_apple into your project


If your project wants to handle the Apple Update Services you need to add the following dependencies to your `pyproject.toml` file:

```toml
dependencies = [
    "fastapi",
    "edutap.wallet_apple",
...
]
```

## Environment Variables

you need to set the following environment variables:

```
EDUTAP_WALLET_APPLE_CERT_DIR=<path to the directory where the certificates are stored>
EDUTAP_WALLET_APPLE_TEAM_IDENTIFIER=<your team identifier>
EDUTAP_WALLET_APPLE_FERNET_KEY=<your fernet key>
```

## Storing Certificates

The certificates are stored in the directory specified in the `EDUTAP_WALLET_APPLE_CERT_DIR` environment variable. 

you need to store the following files in the directory:

- `private.key`  (the private key)
- `certificate-{pass type identifier}.pem` (for each pass type identifier)
- `wwdr_certificate.pem`    (the Apple root certificate)

A detailled description how to create and get the certificates can be found in the [installation documentation](installation.md)

## Entry Points

edutap.wallet_apple provides the following entry points:

- PassRegistration
- PassDataAcquisition
- Logging

you can write your own handlers for these entry points and register them in your application.

therefore you need to specify the following section in your `pyproject.toml` file:

```toml
[project.entry-points.'edutap.wallet_apple.plugins']
PassRegistration = '<your plugin module>:PassRegistration'
PassDataAcquisition = '<your plugin module>:PassDataAcquisition'
Logging = '<your plugin module>:Logging'
```

If you want to specify additional handlers for logging you have to name them `Logging1`, `Logging2`, etc.
The entry points handlers are searched by the Prefixes `Logging` and `PassRegistration`. For PassDataAcquisition only one handler can be registered.