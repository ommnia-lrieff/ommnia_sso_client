from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class CreateRestoreSessionFailureCode(Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_NOT_ACTIVE = "USER_NOT_ACTIVE"
    SERVER_ERROR = "SERVER_ERROR"


class CreateRestoreSessionFailureResponse(BaseModel):
    typename: Literal["CreateRestoreSessionFailureResponse"] = "CreateRestoreSessionFailureResponse"
    code: CreateRestoreSessionFailureCode
    message: Optional[str] = None


class CreateRestoreSessionSuccessResponse(BaseModel):
    typename: Literal["CreateRestoreSessionSuccessResponse"] = "CreateRestoreSessionSuccessResponse"
    token: str


CreateRestoreSessionResponse = Annotated[
    Union[CreateRestoreSessionFailureResponse, CreateRestoreSessionSuccessResponse],
    Field(discriminator="typename"),
]
