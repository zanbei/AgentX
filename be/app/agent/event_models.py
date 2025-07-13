from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from uuid import UUID


class EventLoopMetrics(BaseModel):
    cycle_count: int
    tool_metrics: Dict[str, Any] = {}
    cycle_durations: List[float] = []
    traces: List[Any] = []
    accumulated_usage: Dict[str, int] = {}
    accumulated_metrics: Dict[str, int] = {}


class ToolMetrics(BaseModel):
    tool: Dict[str, Any]
    call_count: int
    success_count: int
    error_count: int
    total_time: float


class ContentBlockDelta(BaseModel):
    delta: Dict[str, Any]
    contentBlockIndex: int


class ContentBlockStart(BaseModel):
    start: Dict[str, Any]
    contentBlockIndex: int


class ContentBlockStop(BaseModel):
    contentBlockIndex: int


class MessageStart(BaseModel):
    role: str


class MessageStop(BaseModel):
    stopReason: str


class MetadataEvent(BaseModel):
    usage: Dict[str, int]
    metrics: Dict[str, int]


class ToolUse(BaseModel):
    toolUseId: str
    name: str
    input: Dict[str, Any]


class TextContent(BaseModel):
    text: str


class ToolResult(BaseModel):
    status: str
    content: List[Dict[str, Any]]
    toolUseId: str


class MessageContent(BaseModel):
    text: Optional[str] = None
    toolUse: Optional[ToolUse] = None
    toolResult: Optional[ToolResult] = None


class Message(BaseModel):
    role: str
    content: List[MessageContent]


# Event types
class EventType(BaseModel):
    messageStart: Optional[MessageStart] = None
    messageStop: Optional[MessageStop] = None
    contentBlockStart: Optional[ContentBlockStart] = None
    contentBlockDelta: Optional[ContentBlockDelta] = None
    contentBlockStop: Optional[ContentBlockStop] = None
    metadata: Optional[MetadataEvent] = None


# Main event models
class InitEvent(BaseModel):
    init_event_loop: Optional[bool] = None
    start: Optional[bool] = None
    start_event_loop: Optional[bool] = None


class EventEvent(BaseModel):
    event: EventType


class MessageEvent(BaseModel):
    message: Message


class TextGenerationEvent(BaseModel):
    data: str
    delta: Dict[str, Any]
    event_loop_metrics: EventLoopMetrics
    agent: Any = None  # We don't need to serialize the agent object
    event_loop_parent_span: Any = None
    event_loop_cycle_id: UUID
    request_state: Dict[str, Any] = {}
    event_loop_cycle_trace: Any = None
    event_loop_cycle_span: Any = None
    event_loop_parent_cycle_id: Optional[UUID] = None


class ToolEvent(BaseModel):
    delta: Dict[str, Any]
    current_tool_use: ToolUse
    event_loop_metrics: EventLoopMetrics
    agent: Any = None  # We don't need to serialize the agent object
    event_loop_parent_span: Any = None
    event_loop_cycle_id: UUID
    request_state: Dict[str, Any] = {}
    event_loop_cycle_trace: Any = None
    event_loop_cycle_span: Any = None
    event_loop_parent_cycle_id: Optional[UUID] = None


# Union type for all possible events
AgentEvent = Union[InitEvent, EventEvent, MessageEvent, TextGenerationEvent, ToolEvent]
