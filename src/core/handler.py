import jsons
import re
import logging
import inspect

from .dto import Event, ResultEvent

__RESOLVE_DICT__ = {}


logger = logging.getLogger(__name__)


def resolve(message: str):
    try:
        event = Event.from_json(message)

        name = event.event
        data = event.data

        if name == "exec":
            command = data.get("cmd", "")
            arguments = data.get("args", {})

            handler = __RESOLVE_DICT__[name][command]

            parameters = list(inspect.signature(handler).parameters.keys())
            arguments = [data.args[parameter] for parameter in parameters if parameter in arguments]

            result = ResultEvent(command, handler(*arguments))

            return result.to_json()
        else:
            return None
    except KeyError as e:
        return jsons.dumps({"message": f'The command {e} is not found.'})
    except Exception as e:
        logger.exception(e)
        return jsons.dumps({"message": "An unhandled error occured."})


def handle(command: str = None, event: str = "exec"):
    def handler_decorator(handler):
        key = re.sub('handler$', "", handler.__name__.lower()) if command is None else command
        logger.info("{} registered {}@{}.".format(handler.__name__, event, key))

        if event not in __RESOLVE_DICT__:
            __RESOLVE_DICT__[event] = {}

        __RESOLVE_DICT__[event][key] = handler

        return handler

    return handler_decorator
