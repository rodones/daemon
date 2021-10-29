from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generic, TypeVar, TypedDict

import jsons

T = TypeVar('T')


@dataclass
class Event(Generic[T]):
    event: str
    data: T = field(default=None, init=False)

    def __init__(self) -> None:
        super().__init__()

    def to_json(self) -> str:
        return jsons.dumps(asdict(self))

    @staticmethod
    def from_json(text) -> 'Event[Any]':
        parsed = jsons.loads(text)
        event = Event()
        event.event = parsed["event"]
        event.data = parsed["data"]

        return event


class ExecData(TypedDict):
    cmd: str
    args: Dict[str, Any]


@dataclass
class ExecEvent(Event[ExecData]):
    event = "exec"

    def __init__(self, cmd: str, **args):
        self.data = {"cmd": cmd, "args": args}


@dataclass
class ResultEvent(Event):
    event = "result"

    def __init__(self, cmd: str, result: Any):
        self.data = {"cmd": cmd, "result": result}
