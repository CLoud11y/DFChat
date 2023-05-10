from datetime import datetime
from config import SECRET_KEY, ALGORITHM
import jwt
from jwt.exceptions import PyJWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security_scheme = HTTPBearer()

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration = datetime.fromtimestamp(payload["exp"])
        if datetime.now() > expiration:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            return payload
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security_scheme)):
    return verify_jwt_token(token.credentials)
