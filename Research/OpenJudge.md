#llm-judge

**Yes, OpenJudge fully supports customization for evaluating arbitrary execution traces against user-defined scenarios using LLM judges.**

## Core Capabilities

### 1. Arbitrary Input Parameters

OpenJudge graders accept arbitrary input parameters through the `**kwargs` mechanism in the `aevaluate` method. [1](#2-0)  This allows you to pass any data including execution traces, logs, API outputs, scenario descriptions, and final states.

### 2. Custom LLM-Based Graders

You can create custom LLM judges using the `LLMGrader` class, which takes a template and model configuration. [2](#2-1)  The template formatting automatically incorporates all passed parameters, including scenario text and trace data. [3](#2-2) 

### 3. Satisfaction Score Output

All graders return a `GraderScore` object containing a numerical satisfaction score (typically 0.0-1.0 or 1-5 scale), reasoning, and optional metadata. [4](#2-3) 

### 4. Built-in Execution Trace Example

OpenJudge includes `TrajectoryComprehensiveGrader` as a concrete example that evaluates complete agent execution traces. [5](#2-4)  It accepts messages in OpenAI format (including tool calls, responses, and final states) and returns comprehensive satisfaction scores across multiple dimensions. [6](#2-5) 

## Implementation Approaches

### Custom LLM Judge for Scenarios

You can define custom prompt templates that incorporate scenario descriptions and execution trace data: [7](#2-6) 

The template can reference any parameters you pass to `aevaluate()`, such as `{scenario}`, `{execution_trace}`, `{api_outputs}`, or `{final_state}`.

### Custom Function-Based Graders

For deterministic evaluation logic, use `FunctionGrader` with custom functions that process trace data: [8](#2-7) 

Your function can accept arbitrary parameters including scenario text and trace data, then return a satisfaction score. [9](#2-8) 

### Scenario-Specific Rubrics

OpenJudge supports generating scenario-specific evaluation rubrics using the `SimpleRubricsGenerator`, which accepts a scenario parameter: [10](#2-9) 

This allows you to create graders tailored to specific usage scenarios that evaluate traces accordingly.

## Notes

- **Flexibility**: The `**kwargs` design pattern means you can pass any combination of parameters (scenario, logs, traces, states) without modifying the base framework.
- **Template Variables**: In LLM graders, any parameter passed to `aevaluate()` becomes available as a template variable for formatting prompts.
- **Metadata Support**: The `GraderScore` includes a metadata field for storing additional evaluation details beyond the satisfaction score.
- **Batch Evaluation**: Use `GradingRunner` to evaluate multiple traces concurrently with progress tracking. [11](#2-10) 
- **Integration**: OpenJudge integrates with observability platforms like Langfuse for fetching execution traces and evaluating them. [12](#2-11)

### Citations

**File:** openjudge/graders/base_grader.py (L78-95)
```python
    @abstractmethod
    async def aevaluate(self, **kwargs: Any) -> GraderScore | GraderRank | GraderError:
        """Abstract method for performing the actual evaluation logic.

        This method must be implemented by all Grader subclasses. It performs
        the actual evaluation logic and returns either a score or a ranking based on
        the grader's mode (pointwise or listwise).

        In pointwise mode, each sample is evaluated independently, returning a
        GraderScore with a numerical value and explanation. In listwise mode, all
        samples are evaluated together, returning a GraderRank with a ranked list and
        explanation.

        Args:
            **kwargs: Arbitrary keyword arguments containing the data to be evaluated.
                     The specific arguments depend on the grader implementation but
                     typically include fields like 'query', 'answer', 'context', etc.

```

**File:** openjudge/graders/llm_grader.py (L36-93)
```python
class LLMGrader(BaseGrader):
    """LLM-based grader that uses large language models for evaluation.

    This class extends the base Grader class to provide LLM-based evaluation capabilities.
    It uses a language model to perform evaluations according to specified rubrics and templates.

    The LLMGrader constructs prompts using a template, sends them to an LLM, and parses
    the structured response into either a GraderScore or GraderRank depending on the mode.

    Attributes:
        template (Template): The template for generating prompts.
        model (BaseChatModel): The language model used for evaluation.
        rubrics (str): The rubrics used for evaluation.
        language (LanguageEnum): The language for the evaluation.
        structured_model (Type[BaseModel]): Pydantic model to process model response
                                             into GraderScore or GraderRank.
        callback (Callable): Function to process model response metadata.
    """

    def __init__(
        self,
        model: BaseChatModel | dict,
        name: str = "",
        mode: GraderMode = GraderMode.POINTWISE,
        language: LanguageEnum | str | None = None,
        description: str = "",
        template: str | dict | PromptTemplate | None = None,
        structured_model: Type[BaseModel] | None = None,
        callback: Callable | None = None,
        **kwargs: Any,
    ):
        """Initialize an LLMGrader.

        Args:
            model: The language model used for evaluation. Can be either a BaseChatModel
                   instance or a dictionary configuration. If a dict is provided, it will
                   be used to initialize an OpenAIChatModel.
            name: The name of the grader. Used for identification and logging.
            mode: The grader mode. Either POINTWISE (individual sample evaluation)
                  or LISTWISE (joint evaluation of multiple samples).
                  Defaults to POINTWISE.
            language: The language of the grader. Can be LanguageEnum, string, or None.
                     If None, defaults to environment variable LANGUAGE or "en".
            description: Human-readable description of what this grader evaluates.
            template: The template for generating prompts. Defines how inputs are formatted
                     for the LLM. Can be a dict or PromptTemplate object.
            structured_model: The Pydantic model for structured output parsing.
                      Can be one of the following:
                      1. A Pydantic BaseModel subclass for structured output parsing
                      2. None, in which case uses GraderScoreCallback for POINTWISE mode
                         or GraderRankCallback for LISTWISE mode
            callback: The callback function for processing model response metadata.
                      Can be one of the following:
                      3. A Callable that processes the response and populates metadata
                      4. None, in which case no callback processing is performed
            **kwargs: Additional keyword arguments passed to the parent Grader class and
                     used in the template rendering.
        """
```

**File:** openjudge/graders/llm_grader.py (L295-303)
```python

        params = {**self.kwargs}
        params.update(kwargs)
        messages = self.template.format(language=self.language, **params)
        chat_response = await self.model.achat(
            messages=list(messages),
            structured_model=self.structured_model,
            callback=self.callback,
        )
```

**File:** openjudge/graders/schema.py (L68-90)
```python
class GraderScore(GraderResult):
    """Grader score result.

    Represents a numerical score assigned by a grader along with a reason.

    Attributes:
        score (float): A numerical score assigned by the grader.
        reason (str): Explanation of how the score was determined.
        metadata (Dict[str, Any]): Optional additional information from the evaluation.

    Example:
        >>> score_result = GraderScore(
        ...     name="accuracy_grader",
        ...     score=0.85,
        ...     reason="Answer is mostly accurate",
        ...     metadata={"confidence": 0.9}
        ... )
        >>> print(score_result.score)
        0.85
    """

    score: float = Field(default=..., description="score")

```

**File:** openjudge/graders/agent/trajectory/trajectory_comprehensive.py (L273-310)
```python
class TrajectoryComprehensiveGrader(LLMGrader):
    """
    Comprehensive evaluation grader for agent trajectories.

    This grader evaluates agent trajectories by assessing each step independently:
    - Step-level evaluation: contribution, relevance, accuracy, efficiency (per step)
    - Overall score is computed by averaging all step scores (not from LLM output)

    The grader uses a 1-5 integer scoring system in prompts to avoid ambiguous boundary
    definitions, then normalizes scores to 0-1 range (1->0.0, 2->0.25, 3->0.5, 4->0.75, 5->1.0).

    The overall score is computed as:
    1. For each step: average of (contribution, relevance, accuracy, efficiency)
    2. Overall score: average of all step scores

    The grader accepts standard messages format and automatically extracts
    the trajectory after removing system prompts.

    Attributes:
        name: Grader name
        model: ChatModelBase instance for evaluation
        language: Language for evaluation prompts
        resolution_threshold: Threshold for determining if the trajectory is resolved (default: 0.8, on normalized 0-1 scale)

    Example:
        >>> import asyncio
        >>> from openjudge.models.openai_chat_model import OpenAIChatModel
        >>> api = OpenAIChatModel(api_key="...", model="qwen3-32b")
        >>> grader = TrajectoryComprehensiveGrader(model=api, resolution_threshold=0.75)
        >>> result = asyncio.run(grader.aevaluate(
        ...     messages=[
        ...         {"role": "system", "content": "..."},
        ...         {"role": "user", "content": "帮我找投资建议"},
        ...         {"role": "assistant", "content": "...", "tool_calls": [...]},
        ...         ...
        ...     ]
        ... ))
        >>> print(f"Score: {result.score}")  # computed from step averages
```

**File:** openjudge/graders/agent/trajectory/trajectory_comprehensive.py (L535-593)
```python
    async def aevaluate(
        self,
        messages: List[Dict[str, Any]],
        query: Optional[str] = None,
        response: Optional[str | Dict[str, Any]] = None,
    ) -> GraderScore | GraderError:
        """
        Evaluate complete agent trajectory comprehensively.

        The evaluation uses 1-5 integer scores in LLM prompts for each step, then normalizes to 0-1 scale:
        - 1 -> 0.0, 2 -> 0.25, 3 -> 0.5, 4 -> 0.75, 5 -> 1.0

        The overall score is computed as the average of all step scores (each step's score is the average
        of its four dimensions: contribution, relevance, accuracy, efficiency).

        The callback function handles step-level to final score/reason conversion efficiently:
        - Calculates average raw scores (1-5) first
        - Then normalizes the final result (avoiding redundant per-step normalization for aggregation)

        Args:
            messages: List of messages (standard format, including system, user, assistant, tool)
                "message" key for message, and "tool_call" key for tool call can be optional.
                example without "message" and "tool_call"
                ```
                [
                  {"role": "system", "content": "..."},
                  {"role": "user", "content": "Plan travel from Shanghai to Hangzhou."},
                  {"role": "assistant", "tool_calls": [{"function": {"arguments": "{\"city\": \"Hangzhou\"}","name": "weather"}}]}
                ]
                ```
                or with "message" and "tool_call"
                ```
                [
                  {"message":{"role": "system", "content": "..."}},
                  {"message":{"role": "user", "content": "Plan travel from Shanghai to Hangzhou."}},
                  {"role": "assistant", "tool_calls": [{"tool_call":{"function": {"arguments": "{\"city\": \"Hangzhou\"}","name": "weather"}}}]}
                ]
                ```
            query:    optional, user query, will use the first message with role=user as query if not provided.
            response: optional, final response, will use the last non-emptry message 'content' with role=assistant if not provided.

        Returns:
            GraderScore: Comprehensive evaluation score for the trajectory (normalized 0.0-1.0)
                - score: Overall score computed from step averages (normalized 0.0-1.0)
                - reason: Aggregated evaluation summary generated from step evaluations
                - metadata: Contains step_evaluations list with normalized (0-1) scores

        Example:
            >>> result = await grader.aevaluate(
            ...     messages=[
            ...         {"role": "user", "content": "帮我找投资建议"},
            ...         {"role": "assistant", "content": "...", "tool_calls": [...]},
            ...         ...
            ...     ]
            ... )
            >>> print(f"Overall Score: {result.score}")  # normalized 0-1, computed from step averages
            >>> for step in result.metadata["step_evaluations"]:
            ...     print(f"Step {step['step_index']}: contribution={step['contribution_score']}")
        """
```

**File:** docs/building_graders/create_custom_graders.md (L92-127)
```markdown
```python
from openjudge.graders.llm_grader import LLMGrader
from openjudge.models.openai_chat_model import OpenAIChatModel

# Define your model
model = OpenAIChatModel(
    model="qwen3-32b",
    api_key="your-api-key"
)

# Create your grader with a well-engineered prompt
helpfulness_grader = LLMGrader(
    name="helpfulness_evaluator",
    mode="pointwise",
    model=model,
    template="""
    You are an expert evaluator assessing the helpfulness of AI responses.

    Instructions:
    1. Consider accuracy, completeness, clarity, and relevance
    2. Score 0.0 for completely unhelpful responses
    3. Score 1.0 for exceptionally helpful responses
    4. Score in between for partial helpfulness

    Query: {query}
    Response: {response}

    Provide your response in JSON format:
    {
        "score": <numerical_score_between_0_and_1>,
        "reason": "<brief_explanation_for_score>"
    }
    """,
    description="Evaluates how helpful a response is to the given query"
)
```
```

**File:** openjudge/graders/function_grader.py (L27-71)
```python
class FunctionGrader(BaseGrader):
    """Function-based grader.

    A grader that uses a provided function to perform evaluations.

    Attributes:
        func (Callable): The function to use for evaluation.
        name (str): The name of the grader.
        mode (GraderMode): The grader mode.
    """

    def __init__(
        self,
        func: Callable,
        name: str = "",
        mode: GraderMode = GraderMode.POINTWISE,
        description: str = "",
        **kwargs: Any,
    ):
        """Initialize a FunctionGrader.

        Args:
            func: The function to use for evaluation. This function will be called
                  with the evaluation data and must return either a GraderScore (for
                  pointwise mode) or a GraderRank (for listwise mode).

                  For pointwise mode, typical signature:
                  ```async def my_func(query: str, response: str, **kwargs) -> GraderScore:```

                  For listwise mode, typical signature:
                  ```async def my_func(query: str, responses: List[str], **kwargs) -> GraderRank:```
            name: The name of the grader. Used for identification and logging.
            mode: The grader mode. Either POINTWISE (individual sample evaluation)
                  or LISTWISE (joint evaluation of multiple samples).
                  Defaults to POINTWISE.
            description: Human-readable description of what this grader evaluates.
            **kwargs: Additional keyword arguments passed to the parent Grader class.
        """
        super().__init__(
            name,
            mode,
            description,
            **kwargs,
        )
        self.func = func
```

**File:** openjudge/graders/function_grader.py (L73-100)
```python
    async def aevaluate(self, **kwargs: Any) -> GraderScore | GraderRank:
        """Evaluate using a function.

        Performs evaluation by calling the wrapped function with the provided arguments.
        The function must return either a GraderScore (for pointwise mode) or a
        GraderRank (for listwise mode) object.

        Args:
            **kwargs: Arbitrary keyword arguments containing the data to be evaluated.
                     These are passed directly to the wrapped function and typically
                     include fields like 'query', 'answer', 'context', etc. The specific
                     fields depend on the function's requirements.

        Returns:
            GraderScore | GraderRank: The evaluation result from the wrapped function.

            In pointwise mode:
                GraderScore: Contains a numerical score and explanation.
                    - score (float): Numerical score computed by the function
                    - reason (str): Explanation of how the score was determined
                    - metadata (Dict[str, Any]): Additional evaluation information

            In listwise mode:
                GraderRank: Contains a ranked list and explanation.
                    - rank (List[int]): Ranking of items computed by the function
                    - reason (str): Explanation of how the ranking was determined
                    - metadata (Dict[str, Any]): Additional evaluation information

```

**File:** openjudge/generator/simple_rubric/generator.py (L1-50)
```python
# -*- coding: utf-8 -*-
"""Simple rubrics generator implementation.

This module implements a task-description-based approach to generating
evaluation rubrics. It creates LLMGrader instances with rubrics generated
from task descriptions and sample queries.

This is a simpler alternative to the iterative_rubric module, which learns
rubrics from preference data through an iterative refinement process.

Usage:
    >>> from openjudge.generator.simple_rubric import SimpleRubricsGenerator, SimpleRubricsGeneratorConfig
    >>> from openjudge.models.openai_chat_model import OpenAIChatModel
    >>>
    >>> config = SimpleRubricsGeneratorConfig(
    ...     grader_name="Medical QA Grader",
    ...     model=OpenAIChatModel(model="gpt-4o-mini"),
    ...     task_description="Medical question answering system",
    ...     scenario="Healthcare professionals seeking quick answers"
    ... )
    >>> generator = SimpleRubricsGenerator(config)
    >>> grader = await generator.generate(dataset=[], sample_queries=["What are the symptoms of flu?"])
"""

from dataclasses import dataclass, field
from typing import List, Optional

from loguru import logger

from openjudge.generator.iterative_rubric.query_rubric_generator import (
    LISTWISE_EVALUATION_TEMPLATE,
    POINTWISE_EVALUATION_TEMPLATE,
)
from openjudge.generator.llm_grader_generator import (
    LLMGraderGenerator,
    LLMGraderGeneratorConfig,
)
from openjudge.generator.simple_rubric.rubric_generator import TaskBasedRubricGenerator
from openjudge.graders.llm_grader import LLMGrader
from openjudge.graders.schema import GraderMode
from openjudge.models.openai_chat_model import OpenAIChatModel
from openjudge.models.schema.prompt_template import LanguageEnum


@dataclass
class SimpleRubricsGeneratorConfig(LLMGraderGeneratorConfig):
    """Configuration for simple rubrics generator.

    This configuration extends LLMGraderGeneratorConfig with parameters
    specific to task-description-based rubric generation.
```

**File:** docs/get_started/evaluate_ai_agents.md (L367-453)
```markdown
## Batch Evaluation with GradingRunner

For evaluating multiple agent traces efficiently, use `GradingRunner` to run graders concurrently with automatic progress tracking:

```python
import asyncio
from openjudge.graders.agent import ToolSelectionGrader
from openjudge.models import OpenAIChatModel
from openjudge.runner.grading_runner import GradingRunner, GraderConfig

async def main():
    # Initialize model and grader
    model = OpenAIChatModel(model="qwen3-32b")
    grader = ToolSelectionGrader(model=model)

    # Define mapper to extract grader inputs from agent traces
    def extract_tool_inputs(data: dict) -> dict:
        messages = data["messages"]
        query = next((m["content"] for m in messages if m["role"] == "user"), "")
        tool_calls = []
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    tool_calls.append({
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"]
                    })
        return {
            "query": query,
            "tool_definitions": data["available_tools"],
            "tool_calls": tool_calls
        }

    # Configure runner with mapper
    runner = GradingRunner(
        grader_configs={
            "tool_selection": GraderConfig(
                grader=grader,
                mapper=extract_tool_inputs
            )
        },
        max_concurrency=16,
        show_progress=True
    )

    # Prepare dataset (agent traces)
    dataset = [
        {   # Bad case: should use calculator, not search_web
            "messages": [
                {"role": "user", "content": "What's 15% tip on a $45 bill?"},
                {"role": "assistant", "tool_calls": [{"function": {"name": "search_web", "arguments": '{"query": "15% tip on $45"}'}}]}
            ],
            "available_tools": [
                {"name": "calculator", "description": "Perform mathematical calculations"},
                {"name": "search_web", "description": "Search the web for information"}
            ]
        },
        {   # Good case: correctly uses get_weather
            "messages": [
                {"role": "user", "content": "What's the weather in Tokyo?"},
                {"role": "assistant", "tool_calls": [{"function": {"name": "get_weather", "arguments": '{"location": "Tokyo"}'}}]}
            ],
            "available_tools": [
                {"name": "get_weather", "description": "Get weather information"},
                {"name": "search_web", "description": "Search the web for information"}
            ]
        },
    ]

    # Run batch evaluation
    results = await runner.arun(dataset)

    # Print results
    for i, result in enumerate(results["tool_selection"]):
        print(f"Trace {i}: Score={result.score}")

asyncio.run(main())
```

**Output:**

```
Trace 0: Score=2.0   # Wrong tool: used search_web instead of calculator
Trace 1: Score=5.0   # Correct tool: used get_weather for weather query
```

For more details on batch evaluation, data mapping, and result aggregation, see [Run Grading Tasks](../running_graders/run_tasks.md)
**File:** README.md (L307-320)
```markdown
## 🔗 Integrations

Seamlessly connect OpenJudge with mainstream observability and training platforms:

| Category | Platform | Status | Documentation |
|:---------|:---------|:------:|:--------------|
| **Observability** | [LangSmith](https://smith.langchain.com/) | ✅ Available | 👉 [LangSmith Integration Guide](https://agentscope-ai.github.io/OpenJudge/integrations/langsmith/) |
| | [Langfuse](https://langfuse.com/) | ✅ Available | 👉 [Langfuse Integration Guide](https://agentscope-ai.github.io/OpenJudge/integrations/langfuse/) |
| | Other frameworks | 🔵 Planned | — |
| **Training** | [verl](https://github.com/volcengine/verl) | ✅ Available | 👉 [VERL Integration Guide](https://agentscope-ai.github.io/OpenJudge/integrations/verl/) |
| | [Trinity-RFT](https://github.com/modelscope/Trinity-RFT) | 🔵 Planned | — |

> 💬 Have a framework you'd like us to prioritize? [Open an Issue](https://github.com/agentscope-ai/OpenJudge/issues)!

```

---

## Official / 2026 links

- **Install:** [`pip install py-openjudge`](https://pypi.org/project/py-openjudge/) — import `openjudge` (do **not** confuse with PyPI package `openjudge`)
- [GitHub `agentscope-ai/OpenJudge`](https://github.com/agentscope-ai/OpenJudge) · [Documentation](https://agentscope-ai.github.io/OpenJudge/)
- [Langfuse integration](https://agentscope-ai.github.io/OpenJudge/integrations/langfuse/) · [LangSmith integration](https://agentscope-ai.github.io/OpenJudge/integrations/langsmith/)
- [`research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md`](research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md)
