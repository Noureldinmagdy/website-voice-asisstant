from abc import ABC
from pydantic import BaseModel
from typing import Optional, Any, List
import re
import pickle
from pydantic import (
    BaseModel, Field, EmailStr, create_model, computed_field
)
from typing import Literal

from map.webite import Website
from map.flow import Flow
from map.steps import InputStep, LeftClickStep
import json
import requests

import logging

logger = logging.getLogger(__name__)


WEBSITES = {
    "alcamp": "./data/maps/alcamp.json",
    "simple": "./data/maps/alcamp.json"
}


class Engine:

    def __init__(self, website, user_id):
        with open(WEBSITES[website], "r") as f:
            data = f.read()
        self.website_map = Website.model_validate_json(data)
        self.user_id = user_id

    def flows_desciption(self) -> str:
        return "\n".join(
            f"flow index = {i} - flow desciption = {desc}" for i, desc in self.website_map.flows_summary()
        )

    @property
    def current_flow(self) -> Flow:
        return self.website_map.current_flow
    
    def select_or_change_flow(self, idx):
        self.website_map.select_or_change_flow(idx)
        return "succfully selected/changed the flow"

    def progress(self) -> str:
        progress_logs = self.website_map.progress(callback=self.callback)
        return f"""
status of flow's progress 
{progress_logs}
"""
    
    def send_params_for_current_flow(self, data: dict) -> str:
        is_validated, report = self.website_map.send_params_for_current_flow(data)
        return f"""
is validated : {is_validated}
report of validation : {report}
"""
    
    def callback(self, **kwargs):
        step = kwargs["obj"]
        if isinstance(step, InputStep):
            response = requests.post(
                "http://127.0.0.1:5000/events/send-input", 
                json={
                    "xpath":step.x_path,
                    "user_id":self.user_id,
                    "value":list(step.input_data.values())[0]
                }, 
                headers = {
                    "Content-Type": "application/json"
                }
            )
        elif isinstance(step, LeftClickStep):
            response = requests.post(
                "http://127.0.0.1:5000/events/click", 
                json={
                    "xpath":step.x_path,
                    "user_id":self.user_id
                }, 
                headers = {
                    "Content-Type": "application/json"
                }
            )


if __name__ == "__main__":
    from map.logging_config import setup_logging
    setup_logging()

    engine = Engine("simple","user-zzpfpq")
    print(engine.progress())
    print("======================")
    print(engine.send_params_for_current_flow({"username":"mohamed saleh"}))
    print("======================")
    print(engine.progress())
    print("======================")
    print(engine.send_params_for_current_flow({"password":"2321321321321309000000"}))
    print("======================")
    print(engine.progress())
    