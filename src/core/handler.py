import jsons
import re
import logging
import inspect

__RESOLVE_DICT__ = {}


logger = logging.getLogger(__name__)


def resolve(message: str):
    try:
        payload = jsons.loads(message)

        command = payload.get("cmd", None)
        arguments = payload.get("args", {})

        handler = __RESOLVE_DICT__[command]
        parameters = list(inspect.signature(handler).parameters.keys())
        arguments = [arguments[parameter] for parameter in parameters if parameter in arguments]

        return jsons.dumps(handler(*arguments), default=lambda x: x.__dict__)
    except KeyError as e:
        return jsons.dumps({"message": f'The command {e} is not found.'})
    except Exception as e:
        logger.error(e)
        return jsons.dumps({"message": "An unhandled error occured."})


def handle(command: str = None):
    def handler_decorator(handler):
        key = re.sub('handler$', "", handler.__name__.lower()) if command is None else command
        logger.info("{} registered {}.".format(handler.__name__, key))
        __RESOLVE_DICT__[key] = handler

        return handler

    return handler_decorator
