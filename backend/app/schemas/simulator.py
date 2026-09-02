from pydantic import BaseModel


class SimulatorRequest(BaseModel):
    scenario: str | None = None
