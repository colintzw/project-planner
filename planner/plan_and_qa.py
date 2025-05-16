from personas import ArchitectInput, ArchitectOutput, QAInput
from pydantic_ai import Agent


class Architect:
    def __init__(self, architect_agent: Agent, qa_agent: Agent):
        self.architect_agent = architect_agent
        self.qa_agent = qa_agent

    def _build_qa_input(
        self, architect_input: ArchitectInput, architect_output: ArchitectOutput
    ) -> QAInput:
        """
        Build the input for the QA agent based on the architect's output.
        """
        return QAInput(
            clarified_context=architect_input.clarified_context,
            detailed_action_plan=architect_output.detailed_action_plan,
            mvp_action_plan=architect_output.mvp_action_plan,
        )

    def _build_architect_input(
        self, clarified_context: str, critique_feedback: str = ""
    ) -> ArchitectInput:
        return ArchitectInput(
            clarified_context=clarified_context, critique_feedback=critique_feedback
        )

    def run_plan(
        self, clarified_context: str, num_qa_turns: int = 3
    ) -> ArchitectOutput:

        curr_input = self._build_architect_input(
            clarified_context=clarified_context, critique_feedback=""
        )
        curr_plan = self.architect_agent.run_sync(
            user_prompt=curr_input.to_prompt()
        ).output

        for _ in range(num_qa_turns):
            qa_input = self._build_qa_input(curr_input, curr_plan)
            critique = self.qa_agent.run_sync(user_prompt=qa_input.to_prompt()).output

            curr_input = self._build_architect_input(
                clarified_context=clarified_context, critique_feedback=critique
            )
            curr_plan = self.architect_agent.run_sync(
                user_prompt=curr_input.to_prompt()
            ).output

        return curr_plan
