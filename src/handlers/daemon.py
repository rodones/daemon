import os
import signal
from core.handler import handle


@handle("daemon/whoami")
def whoami():
    return os.getenv("RODONESD_KEY")


@handle("daemon/die")
def die(message):
    os.kill(os.getpid(), signal.SIGTERM)

    return f'terminating... (cause: {message})'
