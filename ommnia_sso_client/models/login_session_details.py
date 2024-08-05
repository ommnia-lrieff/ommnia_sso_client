from enum import Enum
from typing import Annotated, List, Literal, Optional, Union
from pydantic.alias_generators import to_camel
from pydantic import BaseModel, ConfigDict, Field


class LoginSessionDetailsFailureCode(Enum):
    INVALID_TOKEN = "INVALID_TOKEN"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_COMLETED = "SESSION_COMLETED"


class LoginSessionDetailsSuccessResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    typename: Literal["LoginSessionDetailsSuccessResponse"] = "LoginSessionDetailsSuccessResponse"
    required_permissions: List[str]
    optional_permissions: List[str]
    redirect_to: str


class LoginSessionDetailsFailureResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
    
    typename: Literal["LoginSessionDetailsFailureResponse"] = "LoginSessionDetailsFailureResponse"
    code: LoginSessionDetailsFailureCode
    message: Optional[str]


LoginSessionDetailsResponse = Annotated[
    Union[
        LoginSessionDetailsSuccessResponse,
        LoginSessionDetailsFailureResponse,
    ],
    Field(discriminator="typename"),
]
