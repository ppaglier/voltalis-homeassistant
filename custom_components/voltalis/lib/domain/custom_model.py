from pydantic import BaseModel, ConfigDict


class CustomModel(BaseModel):
    """BaseModel with custom configuration."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
