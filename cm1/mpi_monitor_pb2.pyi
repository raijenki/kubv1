from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Confirmation(_message.Message):
    __slots__ = ["confirmMessage"]
    CONFIRMMESSAGE_FIELD_NUMBER: _ClassVar[int]
    confirmMessage: str
    def __init__(self, confirmMessage: _Optional[str] = ...) -> None: ...

class availNodes(_message.Message):
    __slots__ = ["nodes"]
    NODES_FIELD_NUMBER: _ClassVar[int]
    nodes: int
    def __init__(self, nodes: _Optional[int] = ...) -> None: ...

class nodeName(_message.Message):
    __slots__ = ["nodeName"]
    NODENAME_FIELD_NUMBER: _ClassVar[int]
    nodeName: str
    def __init__(self, nodeName: _Optional[str] = ...) -> None: ...
