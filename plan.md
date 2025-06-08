# Plan for Multi-Agent System Refactoring and Insight Generation

## Goal 1: Refactor and Fix `multi_agents/agents/developer.py` (Status: COMPLETE)
Resolve lint errors in the refactored `developer.py` and ensure it correctly interacts with the `LLM` class for code generation.

### Steps Taken (COMPLETE):
1.  **Corrected LLM Interaction in `developer.py`:**
    *   Changed `self.llm.chat(...)` to `self.llm.generate(...)`.
    *   Adjusted assignment to `llm_raw_reply, _ = self.llm.generate(...)`.
2.  **Addressed Type Errors in Test Block (`if __name__ == '__main__':`)**:
    *   Added `# type: ignore` comments for `MockLLM` and `MockState` assignments and for the `action` call.
3.  **Reviewed and Resolved Lint Errors:**
    *   Corrected `state.memory` access in `Developer.action` to handle a list of agent outputs.
    *   Fixed `MockLLM.generate` history handling.
    *   Updated `MockState.memory` to be a list.
4.  **Testing (Manual/Visual):**
    *   The `if __name__ == '__main__':` block in `developer.py` was run successfully, verifying the refactored agent's core functionality and output file creation.

## Goal 2: Implement Iterative Insight Generation with Robust Context Management (Current Focus)
Enable the multi-agent system to iteratively build business insights by managing context primarily through an "insights log file" and relevant textual data, avoiding reliance on embedding models for now.

### Key Principles for Context Management:
*   **Insights Log File:** A central, human-readable file (e.g., `insights_log.md`) will store evolving insights, summaries, and key findings.
*   **Agent Responsibilities:**
    *   `Reader`: Will read initial business context, data summaries, and the current `insights_log.md` to establish context for the current iteration.
    *   `Planner`: Will use this context to formulate the next analysis step or question.
    *   `Developer`: Will generate code based on the plan and the provided context.
    *   `Reviewer` (if used): Will assess the generated code/output against the context and plan.
    *   `Summarizer`: Will synthesize new findings and update the `insights_log.md`.
*   **No Active Embedding Calls:** All direct calls to embedding models across any agent should be commented out or removed. Context will be built from explicit textual information.
*   **Intelligent Context Window Usage:** Agents should be prompted to utilize the provided context (insights log, data summaries, file contents) effectively to inform their actions.

### Next Steps:
1.  **Identify and Modify Embedding Calls:**
    *   Search codebase (all agents, utility functions) for any calls related to generating or using embeddings (e.g., `OpenAIEmbeddings`, vector store interactions).
    *   Comment out these sections, clearly marking them for potential future re-activation.
    *   Ensure that any logic relying on embeddings has a fallback or is adapted to work with textual context alone.
2.  **Establish `insights_log.md` Handling:**
    *   Define the initial structure/format for `insights_log.md`.
    *   Modify `Reader` agent to load `insights_log.md` at the beginning of an iteration and incorporate its content into the context provided to the `Planner`. If the file doesn't exist, start with an empty/initial state.
    *   Modify `Summarizer` agent to append new, structured insights to `insights_log.md` at the end of an iteration.
3.  **Adapt Agent Prompts for Contextual Awareness:**
    *   Review and update prompts for all agents to explicitly guide them to use the `insights_log.md` content and other provided textual summaries (business context, data summaries) for their decision-making and generation tasks.
4.  **Refine `State` and `SOP` for Iterative Flow:**
    *   Continue refining `State` and `SOP` to support a continuous iterative loop focused on augmenting the `insights_log.md`, rather than competition-specific phases or scores.
    *   Ensure `state.restore_dir` or a similar mechanism correctly manages outputs for each iteration of insight generation.

## Goal 3: Implement and Integrate Critic Agent
Integrate a `Critic` agent to review plans and summaries, providing feedback to improve the quality and relevance of generated insights. The `Critic` will also utilize and contribute to the `insights_log.md`.

### Steps:
1.  **Update `config.json`**: (Status: COMPLETE)
    *   Add `"Critic"` to relevant `phase_to_agents` lists.
    *   Define a configuration for the `Critic` agent under `agent_configurations`.
2.  **Create `multi_agents/agents/critic.py`**:
    *   Define the `Critic` class, inheriting from `AgentBase`.
    *   Implement the `_execute` method to:
        *   Identify the target of critique (e.g., plan from Planner, summary from Summarizer) based on its position in the agent sequence or specific phase logic.
        *   Read the `insights_log.md` for existing context.
        *   Generate a critique using the LLM, focusing on aspects like clarity, actionability, potential biases, and alignment with overall goals.
        *   Append its critique to `insights_log.md` in a structured format.
    *   Develop prompts for the `Critic` agent for different critique tasks (e.g., critiquing a plan, critiquing a summary).
3.  **Adapt `SOP` (if necessary)**:
    *   Ensure the `SOP` correctly sequences the `Critic` agent based on `config.json`.
    *   Verify that the `Critic`'s output can be handled or passed to subsequent agents if needed (though primarily it will write to `insights_log.md`).
4.  **Testing and Refinement**:
    *   Run the system with the `Critic` agent integrated.
    *   Review the critiques generated and their impact on the `insights_log.md`.
    *   Refine prompts and logic for the `Critic` based on test results.

## Future/Broader Goals (Post-Context Management Implementation):
The user also mentioned: "maybe use pandas profiler or something to generate spreadsheet summaries and use in context window to decide what to do next. the point is that it needs to be exploratory to ask questions like a data scientist, then generate and execute code to answer the question, then summarize and add the business insight to the log so a human can read the report."
This aligns with the longer-term vision. Once robust context management and iterative insight logging are in place, features like:
*   Automated data profiling (e.g., using pandas-profiling).
*   More sophisticated question generation by the `Planner`.
*   Tools for the `Developer` to interact with data (e.g., execute SQL, run Python for specific queries).
...can be built upon this foundation.
