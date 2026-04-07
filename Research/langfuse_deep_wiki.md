# DeepWiki Q&A with Code Context for Repository: langfuse/langfuse
## Q1
I am investigating setting up my own agentic architecture for overnight runs while I am asleep and the agents are working. One key part of this is after the work is done, the logs and the tests are passed to a 'Judge LLM' that checks to find any gaps in implementation and find bugs, skipped processes etc. the goal is to store: The full conversation (prompts, outputs), Phase transitions and decisions, Tool invocations (e.g., test runs, git commands). I would also read these in the morning looking for missed work. Would LangFuse be a good addition to this workflow? Why/Why not?
### Answer
# Would Langfuse Be a Good Addition to Your Overnight Agentic Workflow?

**Short answer: Yes, very well aligned.** Langfuse is purpose-built for exactly the tracing, evaluation, and review workflow you're describing. Here's a detailed breakdown of *why*, feature by feature.

---

## 1. Storing the Full Conversation (Prompts & Outputs)

Every unit of work in Langfuse is a **Trace**, which natively carries `input`, `output`, and `metadata` fields, as well as `sessionId` to group related traces together. langfuse:12-30 

Within a trace, every individual LLM call is an **Observation** of type `GENERATION`, which also stores `input`, `output`, `modelParameters`, and complete token/cost accounting (`usageDetails`, `costDetails`). langfuse:55-100 

For an **overnight run**, you would wrap the entire agent run in a single `sessionId`, and each phase or sub-task becomes its own trace within that session — the session view will then show you the complete chronological conversation in the morning.

---

## 2. Tracking Phase Transitions and Decisions

Langfuse supports a **parent-child observation hierarchy**. Each observation has a `parentObservationId`, creating a tree structure that precisely models phase transitions. langfuse:55-68 

There is even a dedicated **Agent Graph View** that can visualize the agent's execution as a graph, including LangGraph-style node/step metadata, which is ideal for reviewing decision paths in the morning. langfuse:1-46 

---

## 3. Tool Invocations (Test Runs, Git Commands)

This is one of the strongest fits. The `ObservationType` enum includes dedicated `TOOL`, `AGENT`, `CHAIN`, and `RETRIEVER` types, designed explicitly for this purpose. Each tool invocation (e.g., a `git commit` or `pytest` run) can be logged as a `TOOL` span with its own `input` (the command) and `output` (the result/stdout). langfuse:5-30 

The `toolDefinitions` and `toolCalls` fields are also stored at the observation level, giving you structured access to tool call names and results. langfuse:96-99 

---

## 4. The "Judge LLM" — Built-in LLM-as-Judge Evaluation

Langfuse has a **native LLM-as-a-judge system** built in. You define an `EvalTemplate` with a custom prompt (e.g., "Given this agent's conversation, identify any gaps in implementation"), and Langfuse's worker will automatically score traces by calling your chosen LLM. Scores (`NUMERIC`, `CATEGORICAL`, or `BOOLEAN`) are written back and associated with each trace. langfuse:114-131 

The key anti-loop safeguard you'd want to know about: evaluation traces themselves are tagged with an internal environment prefix (`langfuse-*`) so they don't trigger further evaluations, preventing infinite eval loops. langfuse:224-249 

Scores can originate from three sources — `API` (your own scripts), `EVAL` (the LLM judge), or `ANNOTATION` (your own manual morning review). langfuse:4-12 

---

## 5. Reading in the Morning

In the morning, you can:

- **Browse the UI**: Filter traces by session, time range, tags, scores, and environment
- **Manually annotate**: The `ANNOTATION` score source lets you attach your own quality scores (thumbs up/down, numeric, categorical) to any trace or span while reviewing
- **Batch Export**: Export all traces and observations for a session as JSON/CSV/JSONL for deeper offline analysis langfuse:1-40 

---

## 6. Self-Hosting for Full Data Privacy

Since you're running overnight agentic runs (likely involving proprietary code and work), self-hosting is important. Langfuse supports full self-hosting via Docker Compose with Postgres, ClickHouse, Redis, and MinIO — all the infrastructure you need.

The entire ingestion pipeline accepts **OpenTelemetry (OTEL)** spans natively, meaning any OTEL-instrumented agent framework will work out of the box without Langfuse-specific SDK wrapping.

---

## Caveats / Things to Be Aware Of

1. **Automation triggers are limited today.** The current `TriggerEventSource` in the Automations system only supports `"prompt"` as an event source. This means you cannot yet auto-trigger a webhook *to your own systems* when a trace is ingested — though you can trigger evals automatically. langfuse:5-13 

2. **The Judge LLM is trace-scoped, not a free-form agent.** The built-in evaluator runs LLM-as-judge *on* individual traces, not as a separate agent that reads all logs holistically. For a "Judge that reads everything at once," you'd use the **Batch Export** to pull all traces from the session and pass them to your Judge LLM separately (via the public API), then write scores back via the API.

3. **Prompt Management is a bonus.** If your overnight agents use Langfuse's **Prompt Management** (versioned, immutable prompt templates with `production`/`staging` labels), you get traceability from a specific prompt version all the way to the trace it produced — invaluable for debugging why an agent took a wrong decision path. langfuse:77-79 

---

## Summary Diagram

```mermaid
graph TD
    "Overnight Agent Run" --> "Langfuse Session (sessionId)"
    "Langfuse Session (sessionId)" --> "Trace: Phase 1 (Planner)"
    "Langfuse Session (sessionId)" --> "Trace: Phase 2 (Coder)"
    "Langfuse Session (sessionId)" --> "Trace: Phase 3 (Tester)"

    "Trace: Phase 2 (Coder)" --> "GENERATION: LLM Call (input/output)"
    "Trace: Phase 2 (Coder)" --> "TOOL: git commit (command/result)"
    "Trace: Phase 2 (Coder)" --> "TOOL: pytest run (command/stdout)"

    "Trace: Phase 3 (Tester)" --> "EVAL Score: LLM Judge (gaps/bugs)"
    "EVAL Score: LLM Judge (gaps/bugs)" --> "Morning Review: UI + Annotation"
    "Morning Review: UI + Annotation" --> "Batch Export for deeper analysis"
```

---

## Notes

- Langfuse is **open-source (MIT)** and fully self-hostable — your overnight runs and code stay private.
- The SDKs (Python, JS/TS) and OTEL support means you do not need to redesign your agent architecture to integrate — you wrap existing code in traces and spans.
- The **observation type hierarchy** (`AGENT` > `CHAIN` > `TOOL` > `GENERATION`) is semantically designed for exactly the kind of agentic workflow you described.
- The built-in **Judge LLM evaluator** with customizable prompt templates is a strong native alternative to building your own — but for a holistic "read all the logs" judge, combining batch export + your own Judge LLM + score API write-back is the recommended pattern.
### Citations
**File:** packages/shared/src/domain/traces.ts (L12-30)
```typescript
export const TraceDomain = z.object({
  id: z.string(),
  name: z.string().nullable(),
  timestamp: z.date(),
  environment: z.string(),
  tags: z.array(z.string()),
  bookmarked: z.boolean(),
  public: z.boolean(),
  release: z.string().nullable(),
  version: z.string().nullable(),
  input: jsonSchema.nullable(),
  output: jsonSchema.nullable(),
  metadata: MetadataDomain,
  createdAt: z.date(),
  updatedAt: z.date(),
  sessionId: z.string().nullable(),
  userId: z.string().nullable(),
  projectId: z.string(),
});
```
**File:** packages/shared/src/domain/observations.ts (L5-30)
```typescript
export const ObservationType = {
  SPAN: "SPAN",
  EVENT: "EVENT",
  GENERATION: "GENERATION",
  AGENT: "AGENT",
  TOOL: "TOOL",
  CHAIN: "CHAIN",
  RETRIEVER: "RETRIEVER",
  EVALUATOR: "EVALUATOR",
  EMBEDDING: "EMBEDDING",
  GUARDRAIL: "GUARDRAIL",
} as const;

export const ObservationTypeDomain = z.enum([
  "SPAN",
  "EVENT",
  "GENERATION",
  "AGENT",
  "TOOL",
  "CHAIN",
  "RETRIEVER",
  "EVALUATOR",
  "EMBEDDING",
  "GUARDRAIL",
]);
export type ObservationType = z.infer<typeof ObservationTypeDomain>;
```
**File:** packages/shared/src/domain/observations.ts (L55-100)
```typescript
export const ObservationSchema = z.object({
  id: z.string(),
  traceId: z.string().nullable(),
  projectId: z.string(),
  environment: z.string(),
  type: ObservationTypeDomain,
  startTime: z.date(),
  endTime: z.date().nullable(),
  name: z.string().nullable(),
  metadata: MetadataDomain,
  parentObservationId: z.string().nullable(),
  level: ObservationLevelDomain,
  statusMessage: z.string().nullable(),
  version: z.string().nullable(),
  createdAt: z.date(),
  updatedAt: z.date(),
  model: z.string().nullable(),
  internalModelId: z.string().nullable(),
  modelParameters: jsonSchema.nullable(),
  input: jsonSchema.nullable(),
  output: jsonSchema.nullable(),
  completionStartTime: z.date().nullable(),
  promptId: z.string().nullable(),
  promptName: z.string().nullable(),
  promptVersion: z.number().nullable(),
  latency: z.number().nullable(),
  timeToFirstToken: z.number().nullable(),
  usageDetails: z.record(z.string(), z.number()),
  costDetails: z.record(z.string(), z.number()),
  providedCostDetails: z.record(z.string(), z.number()),
  // aggregated data from cost_details
  inputCost: z.number().nullable(),
  outputCost: z.number().nullable(),
  totalCost: z.number().nullable(),
  // aggregated data from usage_details
  inputUsage: z.number(),
  outputUsage: z.number(),
  totalUsage: z.number(),
  // pricing tier information
  usagePricingTierId: z.string().nullable(),
  usagePricingTierName: z.string().nullable(),
  // tool data
  toolDefinitions: z.record(z.string(), z.string()).nullable(),
  toolCalls: z.array(z.string()).nullable(),
  toolCallNames: z.array(z.string()).nullable(),
});
```
**File:** web/src/features/trace-graph-view/types.ts (L1-46)
```typescript
import { z } from "zod/v4";

export type GraphNodeData = {
  id: string;
  label: string;
  type: string;
};

export type GraphCanvasData = {
  nodes: GraphNodeData[];
  edges: { from: string; to: string }[];
};

export const LANGGRAPH_NODE_TAG = "langgraph_node";
export const LANGGRAPH_STEP_TAG = "langgraph_step";
export const LANGGRAPH_START_NODE_NAME = "__start__";
export const LANGGRAPH_END_NODE_NAME = "__end__";
export const LANGFUSE_START_NODE_NAME = "__start__";
export const LANGFUSE_END_NODE_NAME = "__end__";

export const LanggraphMetadataSchema = z.object({
  [LANGGRAPH_NODE_TAG]: z.string(),
  [LANGGRAPH_STEP_TAG]: z.number(),
});

export const AgentGraphDataSchema = z.object({
  id: z.string(),
  parent_observation_id: z.string().nullish(),
  type: z.string(),
  name: z.string(),
  start_time: z.string(),
  end_time: z.string().nullish(),
  node: z.string().nullish(),
  step: z.coerce.number().nullish(),
});

export type AgentGraphDataResponse = {
  id: string;
  node: string | null; // langgraph_node
  step: number | null;
  parentObservationId: string | null;
  name: string; // span name
  startTime: string;
  endTime?: string;
  observationType: string;
};
```
**File:** web/src/features/evals/server/router.ts (L114-131)
```typescript
export const CreateEvalTemplate = z.object({
  name: z.string().min(1),
  projectId: z.string(),
  prompt: z.string(),
  provider: z.string().nullish(),
  model: z.string().nullish(),
  modelParams: ZodModelConfig.nullish(),
  vars: z.array(z.string()),
  outputSchema: z.object({
    score: z.string(),
    reasoning: z.string(),
  }),
  cloneSourceId: z.string().optional(),
  referencedEvaluators: z
    .enum(EvalReferencedEvaluators)
    .optional()
    .default(EvalReferencedEvaluators.PERSIST),
});
```
**File:** worker/src/features/evaluation/evalService.ts (L224-249)
```typescript
  //
  // CONTEXT: Prevent infinite eval loops
  // Without this safeguard: user trace → eval → eval trace → another eval → infinite loop
  //
  // IMPLEMENTATION:
  // - Block ALL traces with environment starting with "langfuse-" when coming from trace-upsert queue
  // - This excludes traces from prompt experiments that come via dataset-run-item-upsert queue
  // - Internal traces (e.g., eval executions) use LangfuseInternalTraceEnvironment enum values
  //
  // DUAL SAFEGUARD:
  // - This check prevents eval job CREATION for internal traces
  // - fetchLLMCompletion.ts enforces that internal traces MUST use "langfuse-" prefix
  //
  // See: packages/shared/src/server/llm/fetchLLMCompletion.ts (enforcement)
  // See: packages/shared/src/server/llm/types.ts (LangfuseInternalTraceEnvironment enum)
  if (
    sourceEventType === "trace-upsert" &&
    event.traceEnvironment?.startsWith("langfuse")
  ) {
    logger.debug("Skipping eval job creation for internal Langfuse trace", {
      traceId: event.traceId,
      environment: event.traceEnvironment,
    });

    return;
  }
```
**File:** packages/shared/src/domain/scores.ts (L4-12)
```typescript
export const ScoreSourceArray = ["API", "EVAL", "ANNOTATION"] as const;
export const ScoreSourceEnum = {
  API: "API",
  EVAL: "EVAL",
  ANNOTATION: "ANNOTATION",
} as const;
export const ScoreSourceDomain = z.enum(ScoreSourceArray);
export type ScoreSourceType = z.infer<typeof ScoreSourceDomain>;

```
**File:** packages/shared/src/features/batchExport/types.ts (L1-40)
```typescript
import z from "zod/v4";

import { BatchExport } from "@prisma/client";

import { singleFilter } from "../../interfaces/filters";
import { orderBy } from "../../interfaces/orderBy";
import { BatchTableNames } from "../../interfaces/tableNames";
import { TracingSearchType } from "../../interfaces/search";

export enum BatchExportStatus {
  QUEUED = "QUEUED",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
  CANCELLED = "CANCELLED",
}

export enum BatchExportFileFormat {
  JSON = "JSON",
  CSV = "CSV",
  JSONL = "JSONL",
}

// Use shared BatchTableNames enum for consistency across batch operations
// Keep BatchExportTableName as alias for backward compatibility
export { BatchTableNames as BatchExportTableName };

export const exportOptions: Record<
  BatchExportFileFormat,
  {
    label: string;
    extension: string;
    fileType: string;
  }
> = {
  CSV: { label: "CSV", extension: "csv", fileType: "text/csv; charset=utf-8" },
  JSON: {
    label: "JSON",
    extension: "json",
    fileType: "application/json; charset=utf-8",
```
**File:** packages/shared/src/domain/automations.ts (L5-13)
```typescript
export enum TriggerEventSource {
  Prompt = "prompt",
}

export const EventActionSchema = z.enum(["created", "updated", "deleted"]);

export type TriggerEventAction = z.infer<typeof EventActionSchema>;

export const TriggerEventSourceSchema = z.enum([TriggerEventSource.Prompt]);
```

---

## Official / 2026 links

- [Data model](https://langfuse.com/docs/observability/data-model) · [Sessions](https://langfuse.com/docs/tracing/sessions)
- [LLM-as-a-judge / scores](https://langfuse.com/docs/scores/model-based-evals) · [OpenTelemetry ingest](https://langfuse.com/docs/opentelemetry)
- [Self-host](https://langfuse.com/docs/deployment/self-host)
- [`research_overnight_stack_web/findings_observability_langfuse_openllmetry.md`](research_overnight_stack_web/findings_observability_langfuse_openllmetry.md)
