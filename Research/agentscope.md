#llm-judge 
# AgentScope's Evaluation Framework and Judge Function System

AgentScope provides **two distinct evaluation systems** that serve different purposes in agent development and assessment.

## 1. Tuner Module Judge Function System

The tuner module implements a **judge function system for reinforcement learning-based agent training**. Judge functions follow a specific type signature that takes a task dictionary, the agent's response, and optional auxiliary models (which can include LLMs for evaluation purposes), then returns a reward signal. [1](#1-0) 

The `JudgeOutput` contains a `reward` field (float) and optional `metrics` dictionary for additional performance measurements. Judge functions can leverage existing `MetricBase` implementations to compute sophisticated composite rewards. [2](#1-1) 

### Workflow Integration

Judge functions work in tandem with workflow functions, which encapsulate the agent logic being tuned. Workflow functions return a `WorkflowOutput` containing the agent's response (or direct reward), which is then evaluated by the judge function. [3](#1-2) 

The tuning process uses these components together, with the workflow function generating agent responses and the judge function providing reward signals for RL optimization: [4](#1-3) 

## 2. Benchmark Evaluation Framework

The evaluation framework provides **systematic agent evaluation across task datasets** using metrics. Tasks contain input, ground truth, and a list of metrics to evaluate solutions against. [5](#1-4) 

### Execution Trace Evaluation

Solutions are captured as `SolutionOutput` objects containing:
- `success`: Whether execution completed successfully
- `output`: The final result
- `trajectory`: A list of tool calls and results (execution trace)
- `meta`: Additional metadata [6](#1-5) 

Metrics evaluate these solutions by implementing the `MetricBase` abstract class. For example, the ACE benchmark includes metrics that analyze execution trajectories: [7](#1-6) 

The `ACEProcessAccuracy` metric specifically evaluates execution traces by checking if required milestone function calls appear in the trajectory, demonstrating how the framework analyzes code execution sequences.

### Distributed Evaluation with Ray

The `RayEvaluator` orchestrates distributed evaluation workflows, running solutions multiple times and collecting execution traces via OpenTelemetry: [8](#1-7) 

During evaluation, tracing is explicitly enabled and execution traces are captured with task and repeat IDs in the baggage context. The framework collects statistics about LLM calls, token usage, and other metrics. [9](#1-8) 

## 3. Iterative Refinement Workflows

### Evaluation Framework Approach

The evaluation framework supports iterative refinement through:
- **Result caching**: Solutions and evaluations are stored and checked before re-running
- **n_repeat parameter**: Tasks can be evaluated multiple times
- **Incremental execution**: Only missing results are computed [10](#1-9) 

This enables resumable evaluation workflows where the system can iteratively refine and re-evaluate without redundant computation.

### Tuner Module Approach

The tuner module implements iterative refinement through RL training loops with configurable evaluation intervals and checkpoint saving: [11](#1-10) 

## 4. Capabilities of LLM Judge Components

### For Tuner Judge Functions:
1. **LLM-as-a-Judge**: Auxiliary models parameter enables using LLMs to evaluate agent outputs
2. **Flexible reward computation**: Judge functions can implement any reward logic, from simple string matching to complex LLM-based evaluation
3. **Composite metrics**: Multiple metrics can be combined into a single reward signal
4. **Support for multi-agent scenarios**: Auxiliary models can simulate other agents [12](#1-11) 

### For Evaluation Metrics:
1. **Trajectory analysis**: Metrics can inspect the full sequence of tool calls and results
2. **State verification**: Metrics can compare final states against ground truth
3. **Process accuracy**: Metrics can verify intermediate execution steps
4. **Custom evaluation logic**: Any async function implementing MetricBase [13](#1-12) 

### Execution Trace Capture:

The framework uses OpenTelemetry to capture comprehensive execution traces including:
- LLM calls with all parameters (temperature, top_p, tokens, etc.)
- Agent invocations with input/output messages
- Tool executions with arguments and results
- Token usage and response metadata [14](#1-13) 

## 5. Limitations

### Judge Function System Limitations:

1. **Manual implementation required**: Judge functions must be manually written; there's no built-in LLM judge implementation
2. **Simple example only**: The tutorial only shows basic string matching, not sophisticated LLM-based evaluation
3. **Trinity-RFT dependency**: Requires external Trinity-RFT library for actual training [15](#1-14) 

### Evaluation Framework Limitations:

1. **Ray dependency**: Distributed evaluation requires Ray installation
2. **Metric implementation burden**: Custom metrics must be implemented for each evaluation need
3. **No built-in LLM judge metrics**: The ACE benchmark metrics shown use rule-based checking, not LLM evaluation
4. **Storage format**: File-based storage may not scale for very large evaluations [16](#1-15) 

### Trace Analysis Limitations:

1. **No direct code execution result scoring**: The framework captures execution traces but doesn't provide built-in scoring of code correctness or runtime behavior
2. **Manual metric creation**: Analyzing code execution results requires writing custom metrics
3. **Limited to tool calls**: Trajectory only captures tool use blocks, not arbitrary code execution [6](#1-5) 

## Notes

The key distinction is that **AgentScope provides the infrastructure for evaluation and judging, but not pre-built LLM judge implementations**. Users must:
- Write their own judge functions for RL training
- Implement custom metrics for benchmark evaluation
- Optionally use auxiliary LLM models within these custom implementations

The framework excels at capturing execution traces and orchestrating distributed evaluation, but scoring logic and LLM-based judging must be implemented by the user based on their specific needs.

### Citations

**File:** src/agentscope/tuner/_judge.py (L8-40)
```python
class JudgeOutput(BaseModel):
    """The output of a judge function."""

    reward: float = Field(
        description="The reward value assigned by the judge function.",
    )

    metrics: Dict[str, float] | None = Field(
        description="Metrics from the judge function.",
        default=None,
    )


JudgeType = Callable[
    [Dict, Any, Dict[str, ChatModelBase]],
    Awaitable[JudgeOutput],
]
# A judge function type for tuning.

# Args:
#     task (`Dict`):
#         The task information for the corresponding workflow.
#     response (`Any`):
#         The response field of the WorkflowOutput generated by the
#         corresponding workflow.
#     auxiliary_models (`Dict[str, ChatModelBase] | None`):
#         A dictionary of additional chat models available for LLM-as-a-Judge
#         usage. The keys are model names, and the values are the corresponding
#         `ChatModelBase` instances.
# Returns:
#     `JudgeOutput`:
#         The reward value assigned by the judge function along with optional
#         metrics.
```

**File:** docs/tutorial/en/src/task_tuner.py (L144-186)
```python
# Judge Function
# --------------------
# The judge function evaluates the agent's performance on a given task and provides a reward signal for tuning.
# All judge functions should follow the input/output signature defined in ``agentscope.tuner.JudgeType``.
# Below is a simple judge function that compares the agent's response with the ground truth answer:

from typing import Any
from agentscope.tuner import JudgeOutput


async def example_judge_function(
    task: Dict,
    response: Any,
    auxiliary_models: Optional[Dict[str, ChatModelBase]] = None,
) -> JudgeOutput:
    """A very simple judge function only for demonstration.

    Args:
        task (`Dict`): The task information.
        response (`Any`): The response field from the WorkflowOutput.
        auxiliary_models (`Optional[Dict[str, ChatModelBase]]`): Additional
            chat models for LLM-as-a-Judge purpose.
    Returns:
        `JudgeOutput`: The reward assigned by the judge.
    """
    ground_truth = task["answer"]
    reward = 1.0 if ground_truth in response.get_text_content() else 0.0
    return JudgeOutput(reward=reward)


judge_output = asyncio.run(
    example_judge_function(
        task,
        workflow_output.response,
    ),
)
print(f"Judge reward: {judge_output.reward}")

# %%
# The judge function can also be locally tested in the same way as shown above before formal training to ensure its logic is correct.
#
# .. tip::
#    You can leverage existing `MetricBase <https://github.com/agentscope-ai/agentscope/blob/main/src/agentscope/evaluate/_metric_base.py>`_ implementations in your judge function to compute more sophisticated metrics and combine them into a composite reward.
```

**File:** docs/tutorial/en/src/task_tuner.py (L188-234)
```python
# Configuration and Running
# ~~~~~~~~~~~~~~~
# Finally, you can configure and run the tuning process using the ``tuner`` module.
# Before starting, ensure that `Trinity-RFT <https://github.com/agentscope-ai/Trinity-RFT>`_ is installed in your environment, as it is required for tuning.
#
# Below is an example of configuring and starting the tuning process:
#
# .. note::
#    This example is for demonstration only. For a complete runnable example, see `Tune ReActAgent <https://github.com/agentscope-ai/agentscope/tree/main/examples/tuner/react_agent>`_
#
# .. code-block:: python
#
#        from agentscope.tuner import tune, AlgorithmConfig, DatasetConfig, TunerModelConfig
#        # your workflow / judge function here...
#
#        if __name__ == "__main__":
#            dataset = DatasetConfig(path="my_dataset", split="train")
#            model = TunerModelConfig(model_path="Qwen/Qwen3-0.6B", max_model_len=16384)
#            algorithm = AlgorithmConfig(
#                algorithm_type="multi_step_grpo",
#                group_size=8,
#                batch_size=32,
#                learning_rate=1e-6,
#            )
#            tune(
#                workflow_func=example_workflow_function,
#                judge_func=example_judge_function,
#                model=model,
#                train_dataset=dataset,
#                algorithm=algorithm,
#            )
#
# Here, ``DatasetConfig`` configures the training dataset, ``TunerModelConfig`` sets the parameters for the trainable model, and ``AlgorithmConfig`` specifies the reinforcement learning algorithm and its hyperparameters.
#
# .. tip::
#    The ``tune`` function is based on `Trinity-RFT <https://github.com/agentscope-ai/Trinity-RFT>`_ and internally converts input parameters to a YAML configuration.
#    Advanced users can skip the ``model``, ``train_dataset``, and ``algorithm`` arguments and instead provide a YAML config file path via the ``config_path`` argument.
#    Using a configuration file is recommended for fine-grained control and to leverage advanced Trinity-RFT features. See the Trinity-RFT `Configuration Guide <https://agentscope-ai.github.io/Trinity-RFT/en/main/tutorial/trinity_configs.html>`_ for more options.
#
# Save the above code as ``main.py`` and run it with:
#
# .. code-block:: bash
#
#        ray start --head
#        python main.py
#
# Checkpoints and logs are automatically saved to the ``checkpoints/AgentScope`` directory under your workspace, with each run in a timestamped sub-directory. Tensorboard logs can be found in ``monitor/tensorboard`` within the checkpoint directory.
```

**File:** src/agentscope/tuner/_workflow.py (L8-53)
```python
class WorkflowOutput(BaseModel):
    """The output of a workflow function."""

    reward: float | None = Field(
        description=(
            "The reward obtained from the workflow function. "
            "Used for direct reward output."
        ),
        default=None,
    )
    response: Any | None = Field(
        description=(
            "The response generated by the workflow function. "
            "Used as judge input."
        ),
        default=None,
    )

    metrics: Dict[str, float] | None = Field(
        description="Metrics from the workflow function.",
        default=None,
    )


WorkflowType = Callable[
    [Dict, ChatModelBase, Dict[str, ChatModelBase]],
    Awaitable[WorkflowOutput],
]
# An agent workflow function type for tuning.

# Args:
#     task (`Dict`):
#         The task information for the workflow run.
#     model (`ChatModelBase`):
#         The primary chat model used in the workflow, this is the main model
#         being tuned.
#     auxiliary_models (`Dict[str, ChatModelBase] | None`):
#         A dictionary of additional chat models available for LLM-as-a-Judge
#         usage. The keys are model names, and the values are the corresponding
#         `ChatModelBase` instances. Note that these auxiliary models are not
#         tuned during the workflow.

# Returns:
#     `WorkflowOutput`:
#         The workflow execution results, including optional reward, raw
#         response and metrics.
```

**File:** src/agentscope/tuner/_tune.py (L16-73)
```python
def tune(
    *,
    workflow_func: WorkflowType,
    judge_func: JudgeType | None = None,
    train_dataset: DatasetConfig | None = None,
    eval_dataset: DatasetConfig | None = None,
    model: TunerModelConfig | None = None,
    auxiliary_models: dict[str, TunerModelConfig] | None = None,
    algorithm: AlgorithmConfig | None = None,
    project_name: str | None = None,
    experiment_name: str | None = None,
    monitor_type: str | None = None,
    config_path: str | None = None,
) -> None:
    """Train the agent workflow with the specific configuration.

    Args:
        workflow_func (`WorkflowType`): The learning workflow function
            to execute.
        judge_func (`JudgeType`, optional): The judge function used to
            evaluate the workflow output. Defaults to None.
        train_dataset (`DatasetConfig`, optional): The training dataset for
            the learning process. Defaults to None.
        eval_dataset (`DatasetConfig`, optional): The evaluation dataset for
            the learning process. Defaults to None.
        model (`TunerModelConfig`, optional): The model to be tuned.
            Defaults to None.
        auxiliary_models (`dict[str, TunerModelConfig]`, optional): A
            dictionary of auxiliary models for LLM-as-a-Judge
            or acting other agents in multi-agent scenarios.
            Defaults to None.
        algorithm (`AlgorithmConfig`, optional): The tuning algorithm
            configuration. Defaults to None.
        project_name (`str`, optional): Name of the project.
            Defaults to None.
        experiment_name (`str`, optional): Name of the experiment.
            Leave None to use timestamp. Defaults to None.
        monitor_type (`str`, optional): Type of the monitor to use.
            Could be one of 'tensorboard', 'wandb', 'mlflow', 'swanlab'.
            Leave None to use tensorboard. Defaults to None.
        config_path (`str`, optional): Path to a trinity yaml configuration
            file. If provided, only `workflow_func` is necessary, other
            arguments will override the corresponding fields in the config.
            Defaults to None.
    """
    try:
        from trinity.cli.launcher import run_stage
        from trinity.utils.dlc_utils import setup_ray_cluster, stop_ray_cluster
    except ImportError as e:
        raise ImportError(
            "Trinity-RFT is not installed. Please install it with "
            "`pip install trinity-rft`.",
        ) from e

    check_workflow_function(workflow_func)
    if judge_func is not None:
        check_judge_function(judge_func)

```

**File:** src/agentscope/evaluate/_task.py (L11-53)
```python
@dataclass
class Task:
    """The base class for task in evaluation."""

    id: str
    """The unique identifier for the task."""

    input: JSONSerializableObject
    """The task input, which should be a JSON serializable object."""

    ground_truth: JSONSerializableObject
    """The task ground truth if exists, which should be a JSON serializable
    object."""

    metrics: list[MetricBase]
    """The metrics to evaluate the task, which should be a list of
    `MetricBase` objects."""

    tags: dict[str, str] | None = field(default_factory=lambda: None)
    """Tags to categorize the task, e.g. `{"difficulty": "easy",
    "cate": "math"}`."""

    metadata: dict[str, Any] | None = field(
        default_factory=lambda: None,
    )
    """Additional metadata for the task."""

    async def evaluate(self, solution: SolutionOutput) -> list[MetricResult]:
        """Evaluate the task with the given solution.

        Args:
            solution (`SolutionOutput`):
                The solution to evaluate the task with.

        Returns:
            `MetricResult`:
                The result of the evaluation.
        """
        evaluations = []
        for metric in self.metrics:
            result = await metric(solution)
            evaluations.append(result)
        return evaluations
```

**File:** src/agentscope/evaluate/_solution.py (L16-28)
```python
@dataclass
class SolutionOutput(DictMixin):
    """The output of a solution in evaluation task"""

    success: bool
    """Indicates whether the solution is executed successfully. When the
    solution raise exception, this should be set to False."""
    output: JSONSerializableObject
    """The final output of the solution."""
    trajectory: list[ToolUseBlock | ToolResultBlock | TextBlock]
    """The tool calls and results trajectory"""
    meta: dict[str, Any] | None = field(default_factory=lambda: None)
    """Additional metadata for the solution"""
```

**File:** src/agentscope/evaluate/_ace_benchmark/_ace_metric.py (L8-67)
```python
class ACEProcessAccuracy(MetricBase):
    """The ace benchmark process accuracy metric."""

    def __init__(
        self,
        mile_stone: list[str],
    ) -> None:
        """Initialize the AceBench process accuracy metric."""
        super().__init__(
            name="process_accuracy",
            metric_type=MetricType.NUMERICAL,
            description="The AceBench Agent eval process accuracy metric.",
        )
        self.mile_stone = mile_stone

    async def __call__(
        self,
        solution: SolutionOutput,
    ) -> MetricResult:
        """Calculate the metric result."""

        # Turn the tool use block sequence into ACEBench format
        # e.g. func(arg1='dfd', arg2=44)
        gathered_trajectory = []
        for tool_call in solution.trajectory:
            if tool_call.get("type") == "tool_use":
                function_name = tool_call.get("name")
                kwargs = tool_call.get("input")

                gathered_kwargs = []
                for key, value in kwargs.items():
                    if isinstance(value, str):
                        gathered_kwargs.append(
                            f"{key}='{value}'",
                        )

                    else:
                        gathered_kwargs.append(
                            f"{key}={value}",
                        )

                kwargs_str = ", ".join(gathered_kwargs)
                gathered_trajectory.append(
                    f"[{function_name}({kwargs_str})]",
                )

        for stone in self.mile_stone:
            if stone not in gathered_trajectory:
                return MetricResult(
                    name=self.name,
                    result=0,
                    message=f"Error: Missing milestone '{stone}' in "
                    "the given trajectory.",
                )

        return MetricResult(
            name=self.name,
            result=1,
            message="Success",
        )
```

**File:** src/agentscope/evaluate/_evaluator/_ray_evaluator.py (L14-22)
```python
def _check_ray_available() -> None:
    """Check if ray is available and raise ImportError if not."""
    try:
        import ray  # noqa  # pylint: disable=unused-import
    except ImportError as e:
        raise ImportError(
            "Ray is not installed. Please install it with `pip install ray` "
            "to use the RayEvaluator.",
        ) from e
```

**File:** src/agentscope/evaluate/_evaluator/_ray_evaluator.py (L38-67)
```python
@_ray_remote_decorator
class RayEvaluationActor:
    """
    Actor class for running evaluation with ray remote.
    """

    @staticmethod
    async def run(
        storage: EvaluatorStorageBase,
        task: Task,
        repeat_id: str,
        solution_output: SolutionOutput,
    ) -> None:
        """
        Run the evaluation for a task and solution result.

        Args:
            storage (EvaluatorStorageBase): Evaluator storage.
            task (Task): Task to be evaluated.
            repeat_id (str): Repeat ID
            solution_output (SolutionOutput): output data after execute agents.
        """
        evaluation_results = await task.evaluate(solution_output)
        # store the evaluation result
        for result in evaluation_results:
            storage.save_evaluation_result(
                task_id=task.id,
                repeat_id=repeat_id,
                evaluation=result,
            )
```

**File:** src/agentscope/evaluate/_evaluator/_ray_evaluator.py (L96-168)
```python
    async def run(
        self,
        storage: EvaluatorStorageBase,
        repeat_id: str,
        task: Task,
        solution: Callable[
            [Task, Callable],
            Coroutine[Any, Any, SolutionOutput],
        ],
    ) -> None:
        """Generate a solution to a task and evaluate.

        Args:
            storage (EvaluatorStorageBase): Evaluator storage.
            repeat_id (str): Repeat ID.
            task (Task): Task to be evaluated.
            solution
                (Callable[[Task, Callable], Awaitable[SolutionOutput, Any]]):
                callable function to execute agents and generate results.
        """
        if storage.solution_result_exists(task.id, repeat_id):
            # Obtain from storage
            solution_result = storage.get_solution_result(
                task.id,
                repeat_id,
            )

        else:
            from opentelemetry import trace, baggage
            from opentelemetry.context import attach, detach

            tracer = trace.get_tracer(__name__)

            # Set baggage items
            ctx = baggage.set_baggage("task_id", task.id)
            ctx = baggage.set_baggage("repeat_id", repeat_id, context=ctx)

            # Attach the context with baggage
            token = attach(ctx)

            try:
                with tracer.start_as_current_span(
                    name=f"Solution_{task.id}_{repeat_id}",
                ):
                    from ... import _config

                    _config.trace_enabled = True

                    # Run the solution
                    solution_result = await solution(
                        task,
                        storage.get_agent_pre_print_hook(
                            task.id,
                            repeat_id,
                        ),
                    )
            finally:
                detach(token)
                # Ensure all spans are flushed
                trace.get_tracer_provider().force_flush()

            storage.save_solution_stats(
                task.id,
                repeat_id,
                self.exporter.cnt.get(task.id, {}).get(repeat_id, {}),
            )

            storage.save_solution_result(
                task.id,
                repeat_id,
                solution_result,
            )

```

**File:** src/agentscope/evaluate/_evaluator_storage/_file_evaluator_storage.py (L206-256)
```python
    def solution_result_exists(self, task_id: str, repeat_id: str) -> bool:
        """Check if the solution for the given task and repeat is finished.

        Args:
            task_id (`str`):
                The task ID.
            repeat_id (`str`):
                The repeat ID for the task, usually the index of the repeat
                evaluation.

        Returns:
            `bool`:
                True if the solution result file exists, False otherwise.
        """
        path_file = self._get_save_path(
            task_id,
            repeat_id,
            self.SOLUTION_FILE_NAME,
        )

        return os.path.exists(path_file) and os.path.getsize(path_file) > 0

    def evaluation_result_exists(
        self,
        task_id: str,
        repeat_id: str,
        metric_name: str,
    ) -> bool:
        """Check if the evaluation result for the given solution and metric
        is finished.

        Args:
            task_id (`str`):
                The task ID.
            repeat_id (`str`):
                The repeat ID for the task, usually the index of the repeat
                evaluation.
            metric_name (`str`):
                The name of the metric.

        Returns:
            `bool`:
                True if the evaluation result file exists, False otherwise.
        """
        path_file = self._get_save_path(
            task_id,
            repeat_id,
            self.EVALUATION_DIR_NAME,
            f"{metric_name}.json",
        )
        return os.path.exists(path_file) and os.path.getsize(path_file) > 0
```

**File:** src/agentscope/evaluate/_metric_base.py (L46-101)
```python
@dataclass
class MetricBase(ABC):
    """The base class for _metric in evaluation."""

    name: str
    """The name of the Metric"""

    metric_type: MetricType
    """The metric type"""

    description: str | None
    """The description of the metric"""

    categories: list[str] | None
    """The candidate categories. If `metric_type` is "category", the
    categories must be provided, otherwise it should be `None`."""

    def __init__(
        self,
        name: str,
        metric_type: MetricType,
        description: str | None = None,
        categories: list[str] | None = None,
    ) -> None:
        """Initialize the _metric object.

        Args:
            name (`str`):
                The name of the metric.
            metric_type (`MetricType`):
                The type of the metric, can be either "category" or
                "numerical", which will determine how to display the result.
            description (`str`):
                The description of the metric.
            categories (`list[str] | None`, optional):
                The candidate categories. If `metric_type` is "category", the
                categories must be provided, otherwise it should be `None`.
        """
        self.name = name
        self.metric_type = metric_type
        self.description = description

        if metric_type == MetricType.CATEGORY and categories is None:
            raise ValueError(
                "Categories must be provided for category metrics.",
            )

        self.categories = categories

    @abstractmethod
    async def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> MetricResult:
        """The call function to calculate the _metric result"""
```

**File:** src/agentscope/tracing/_extractor.py (L198-267)
```python
def _get_llm_request_attributes(
    instance: ChatModelBase,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    """Get LLM request attributes for OpenTelemetry tracing.

    Extracts request parameters from LLM model calls into GenAI attributes.

    Args:
        instance (`ChatModelBase`):
            The chat model instance making the request.
        args (`Tuple[Any, ...]`):
            Positional arguments passed to the model call.
        kwargs (`Dict[str, Any]`):
            Keyword arguments including generation parameters such as
            temperature, top_p, top_k, max_tokens, presence_penalty,
            frequency_penalty, stop_sequences, seed, tools, and tool_choice.

    Returns:
        `Dict[str, Any]`:
            OpenTelemetry GenAI attributes with string values, including
            operation name, provider name, model name, generation parameters,
            tool definitions, and custom AgentScope function input.
    """

    attributes = {
        # required attributes
        SpanAttributes.GEN_AI_OPERATION_NAME: OperationNameValues.CHAT,
        SpanAttributes.GEN_AI_PROVIDER_NAME: _get_provider_name(instance),
        # conditionally required attributes
        SpanAttributes.GEN_AI_REQUEST_MODEL: getattr(
            instance,
            "model_name",
            "unknown_model",
        ),
        # recommended attributes
        SpanAttributes.GEN_AI_REQUEST_TEMPERATURE: kwargs.get("temperature"),
        SpanAttributes.GEN_AI_REQUEST_TOP_P: kwargs.get("p")
        or kwargs.get("top_p"),
        SpanAttributes.GEN_AI_REQUEST_TOP_K: kwargs.get("top_k"),
        SpanAttributes.GEN_AI_REQUEST_MAX_TOKENS: kwargs.get("max_tokens"),
        SpanAttributes.GEN_AI_REQUEST_PRESENCE_PENALTY: kwargs.get(
            "presence_penalty",
        ),
        SpanAttributes.GEN_AI_REQUEST_FREQUENCY_PENALTY: kwargs.get(
            "frequency_penalty",
        ),
        SpanAttributes.GEN_AI_REQUEST_STOP_SEQUENCES: kwargs.get(
            "stop_sequences",
        ),
        SpanAttributes.GEN_AI_REQUEST_SEED: kwargs.get("seed"),
        # custom attributes
        SpanAttributes.AGENTSCOPE_FUNCTION_INPUT: _serialize_to_str(
            {
                "args": args,
                "kwargs": kwargs,
            },
        ),
    }

    # Extract tool definitions if provided
    tool_definitions = _get_tool_definitions(
        tools=kwargs.get("tools"),
        tool_choice=kwargs.get("tool_choice"),
    )
    if tool_definitions:
        attributes[SpanAttributes.GEN_AI_TOOL_DEFINITIONS] = tool_definitions

    return {k: v for k, v in attributes.items() if v is not None}
```

---

## Official / 2026 links

- [Evaluation tutorial](https://doc.agentscope.io/tutorial/task_eval.html) · [OpenJudge + AgentScope](https://doc.agentscope.io/tutorial/task_eval_openjudge.html)
- [`research_overnight_stack_web/findings_judge_openjudge_agentscope_dify.md`](research_overnight_stack_web/findings_judge_openjudge_agentscope_dify.md)
