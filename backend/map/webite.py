
from pydantic import BaseModel
from typing import List
from pydantic import (
    BaseModel, computed_field
)
from map.flow import Flow
from pydantic import Field

class Website(BaseModel):
    flows: List[Flow] = Field(default_factory=list)
    current_flow_i: int = 0

    @computed_field
    @property
    def current_flow(self) -> Flow:
        return self.flows[self.current_flow_i]

    def flows_summary(self) -> list[tuple[int, str]]:
        return [(i, flow.desc) for i, flow in enumerate(self.flows)]
    
    def select_or_change_flow(self, idx) -> None:
        self.current_flow_i = idx

    def progress(self, callback: callable = None) -> str:
        return self.current_flow.progress(callback=callback)
    
    def send_params_for_current_flow(self, data: dict) -> list[bool, str]:
        return self.current_flow.send_params_for_current_step(data)