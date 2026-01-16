from pydantic import (
    BaseModel, Field, EmailStr, create_model
)
from typing import Any

TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "email": EmailStr,
    "any": Any
}

def build_input_schema(
    schema: dict,
    model_name: str = "DynamicInputSchema"
) -> type[BaseModel]:

    fields = {}

    for field_name, rules in schema.items():
        field_type_key = rules.get("type", "string")

        if field_type_key not in TYPE_MAP:
            raise ValueError(f"Unsupported type: {field_type_key}")

        field_type = TYPE_MAP[field_type_key]

        field_args = {}

        # Common constraints
        for key in [
            "min_length",
            "max_length",
            "ge",
            "le",
            "gt",
            "lt",
            "regex",
            "description"
        ]:
            if key in rules:
                field_args[key] = rules[key]

        default = rules.get("default", ...)

        fields[field_name] = (
            field_type,
            Field(default, **field_args)
        )

    return create_model(model_name, **fields)
