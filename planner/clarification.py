import asyncio
from typing import List

from pydantic_ai import Agent

from planner.personas import InvestigatorInput

QUEUE_END_SIGNAL = None


class Clarification:
    """
    The ClarificationPhase class is responsible for managing the clarification phase of the planning process.
    It handles the interaction with the user to clarify any ambiguities in the plan.
    """

    agent: Agent
    last_input: InvestigatorInput = None

    def __init__(self, investigator_agent: Agent):
        """
        Initializes the ClarificationPhase with a reference to the planner.
        """
        self.agent = investigator_agent
        self.agent.instrument = True  # opentelemetry instrumentation on.
        self.last_input = None

    def _build_input(self, user_prompt: str) -> InvestigatorInput:
        """
        Builds the input for the agent based on the user's input.
        """
        if self.last_input is None:
            return InvestigatorInput(
                initial_idea=user_prompt,
                previous_dialogue_history="",
                latest_user_input=user_prompt,
            )

        return InvestigatorInput(
            initial_idea=self.last_input.initial_idea,
            previous_dialogue_history=self.last_input.previous_dialogue_history,
            latest_user_input=user_prompt,
        )

    def _update_last_input(self, curr_input: InvestigatorInput, response: str) -> None:
        """
        Appends the agent's response to the dialogue history. and updates the last input
        """
        prefix = "\n\nNext interaction"
        if self.last_input is None:
            prefix = "Initial interaction"

        curr_input.previous_dialogue_history += f"""{prefix}:
User: 
{curr_input.latest_user_input}
Assistant: 
{response}
"""
        self.last_input = curr_input

    async def accumulate_streams_to_queues(
        self, user_prompt: str, queues: List[asyncio.Queue]
    ):
        """
        Runs the clarification phase, prompting the user for clarifications as needed.
        """
        curr_input = self._build_input(user_prompt)
        response = ""
        async with self.agent.run_stream(curr_input.to_prompt()) as result:
            stream = result.stream_text(delta=True)
            async for token in stream:
                response += token
                # put token in all queues
                await asyncio.gather(*(queue.put(token) for queue in queues))

            await asyncio.gather(*(queue.put(QUEUE_END_SIGNAL) for queue in queues))

        self._update_last_input(curr_input, response)
