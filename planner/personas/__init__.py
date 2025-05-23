from typing import Dict, Optional

import logfire
from pydantic import BaseModel
from pydantic_ai import Agent

from .architect import ARCHITECT_PROMPT, ArchitectInput, ArchitectOutput
from .investigator import INVESTIGATOR_PROMPT, InvestigatorInput
from .qahell import QA_PROMPT, QAInput
from .tldr import TLDR_PROMPT, TLDRInput, TLDROutput
from .utils import _KEY_CONFIG, initialize_model

_DEFAULT_MODEL_NAME = "qwen/qwen3-4b:free"


def setup_logfire():
    logfire.configure(token=_KEY_CONFIG["logfire"])


class ModelNames(BaseModel):
    architect: Optional[str] = _DEFAULT_MODEL_NAME
    investigator: Optional[str] = _DEFAULT_MODEL_NAME
    qa: Optional[str] = _DEFAULT_MODEL_NAME
    tldr: Optional[str] = _DEFAULT_MODEL_NAME


def setup_agents(model_names: ModelNames) -> Dict:
    """
    Set up the agents with the specified model names.
    """
    agents = {
        "investigator": Agent(
            model=initialize_model(model_names.investigator),
            system_prompt=INVESTIGATOR_PROMPT,
            name="investigator",
        ),
        "architect": Agent(
            name="architect",
            system_prompt=ARCHITECT_PROMPT,
            output_type=ArchitectOutput,
            model=initialize_model(model_names.architect),
        ),
        "qa": Agent(
            name="qa",
            system_prompt=QA_PROMPT,
            model=initialize_model(model_names.qa),
        ),
        "tldr": Agent(
            name="tldr",
            system_prompt=TLDR_PROMPT,
            model=initialize_model(model_names.tldr),
            output_type=TLDROutput,
        ),
    }
    return agents
