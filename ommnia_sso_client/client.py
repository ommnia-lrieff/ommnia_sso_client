from gql.transport.aiohttp import AIOHTTPTransport
from gql import Client as GQLClient, gql
from dataclasses import dataclass
from typing import ClassVar, List, Optional, Type
from graphql import DocumentNode as GQLDocumentNode
from ommnia_sso_tokens import TokenSigner, LoginSessionCreationToken
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from ommnia_sso_client.models import (
    CreateLoginSessionFailureCode,
    CreateLoginSessionFailureResponse,
    CreateLoginSessionResponse,
    CreateLoginSessionSuccessResponse,
    CreateRestoreSessionFailureCode,
    CreateRestoreSessionFailureResponse,
    CreateRestoreSessionResponse,
    CreateRestoreSessionSuccessResponse,
    RegularLoginFailureCode,
    RegularLoginFailureResponse,
    RegularLoginRequest,
    RegularLoginResponse,
    RegularLoginSuccessResponse,
)
from ommnia_sso_client.models.login_session_details import (
    LoginSessionDetailsFailureCode,
    LoginSessionDetailsFailureResponse,
    LoginSessionDetailsResponse,
    LoginSessionDetailsSuccessResponse,
)
from ommnia_sso_client.models.restore import (
    RestoreFailureCode,
    RestoreFailureResponse,
    RestoreResponse,
    RestoreSuccessResponse,
)


@dataclass(frozen=True, kw_only=True)
class ClientSettings:
    app_name: str  # The name of the app for which the client is active.
    graphql_server_url: str  # The URL of the SSO GraphQL server.
    client_private_key: (
        str  # The private RSA signing key used to sign the JWT that is sent to the server.
    )
    server_public_key: str  # The public RSA verification key used to verify the JWT that originates from the server.


class _ClientFactory:
    def create(self, settings: ClientSettings) -> "Client":
        return Client(
            settings=settings,
            client=GQLClient(transport=AIOHTTPTransport(url=settings.graphql_server_url)),
        )


class ClientFactory:
    _instance: ClassVar[Optional[_ClientFactory]] = None

    def __new__(cls: Type["ClientFactory"]) -> _ClientFactory:
        if cls._instance is None:
            cls._instance = _ClientFactory()

        return cls._instance


@dataclass(frozen=True, kw_only=True)
class Client:
    settings: ClientSettings
    client: GQLClient

    @dataclass(frozen=True, kw_only=True)
    class CreateLoginURLException(Exception):
        code: CreateLoginSessionFailureCode
        message: Optional[str]

    @dataclass(frozen=True, kw_only=True)
    class RegularLoginException(Exception):
        code: RegularLoginFailureCode
        message: Optional[str]

    @dataclass(frozen=True, kw_only=True)
    class CreateRestoreSessionException(Exception):
        code: CreateRestoreSessionFailureCode
        message: Optional[str]

    @dataclass(frozen=True, kw_only=True)
    class RestoreException(Exception):
        code: RestoreFailureCode
        message: Optional[str]

    @dataclass(frozen=True, kw_only=True)
    class LoginSessionDetailsException(Exception):
        code: LoginSessionDetailsFailureCode
        message: Optional[str]

    class _CreateLoginSessionMutationResponse(BaseModel):
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        create_login_session: CreateLoginSessionResponse

    class _RegularLoginMutationResponse(BaseModel):
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        regular_login: RegularLoginResponse

    class _CreateRestoreSessionMutationResponse(BaseModel):
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        create_restore_session: CreateRestoreSessionResponse

    class _RestoreMutationResponse(BaseModel):
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        restore: RestoreResponse

    class _LoginSessionDetailsQueryResponse(BaseModel):
        model_config = ConfigDict(
            alias_generator=to_camel,
            populate_by_name=True,
            from_attributes=True,
        )

        login_session_details: LoginSessionDetailsResponse

    _CREATE_LOGIN_SESSION_MUTATION: ClassVar[GQLDocumentNode] = gql("""
    mutation CreateLoginSession($requestToken: String!) {
        createLoginSession(requestToken: $requestToken) {
            typename: __typename
            
            ... on CreateLoginSessionFailureResponse {
                message
                code
            }

            ... on CreateLoginSessionSuccessResponse {
                __typename
                token
            }
        }
    }
    """)

    _REGULAR_LOGIN_MUTATION: ClassVar[GQLDocumentNode] = gql("""
    mutation RegularLoginMutation($request: RegularLoginRequest!) {
        regularLogin(request: $request) {
            typename: __typename

            ... on RegularLoginSuccessResponse {
                token
            }

            ... on RegularLoginFailureResponse {
                message
                code
            }
        }
    }
    """)

    _CREATE_RESTORE_SESSION_MUTATION: ClassVar[GQLDocumentNode] = gql("""
    mutation CreateRestoreSessionMutation($email: String!) {
        createRestoreSession(email: $email) {
            typename: __typename
            
            ... on CreateRestoreSessionFailureResponse {
                message
                code
            }
            ... on CreateRestoreSessionSuccessResponse {
                token
            }
        }
    }
    """)

    _RESTORE_MUTATION: ClassVar[GQLDocumentNode] = gql("""
    mutation RestoreMutation($code: String!, $password: String!, $token: String!) {
        restore(code: $code, password: $password, token: $token) {
            typename: __typename

            ... on RestoreFailureResponse {
                message
                code
            }
            ... on RestoreSuccessResponse {
                phantom
            }
        }
    }
    """)

    _LOGIN_SESSION_DETAILS_QUERY: ClassVar[GQLDocumentNode] = gql("""
    query LoginSessionDetailsQuery($token: String!) {
        loginSessionDetails(token: $token) {
            typename: __typename
            
            ... on LoginSessionDetailsFailureResponse {
                message
                code
            }
            ... on LoginSessionDetailsSuccessResponse {
                redirectTo
                optionalPermissions
                requiredPermissions
            }
        }
    }
    """)

    async def login_session_details(self, token: str) -> LoginSessionDetailsResponse:
        response: LoginSessionDetailsResponse = (
            self._LoginSessionDetailsQueryResponse.model_validate(
                await self.client.execute_async(
                    self._LOGIN_SESSION_DETAILS_QUERY,
                    {
                        "token": token,
                    },
                )
            ).login_session_details
        )

        if isinstance(response, LoginSessionDetailsFailureResponse):
            raise self.LoginSessionDetailsException(
                code=response.code,
                message=response.message,
            )

        assert isinstance(response, LoginSessionDetailsSuccessResponse)
        return response

    async def restore(
        self,
        code: str,
        password: str,
        token: str,
    ) -> None:
        response: RestoreResponse = self._RestoreMutationResponse.model_validate(
            await self.client.execute_async(
                self._CREATE_RESTORE_SESSION_MUTATION,
                {
                    "code": code,
                    "password": password,
                    "token": token,
                },
            )
        ).restore

        if isinstance(response, RestoreFailureResponse):
            raise self.RestoreException(
                code=response.code,
                message=response.message,
            )

        assert isinstance(response, RestoreSuccessResponse)

    async def create_restore_session(
        self,
        email: str,
    ) -> str:
        response: CreateRestoreSessionResponse = (
            self._CreateRestoreSessionMutationResponse.model_validate(
                await self.client.execute_async(
                    self._CREATE_RESTORE_SESSION_MUTATION,
                    {
                        "email": email,
                    },
                )
            ).create_restore_session
        )

        if isinstance(response, CreateRestoreSessionFailureResponse):
            raise self.CreateRestoreSessionException(
                code=response.code,
                message=response.message,
            )

        assert isinstance(response, CreateRestoreSessionSuccessResponse)
        return response.token

    async def regular_login(
        self,
        email: str,
        password: str,
        token: str,
    ) -> str:
        request: RegularLoginRequest = RegularLoginRequest(
            email=email,
            password=password,
            token=token,
        )

        response: RegularLoginResponse = self._RegularLoginMutationResponse.model_validate(
            await self.client.execute_async(
                self._REGULAR_LOGIN_MUTATION,
                {
                    "request": request.model_dump(),
                },
            )
        ).regular_login

        if isinstance(response, RegularLoginFailureResponse):
            raise self.RegularLoginException(
                code=response.code,
                message=response.message,
            )

        assert isinstance(response, RegularLoginSuccessResponse)
        return response.token

    async def create_login_token(
        self,
        redirect_url: str,
        target_app_name: Optional[str] = None,
        required_permissions: List[str] = [],
        optional_permissions: List[str] = [],
    ) -> str:
        token_value: LoginSessionCreationToken = LoginSessionCreationToken(
            app_name=self.settings.app_name,
            target_app_name=target_app_name,
            required_permissions=required_permissions,
            optional_permissions=optional_permissions,
            redirect_url=redirect_url,
        )

        request_token: str = await TokenSigner().sign(token_value, self.settings.client_private_key)

        response: CreateLoginSessionResponse = (
            self._CreateLoginSessionMutationResponse.model_validate(
                await self.client.execute_async(
                    self._CREATE_LOGIN_SESSION_MUTATION,
                    {
                        "requestToken": request_token,
                    },
                )
            ).create_login_session
        )

        if isinstance(response, CreateLoginSessionFailureResponse):
            raise self.CreateLoginURLException(
                code=response.code,
                message=response.message,
            )

        assert isinstance(response, CreateLoginSessionSuccessResponse)
        return response.token
