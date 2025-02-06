from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from schemas.oauth_sch import AccessToken
from services.oauth_service import OauthService
from services.azure_auth_service import AzureAuthService
from utils.exceptions.common_exception import IdNotFoundException

token_auth_scheme = HTTPBearer()

class Permission:
    def get_cred_exception(self, status_code: int, msg: str) -> HTTPException:
        credentials_exception = HTTPException(
            status_code=status_code,
            detail=msg,
            headers={"WWW-Authenticate": "Bearer"},
        )
        return credentials_exception
    
    async def is_allowed(self, role: str, token: str) -> bool:
        at, msg = await OauthService().check_token(token)
        if at:
            if role in at.authorities:
                return True
            else:
                raise self.get_cred_exception(
                    status.HTTP_403_FORBIDDEN, "Not Authorized")
        else:
            raise self.get_cred_exception(status.HTTP_401_UNAUTHORIZED, msg)

    async def is_authenticated(self, token: str = Depends(token_auth_scheme)) -> bool:
        at, msg = await OauthService().check_token(token)
        if at:
            return True
        else:
            raise self.get_cred_exception(status.HTTP_401_UNAUTHORIZED, msg)

    async def is_admin(self, token: str = Depends(token_auth_scheme)) -> bool:
        return await self.is_allowed('MSG_SVC_ADMIN', token)

    async def is_allowed_send(self, token: str = Depends(token_auth_scheme)) -> bool:
        return await self.is_allowed('MSG_SVC', token)
    
    async def get_login_user(self, request: Request, token: str = Depends(token_auth_scheme)) -> AccessToken:
        try:
            if len(token.credentials) == 30:
                login_user, msg = await OauthService().check_token(token.credentials)
            else:
                login_user, msg = await AzureAuthService().check_token(token.credentials)
                
            request.state.login_user = login_user
            if login_user is None:
                raise self.get_cred_exception(status.HTTP_401_UNAUTHORIZED, msg)
            return login_user
        except Exception as e:
            print(token.credentials) #tes failed login. delete soon
            raise self.get_cred_exception(status.HTTP_401_UNAUTHORIZED, e.detail if hasattr(e, 'detail') else str(e))

