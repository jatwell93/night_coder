# DeepWiki Q&A with Code Context for Repository: traceloop/openllmetry
## Q1
I am investigating setting up my own agentic architecture for overnight runs while I am asleep and the agents are working. One key part of this is after the work is done, the logs and the tests are passed to a 'Judge LLM' that checks to find any gaps in implementation and find bugs, skipped processes etc. the goal is to store: The full conversation (prompts, outputs), Phase transitions and decisions, Tool invocations (e.g., test runs, git commands). I would also read these in the morning looking for missed work. Would OpenLLMetry be a good addition to this workflow? Why/Why not?
### Answer
# OpenLLMetry for Your Overnight Agentic Workflow: A Detailed Analysis

**Yes, OpenLLMetry would be a valuable addition — but with important caveats about what it covers natively vs. what requires manual instrumentation.** Here is a breakdown against each of your three storage goals.

---

## 1. ✅ Full Conversation (Prompts & Outputs)

This is OpenLLMetry's strongest area. It auto-instruments all major LLM providers (OpenAI, Anthropic, Claude, Gemini, Groq, Ollama, etc.) using monkey-patching via `wrapt`. openllmetry:1-38 

For each LLM call, it captures the full request (model, messages, temperature, max tokens) and the full response (completion, token usage, finish reason, model fingerprint) as OpenTelemetry span attributes: openllmetry:105-247 

Crucially, prompt content tracing is **on by default** via the `TRACELOOP_TRACE_CONTENT` environment variable: openllmetry:177-180 

For structured event-level logging (individual messages and choice events), the `emit_event` system emits `MessageEvent` and `ChoiceEvent` as OTEL log records: openllmetry:37-84 openllmetry:1-41 

---

## 2. ✅ Phase Transitions and Decisions

This is well-supported through the `@workflow`, `@agent`, `@task`, and `@tool` decorators. These map directly to your "phase transitions" concept: openllmetry:14-71 

Each decorated function gets a span that records:
- `TRACELOOP_SPAN_KIND` (WORKFLOW / AGENT / TASK / TOOL)
- `TRACELOOP_ENTITY_NAME`
- `TRACELOOP_ENTITY_INPUT` (JSON-serialized args)
- `TRACELOOP_ENTITY_OUTPUT` (JSON-serialized return value)
- `TRACELOOP_ENTITY_PATH` (the chained path of parent entities) openllmetry:135-196 

The semantic conventions define the full span kind taxonomy: openllmetry:285-290 

For frameworks like **CrewAI**, this is instrumented automatically at the `Crew.kickoff`, `Agent.execute_task`, and `Task.execute_sync` levels — meaning workflow phase transitions are tracked without any code changes: openllmetry:38-51 

The workflow/agent name is propagated across all child spans via context: openllmetry:246-263 

---

## 3. ⚠️ Tool Invocations (Test Runs, Git Commands)

This is the area with **the most nuance**.

### ✅ LLM-native tool calls (function calling)
OpenLLMetry captures tool call arguments and results for LLM function calling natively: openllmetry:75-103 

### ✅ MCP tool calls
The `McpInstrumentor` intercepts `tools/call` at the protocol level, recording `TRACELOOP_ENTITY_INPUT`, `TRACELOOP_ENTITY_OUTPUT`, and error states for every MCP tool invocation: openllmetry:269-306 

The `SpanAttributes` include dedicated MCP fields: openllmetry:241-245 

### ❌ Shell/git commands (not natively covered)
OpenLLMetry has **no built-in instrumentation** for `subprocess`, `git`, shell scripts, or test runners. You would need to manually wrap those using the `@tool` decorator or `track_llm_call` context manager: openllmetry:75-87 

---

## 4. ✅ Feeding Data to a Judge LLM (Morning Review)

OpenLLMetry supports a `span_postprocess_callback` hook that fires on every completed span. This is the integration point where you could programmatically pass spans to your Judge LLM: openllmetry:71-72 openllmetry:133-148 

For session-level grouping (so your Judge LLM sees a coherent "run"), you can attach metadata via `set_association_properties`: openllmetry:6-43 openllmetry:230-243 

You can also export to **any OTLP-compatible backend** (Jaeger, Grafana Tempo, Honeycomb, the Traceloop platform, or even a local file exporter), via HTTP or gRPC: openllmetry:294-333 

---

## Summary Architecture for Your Use Case

```mermaid
graph TD
    "Overnight Agent Run" --> "OpenLLMetry Auto-Instruments"
    "OpenLLMetry Auto-Instruments" --> "LLM Calls (prompts/outputs)"
    "OpenLLMetry Auto-Instruments" --> "Agent/Task/Workflow Spans"
    "OpenLLMetry Auto-Instruments" --> "MCP Tool Calls"
    "Manual @tool Decorator" --> "Git/Shell Commands"
    "LLM Calls (prompts/outputs)" --> "OTLP Backend (Jaeger / Traceloop / File)"
    "Agent/Task/Workflow Spans" --> "OTLP Backend (Jaeger / Traceloop / File)"
    "MCP Tool Calls" --> "OTLP Backend (Jaeger / Traceloop / File)"
    "Git/Shell Commands" --> "OTLP Backend (Jaeger / Traceloop / File)"
    "OTLP Backend (Jaeger / Traceloop / File)" --> "span_postprocess_callback OR batch export"
    "span_postprocess_callback OR batch export" --> "Judge LLM"
    "OTLP Backend (Jaeger / Traceloop / File)" --> "Morning Review UI"
```

---

## Notes

1. **What OpenLLMetry IS**: An OpenTelemetry-based observability layer for LLM applications. It is not a conversation logger or a replay system — it emits structured trace spans/events to any OTLP sink you configure.

2. **The biggest gap for your use case** is non-LLM tool invocations (git, pytest, bash). These require manual `@tool` decoration or custom spans. OpenLLMetry has no subprocess or shell instrumentation.

3. **Content tracing is opt-out**, not opt-in. The `TRACELOOP_TRACE_CONTENT=false` env var disables prompt/response capture — make sure it stays at its default (`true`) for your overnight runs. openllmetry:8-9 

4. **For morning review**: OpenLLMetry does not provide a built-in log viewer. You need a backend such as Jaeger, Grafana Tempo, or the hosted Traceloop platform. The spans contain timestamps, parent-child trace hierarchies, and all attributes needed to reconstruct the full overnight run.

5. **For the Judge LLM specifically**: The `span_postprocess_callback` fires per-span, not per-session. You'd likely want to collect spans into a session (using `association_properties` with a `session_id`) and batch-process them at the end of the run, rather than judging each span individually.
### Citations
**File:** packages/traceloop-sdk/traceloop/sdk/instruments.py (L1-38)
```python
from enum import Enum


class Instruments(Enum):
    AGNO = "agno"
    ALEPHALPHA = "alephalpha"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    CHROMA = "chroma"
    COHERE = "cohere"
    CREWAI = "crewai"
    CREW = "crewai"  # deprecated alias; remove in future major version
    GOOGLE_GENERATIVEAI = "google_generativeai"
    GROQ = "groq"
    HAYSTACK = "haystack"
    LANCEDB = "lancedb"
    LANGCHAIN = "langchain"
    LLAMA_INDEX = "llama_index"
    MARQO = "marqo"
    MCP = "mcp"
    MILVUS = "milvus"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    OPENAI = "openai"
    OPENAI_AGENTS = "openai_agents"
    PINECONE = "pinecone"
    PYMYSQL = "pymysql"
    QDRANT = "qdrant"
    REDIS = "redis"
    REPLICATE = "replicate"
    REQUESTS = "requests"
    SAGEMAKER = "sagemaker"
    TOGETHER = "together"
    TRANSFORMERS = "transformers"
    URLLIB3 = "urllib3"
    VERTEXAI = "vertexai"
    WATSONX = "watsonx"
    WEAVIATE = "weaviate"
```
**File:** packages/opentelemetry-instrumentation-openai/opentelemetry/instrumentation/openai/shared/__init__.py (L75-103)
```python
def _set_functions_attributes(span, functions):
    if not functions:
        return

    for i, function in enumerate(functions):
        prefix = f"{SpanAttributes.LLM_REQUEST_FUNCTIONS}.{i}"
        _set_span_attribute(span, f"{prefix}.name", function.get("name"))
        _set_span_attribute(span, f"{prefix}.description", function.get("description"))
        _set_span_attribute(
            span, f"{prefix}.parameters", json.dumps(function.get("parameters"))
        )


def set_tools_attributes(span, tools):
    if not tools:
        return

    for i, tool in enumerate(tools):
        function = tool.get("function")
        if not function:
            continue

        prefix = f"{SpanAttributes.LLM_REQUEST_FUNCTIONS}.{i}"
        _set_span_attribute(span, f"{prefix}.name", function.get("name"))
        _set_span_attribute(span, f"{prefix}.description", function.get("description"))
        _set_span_attribute(
            span, f"{prefix}.parameters", json.dumps(function.get("parameters"))
        )

```
**File:** packages/opentelemetry-instrumentation-openai/opentelemetry/instrumentation/openai/shared/__init__.py (L105-247)
```python
def _set_request_attributes(span, kwargs, instance=None):
    if not span.is_recording():
        return

    _set_api_attributes(span)

    base_url = _get_openai_base_url(instance) if instance else ""
    vendor = _get_vendor_from_url(base_url)
    _set_span_attribute(span, GenAIAttributes.GEN_AI_SYSTEM, vendor)

    model = kwargs.get("model")
    if vendor == "AWS" and model and "." in model:
        model = _cross_region_check(model)
    elif vendor == "OpenRouter":
        model = _extract_model_name_from_provider_format(model)

    _set_span_attribute(span, GenAIAttributes.GEN_AI_REQUEST_MODEL, model)
    _set_span_attribute(
        span, GenAIAttributes.GEN_AI_REQUEST_MAX_TOKENS, kwargs.get("max_tokens")
    )
    _set_span_attribute(
        span, GenAIAttributes.GEN_AI_REQUEST_TEMPERATURE, kwargs.get("temperature")
    )
    _set_span_attribute(span, GenAIAttributes.GEN_AI_REQUEST_TOP_P, kwargs.get("top_p"))
    _set_span_attribute(
        span, SpanAttributes.LLM_FREQUENCY_PENALTY, kwargs.get("frequency_penalty")
    )
    _set_span_attribute(
        span, SpanAttributes.LLM_PRESENCE_PENALTY, kwargs.get("presence_penalty")
    )
    _set_span_attribute(span, SpanAttributes.LLM_USER, kwargs.get("user"))
    _set_span_attribute(span, SpanAttributes.LLM_HEADERS, str(kwargs.get("headers")))
    # The new OpenAI SDK removed the `headers` and create new field called `extra_headers`
    if kwargs.get("extra_headers") is not None:
        _set_span_attribute(
            span, SpanAttributes.LLM_HEADERS, str(kwargs.get("extra_headers"))
        )
    _set_span_attribute(
        span, SpanAttributes.LLM_IS_STREAMING, kwargs.get("stream") or False
    )
    _set_span_attribute(
        span, OpenAIAttributes.OPENAI_REQUEST_SERVICE_TIER, kwargs.get("service_tier")
    )
    if response_format := kwargs.get("response_format"):
        # backward-compatible check for
        # openai.types.shared_params.response_format_json_schema.ResponseFormatJSONSchema
        if (
            isinstance(response_format, dict)
            and response_format.get("type") == "json_schema"
            and response_format.get("json_schema")
        ):
            schema = dict(response_format.get("json_schema")).get("schema")
            if schema:
                _set_span_attribute(
                    span,
                    SpanAttributes.LLM_REQUEST_STRUCTURED_OUTPUT_SCHEMA,
                    json.dumps(schema),
                )
        elif (
            isinstance(response_format, pydantic.BaseModel)
            or (
                hasattr(response_format, "model_json_schema")
                and callable(response_format.model_json_schema)
            )
        ):
            _set_span_attribute(
                span,
                SpanAttributes.LLM_REQUEST_STRUCTURED_OUTPUT_SCHEMA,
                json.dumps(response_format.model_json_schema()),
            )
        else:
            schema = None
            try:
                schema = json.dumps(pydantic.TypeAdapter(response_format).json_schema())
            except Exception:
                try:
                    schema = json.dumps(response_format)
                except Exception:
                    pass

            if schema:
                _set_span_attribute(
                    span,
                    SpanAttributes.LLM_REQUEST_STRUCTURED_OUTPUT_SCHEMA,
                    schema,
                )


@dont_throw
def _set_response_attributes(span, response):
    if not span.is_recording():
        return

    if "error" in response:
        _set_span_attribute(
            span,
            f"{GenAIAttributes.GEN_AI_PROMPT}.{PROMPT_ERROR}",
            json.dumps(response.get("error")),
        )
        return

    response_model = response.get("model")
    if response_model:
        response_model = _extract_model_name_from_provider_format(response_model)
    _set_span_attribute(span, GenAIAttributes.GEN_AI_RESPONSE_MODEL, response_model)
    _set_span_attribute(span, GenAIAttributes.GEN_AI_RESPONSE_ID, response.get("id"))

    _set_span_attribute(
        span,
        SpanAttributes.LLM_OPENAI_RESPONSE_SYSTEM_FINGERPRINT,
        response.get("system_fingerprint"),
    )
    _set_span_attribute(
        span,
        OpenAIAttributes.OPENAI_RESPONSE_SERVICE_TIER,
        response.get("service_tier"),
    )
    _log_prompt_filter(span, response)
    usage = response.get("usage")
    if not usage:
        return

    if is_openai_v1() and not isinstance(usage, dict):
        usage = usage.__dict__

    _set_span_attribute(
        span, SpanAttributes.LLM_USAGE_TOTAL_TOKENS, usage.get("total_tokens")
    )
    _set_span_attribute(
        span,
        GenAIAttributes.GEN_AI_USAGE_OUTPUT_TOKENS,
        usage.get("completion_tokens"),
    )
    _set_span_attribute(
        span, GenAIAttributes.GEN_AI_USAGE_INPUT_TOKENS, usage.get("prompt_tokens")
    )
    prompt_tokens_details = dict(usage.get("prompt_tokens_details", {}))
    _set_span_attribute(
        span,
        SpanAttributes.LLM_USAGE_CACHE_READ_INPUT_TOKENS,
        prompt_tokens_details.get("cached_tokens", 0),
    )
    return
```
**File:** packages/opentelemetry-instrumentation-openai/opentelemetry/instrumentation/openai/utils.py (L177-180)
```python
def should_send_prompts():
    return (
        os.getenv(TRACELOOP_TRACE_CONTENT) or "true"
    ).lower() == "true" or context_api.get_value("override_enable_content_tracing")
```
**File:** packages/opentelemetry-instrumentation-openai/opentelemetry/instrumentation/openai/shared/event_emitter.py (L37-84)
```python
def emit_event(event: Union[MessageEvent, ChoiceEvent]) -> None:
    """
    Emit an event to the OpenTelemetry SDK.

    Args:
        event: The event to emit.
    """
    if not should_emit_events():
        return

    if isinstance(event, MessageEvent):
        _emit_message_event(event)
    elif isinstance(event, ChoiceEvent):
        _emit_choice_event(event)
    else:
        raise TypeError("Unsupported event type")


def _emit_message_event(event: MessageEvent) -> None:
    body = asdict(event)

    if event.role in VALID_MESSAGE_ROLES:
        name = "gen_ai.{}.message".format(event.role)
        # According to the semantic conventions, the role is conditionally required if available
        # and not equal to the "role" in the message name. So, remove the role from the body if
        # it is the same as the in the event name.
        body.pop("role", None)
    else:
        name = "gen_ai.user.message"

    # According to the semantic conventions, only the assistant role has tool call
    if event.role != Roles.ASSISTANT.value and event.tool_calls is not None:
        del body["tool_calls"]
    elif event.tool_calls is None:
        del body["tool_calls"]

    if not should_send_prompts():
        del body["content"]
        if body.get("tool_calls") is not None:
            for tool_call in body["tool_calls"]:
                tool_call["function"].pop("arguments", None)

    log_record = LogRecord(
        body=body,
        attributes=EVENT_ATTRIBUTES,
        event_name=name
    )
    Config.event_logger.emit(log_record)
```
**File:** packages/opentelemetry-instrumentation-openai/opentelemetry/instrumentation/openai/shared/event_models.py (L1-41)
```python
from dataclasses import dataclass
from typing import Any, List, Literal, Optional, TypedDict


class _FunctionToolCall(TypedDict):
    function_name: str
    arguments: Optional[dict[str, Any]]


class ToolCall(TypedDict):
    """Represents a tool call in the AI model."""

    id: str
    function: _FunctionToolCall
    type: Literal["function"]


class CompletionMessage(TypedDict):
    """Represents a message in the AI model."""

    content: Any
    role: str = "assistant"


@dataclass
class MessageEvent:
    """Represents an input event for the AI model."""

    content: Any
    role: str = "user"
    tool_calls: Optional[List[ToolCall]] = None


@dataclass
class ChoiceEvent:
    """Represents a completion event for the AI model."""

    index: int
    message: CompletionMessage
    finish_reason: str = "unknown"
    tool_calls: Optional[List[ToolCall]] = None
```
**File:** packages/traceloop-sdk/traceloop/sdk/decorators/__init__.py (L14-71)
```python
def task(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[TraceloopSpanKindValues] = TraceloopSpanKindValues.TASK,
) -> Callable[[F], F]:
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
        )


def workflow(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
    tlp_span_kind: Optional[TraceloopSpanKindValues] = TraceloopSpanKindValues.WORKFLOW,
) -> Callable[[F], F]:
    if method_name is None:
        return entity_method(name=name, version=version, tlp_span_kind=tlp_span_kind)
    else:
        return entity_class(
            name=name,
            version=version,
            method_name=method_name,
            tlp_span_kind=tlp_span_kind,
        )


def agent(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
) -> Callable[[F], F]:
    return workflow(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.AGENT,
    )


def tool(
    name: Optional[str] = None,
    version: Optional[int] = None,
    method_name: Optional[str] = None,
) -> Callable[[F], F]:
    return task(
        name=name,
        version=version,
        method_name=method_name,
        tlp_span_kind=TraceloopSpanKindValues.TOOL,
    )
```
**File:** packages/traceloop-sdk/traceloop/sdk/decorators/base.py (L135-196)
```python
def _setup_span(entity_name, tlp_span_kind, version):
    """Sets up the OpenTelemetry span and context"""
    if tlp_span_kind in [
        TraceloopSpanKindValues.WORKFLOW,
        TraceloopSpanKindValues.AGENT,
    ]:
        set_workflow_name(entity_name)

    if tlp_span_kind == TraceloopSpanKindValues.AGENT:
        print(f"Setting agent name: {entity_name}")
        set_agent_name(entity_name)

    span_name = f"{entity_name}.{tlp_span_kind.value}"

    with get_tracer() as tracer:
        span = tracer.start_span(span_name)
        ctx = trace.set_span_in_context(span)
        ctx_token = context_api.attach(ctx)

        if tlp_span_kind in [
            TraceloopSpanKindValues.TASK,
            TraceloopSpanKindValues.TOOL,
        ]:
            entity_path = get_chained_entity_path(entity_name)
            set_entity_path(entity_path)

        span.set_attribute(SpanAttributes.TRACELOOP_SPAN_KIND, tlp_span_kind.value)
        span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_NAME, entity_name)
        if version:
            span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_VERSION, version)

    return span, ctx, ctx_token


def _handle_span_input(span, args, kwargs, cls=None):
    """Handles entity input logging in JSON for both sync and async functions"""
    try:
        if _should_send_prompts():
            json_input = json.dumps(
                {"args": args, "kwargs": kwargs}, **({"cls": cls} if cls else {})
            )
            truncated_json = _truncate_json_if_needed(json_input)
            span.set_attribute(
                SpanAttributes.TRACELOOP_ENTITY_INPUT,
                truncated_json,
            )
    except TypeError:
        pass


def _handle_span_output(span, res, cls=None):
    """Handles entity output logging in JSON for both sync and async functions"""
    try:
        if _should_send_prompts():
            json_output = json.dumps(res, **({"cls": cls} if cls else {}))
            truncated_json = _truncate_json_if_needed(json_output)
            span.set_attribute(
                SpanAttributes.TRACELOOP_ENTITY_OUTPUT,
                truncated_json,
            )
    except TypeError:
        pass
```
**File:** packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py (L241-245)
```python
    MCP_METHOD_NAME = "mcp.method.name"
    MCP_REQUEST_ARGUMENT = "mcp.request.argument"
    MCP_REQUEST_ID = "mcp.request.id"
    MCP_SESSION_INIT_OPTIONS = "mcp.session.init_options"
    MCP_RESPONSE_VALUE = "mcp.response.value"
```
**File:** packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py (L285-290)
```python
class TraceloopSpanKindValues(Enum):
    WORKFLOW = "workflow"
    TASK = "task"
    AGENT = "agent"
    TOOL = "tool"
    UNKNOWN = "unknown"
```
**File:** packages/opentelemetry-instrumentation-crewai/opentelemetry/instrumentation/crewai/instrumentation.py (L38-51)
```python
        wrap_function_wrapper("crewai.crew", "Crew.kickoff",
                              wrap_kickoff(tracer, duration_histogram, token_histogram))
        wrap_function_wrapper("crewai.agent", "Agent.execute_task",
                              wrap_agent_execute_task(tracer, duration_histogram, token_histogram))
        wrap_function_wrapper("crewai.task", "Task.execute_sync",
                              wrap_task_execute(tracer, duration_histogram, token_histogram))
        wrap_function_wrapper("crewai.llm", "LLM.call",
                              wrap_llm_call(tracer, duration_histogram, token_histogram))

    def _uninstrument(self, **kwargs):
        unwrap("crewai.crew.Crew", "kickoff")
        unwrap("crewai.agent.Agent", "execute_task")
        unwrap("crewai.task.Task", "execute_sync")
        unwrap("crewai.llm.LLM", "call")
```
**File:** packages/traceloop-sdk/traceloop/sdk/tracing/tracing.py (L133-148)
```python

                if span_postprocess_callback:
                    # Create a wrapper that calls both the custom and original methods
                    original_on_end = obj.__spans_processor.on_end

                    def wrapped_on_end(span):
                        # Call the custom on_end first
                        span_postprocess_callback(span)
                        # Then call the original to ensure normal processing
                        original_on_end(span)

                    obj.__spans_processor.on_end = wrapped_on_end

                obj.__spans_processor.on_start = obj._span_processor_on_start
                obj.__tracer_provider.add_span_processor(obj.__spans_processor)

```
**File:** packages/traceloop-sdk/traceloop/sdk/tracing/tracing.py (L230-243)
```python
def set_association_properties(properties: dict) -> None:
    attach(set_value("association_properties", properties))

    # Attach association properties to the current span, if it's a workflow or a task
    span = trace.get_current_span()
    if get_value("workflow_name") is not None or get_value("entity_name") is not None:
        _set_association_properties_attributes(span, properties)


def _set_association_properties_attributes(span, properties: dict) -> None:
    for key, value in properties.items():
        span.set_attribute(
            f"{SpanAttributes.TRACELOOP_ASSOCIATION_PROPERTIES}.{key}", value
        )
```
**File:** packages/traceloop-sdk/traceloop/sdk/tracing/tracing.py (L246-263)
```python
def set_workflow_name(workflow_name: str) -> None:
    attach(set_value("workflow_name", workflow_name))


def set_agent_name(agent_name: str) -> None:
    attach(set_value("agent_name", agent_name))


def set_entity_path(entity_path: str) -> None:
    attach(set_value("entity_path", entity_path))


def get_chained_entity_path(entity_name: str) -> str:
    parent = get_value("entity_path")
    if parent is None:
        return entity_name
    else:
        return f"{parent}.{entity_name}"
```
**File:** packages/traceloop-sdk/traceloop/sdk/tracing/tracing.py (L294-333)
```python
def init_spans_exporter(api_endpoint: str, headers: Dict[str, str]) -> SpanExporter:
    """
    Initialize a span exporter based on the endpoint URL scheme.

    Supported schemes:
        - http:// or https:// → HTTP exporter
        - grpc:// → gRPC exporter (insecure)
        - grpcs:// → gRPC exporter (secure/TLS)
        - No scheme → gRPC exporter (insecure, for backward compatibility)

    Args:
        api_endpoint: The endpoint URL (with or without scheme)
        headers: Headers to include with the exporter requests

    Returns:
        SpanExporter: Configured HTTP or gRPC exporter
    """
    parsed = urlparse(api_endpoint.strip())

    match parsed.scheme.lower():
        case "http" | "https":
            base_url = api_endpoint.strip().rstrip('/')
            if not base_url.endswith('/v1/traces'):
                endpoint = f"{base_url}/v1/traces"
            else:
                endpoint = base_url
            return HTTPExporter(endpoint=endpoint, headers=headers)
        case "grpc":
            return GRPCExporter(
                endpoint=parsed.netloc, headers=headers, insecure=True
            )
        case "grpcs":
            return GRPCExporter(
                endpoint=parsed.netloc, headers=headers, insecure=False
            )
        case _:
            # No scheme → default to insecure gRPC for backward compatibility
            return GRPCExporter(
                endpoint=api_endpoint.strip(), headers=headers, insecure=True
            )
```
**File:** packages/opentelemetry-instrumentation-mcp/opentelemetry/instrumentation/mcp/instrumentation.py (L269-306)
```python
    async def _handle_tool_call(self, tracer, method, params, args, kwargs, wrapped):
        """Handle tools/call with tool semantics"""
        # Extract the actual tool name
        entity_name = method
        span_name = f"{method}.tool"
        if params:
            try:
                if hasattr(params, "name"):
                    entity_name = params.name
                    span_name = f"{params.name}.tool"
                elif hasattr(params, "__dict__") and "name" in params.__dict__:
                    entity_name = params.__dict__["name"]
                    span_name = f"{params.__dict__['name']}.tool"
            except Exception:
                pass

        with tracer.start_as_current_span(span_name) as span:
            # Set tool-specific attributes
            span.set_attribute(
                SpanAttributes.TRACELOOP_SPAN_KIND, TraceloopSpanKindValues.TOOL.value
            )
            span.set_attribute(SpanAttributes.TRACELOOP_ENTITY_NAME, entity_name)

            # Add input
            clean_input = self._extract_clean_input(method, params)
            if clean_input:
                try:
                    span.set_attribute(
                        SpanAttributes.TRACELOOP_ENTITY_INPUT, json.dumps(clean_input)
                    )
                except (TypeError, ValueError):
                    span.set_attribute(
                        SpanAttributes.TRACELOOP_ENTITY_INPUT, str(clean_input)
                    )

            return await self._execute_and_handle_result(
                span, method, args, kwargs, wrapped, clean_output=True
            )
```
**File:** packages/traceloop-sdk/traceloop/sdk/tracing/manual.py (L75-87)
```python
@contextmanager
def track_llm_call(vendor: str, type: str):
    with get_tracer() as tracer:
        span = tracer.start_span(name=f"{vendor}.{type}")
        span.set_attribute(GenAIAttributes.GEN_AI_SYSTEM, vendor)
        span.set_attribute(SpanAttributes.LLM_REQUEST_TYPE, type)
        ctx = set_span_in_context(span)
        token = context.attach(ctx)
        try:
            yield LLMSpan(span)
        finally:
            context.detach(token)
            span.end()
```
**File:** packages/traceloop-sdk/traceloop/sdk/__init__.py (L71-72)
```python
        span_postprocess_callback: Optional[Callable[[ReadableSpan], None]] = None,
    ) -> Optional[Client]:
```
**File:** packages/traceloop-sdk/traceloop/sdk/associations/associations.py (L6-43)
```python
class AssociationProperty(str, Enum):
    """Standard association properties for tracing."""

    CUSTOMER_ID = "customer_id"
    USER_ID = "user_id"
    SESSION_ID = "session_id"


# Type alias for a single association
Association = tuple[AssociationProperty, str]


class Associations:
    """Class for managing trace associations."""

    @staticmethod
    def set(associations: Sequence[Association]) -> None:
        """
        Set associations that will be added directly to all spans in the current context.

        Args:
            associations: A sequence of (property, value) tuples

        Example:
            # Single association
            traceloop.associations.set([(AssociationProperty.SESSION_ID, "conv-123")])

            # Multiple associations
            traceloop.associations.set([
                (AssociationProperty.USER_ID, "user-456"),
                (AssociationProperty.SESSION_ID, "session-789")
            ])
        """
        # Convert associations to a dict and use set_association_properties
        properties = {prop.value: value for prop, value in associations}
        set_association_properties(properties)


```
**File:** packages/traceloop-sdk/traceloop/sdk/config/__init__.py (L8-9)
```python
def is_content_tracing_enabled() -> bool:
    return (os.getenv("TRACELOOP_TRACE_CONTENT") or "true").lower() == "true"
```

---

## Official / 2026 links

- [OpenLLMetry docs (Traceloop)](https://www.traceloop.com/docs/openllmetry) · [GitHub `traceloop/openllmetry`](https://github.com/traceloop/openllmetry)
- [Langfuse + OpenLLMetry example](https://langfuse.com/docs/opentelemetry/example-openllmetry)
- [`research_overnight_stack_web/findings_observability_langfuse_openllmetry.md`](research_overnight_stack_web/findings_observability_langfuse_openllmetry.md)
