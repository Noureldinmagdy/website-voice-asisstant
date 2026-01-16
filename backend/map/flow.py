
from pydantic import BaseModel
from typing import  List
from pydantic import (
    BaseModel, Field, computed_field
)
from typing import Union, Annotated
from pydantic import Field
from map.steps import LeftClickStep, InputStep




StepUnion = Annotated[
    Union[LeftClickStep, InputStep],
    Field(discriminator="step_type")
]

class Flow(BaseModel):
    steps: List[StepUnion] = []
    current_step_i: int = 0
    desc: str
    
    @computed_field
    @property
    def current_step(self) -> StepUnion:
        return self.steps[self.current_step_i]

    def progress(self, callback: callable = None) -> str:
        logs = ""
        for i in range(self.current_step_i, len(self.steps)):
            current_step = self.steps[self.current_step_i]
            if hasattr(current_step, "input_schema"):
                if current_step.input_data == None:
                    return "".join([
                        logs,
                        "current step desciption : \n",
                        current_step.desc + " \n",
                        "needs parameters to run \n",
                        str(current_step.input_schema.model_json_schema())
                    ])
            result = current_step.run(callback=callback)
            logs += f"{result} \n"

            if not self.current_step_i == len(self.steps)-1: # we not reached the last step
                self.current_step_i += 1
        
        return f"{logs} \nFlow compeleted"

                
    def send_params_for_current_step(self, data) -> list[bool, str]:
        return self.current_step.validate_input(data)
    
    def select_or_change_step(self, idx) -> None:
        self.current_step_i = idx
        