from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional, Union
from enum import Enum


class RestoreFailureCode(Enum):
    INVALID_TOKEN = "INVALID_TOKEN"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_COMPLETED = "SESSION_COMPLETED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    USER_NOT_ACTIVE = "USER_NOT_ACTIVE"
    WRONG_CODE = "WRONG_CODE"


class RestoreSuccessResponse(BaseModel):
    typename: Literal["RestoreSuccessResponse"] = "RestoreSuccessResponse"
    phantom: None = None


class RestoreFailureResponse(BaseModel):
    typename: Literal["RestoreFailureResponse"] = "RestoreFailureResponse"
    code: RestoreFailureCode
    message: Optional[str]


RestoreResponse = Annotated[
    Union[
        RestoreSuccessResponse,
        RestoreFailureResponse,
    ],
    Field(discriminator="typename"),
]
