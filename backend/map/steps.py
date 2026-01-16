from abc import ABC
from pydantic import BaseModel
from typing import Any
import re
from typing import Literal
from map.utils.create_schema import build_input_schema


class Step(BaseModel, ABC):
    step_type: str
    x_path: str
    desc: str
    
    def run(self, callback: callable = None):
        if callback: callback(obj = self)
    
class LeftClickStep(Step):
    desc: str = "Left click on the element"
    step_type: Literal["left_click"] = "left_click"
    
    def run(self, **params):
        super().run(**params)
        return f"Left clicking on element at {self.x_path}"

class InputStep(Step):
    desc: str = "Input text into the element"
    step_type: Literal["input"] = "input"

    # 
    input_schema_def: dict | None = None

    input_data: dict | None = None

    @property
    def input_schema(self) -> type[BaseModel] | None:
        if self.input_schema_def is None:
            return None
        return build_input_schema(self.input_schema_def)

    def validate_input(self, input_data: dict) -> Any:
        try:
            self.input_data = self.input_schema.model_validate(input_data).model_dump()
            return True, "succfully validated"
        except Exception as e:
            error_report = str(e)

            error_report = re.sub(
                r"^\s*For further information visit.*$",
                "",
                error_report,
                flags=re.MULTILINE
            ).strip()

            return False, error_report
        
    
    def run(self, **params):
        super().run(**params)
        return f"Succfully Inputting text into element at {self.x_path} with {self.input_data}"

if __name__ == "__main__":
    a = LeftClickStep(
        x_path="sadas"
    )
    a.run(callback = lambda obj: print(isinstance(obj, LeftClickStep)))