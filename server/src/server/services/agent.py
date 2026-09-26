from enum import StrEnum

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openrouter import ChatOpenRouter
from pydantic import BaseModel

from server.core.config import settings


class Model(StrEnum):
    GEMINI_2_5_FLASH = "google/gemini-2.5-flash"


class Task(StrEnum):
    PROCESS_CV = Model.GEMINI_2_5_FLASH


class _Agent:
    def __init__(
        self,
        model: Model = Model.GEMINI_2_5_FLASH,
        system_prompt: str | None = None,
        structured_output: type[BaseModel] | None = None,
    ):
        self._agent = ChatOpenRouter(
            api_key=settings.openrouter_api_key,
            model=model.value,
        ).with_structured_output(structured_output)
        self._system_prompt = system_prompt

    async def invoke(self, prompt: str):
        return await self._agent.ainvoke(
            [
                SystemMessage(content=self._system_prompt),
                HumanMessage(content=prompt),
            ]
        )


def create_agent(
    model_or_task: Model | Task = Model.GEMINI_2_5_FLASH,
    *,
    system_prompt: str | None = None,
    structured_output: type[BaseModel] | None = None,
) -> _Agent:
    model = Model(model_or_task) if isinstance(model_or_task, Task) else model_or_task
    return _Agent(model, system_prompt, structured_output)
