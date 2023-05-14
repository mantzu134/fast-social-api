from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
from fastapi import Depends, HTTPException, status
from . import schema
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_jwt_token(
    *,
    data: dict,
    secret_key: str = os.environ.get("SECRET_KEY"),
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=["HS256"])

        # Validate the payload using the Pydantic model
        valid_payload = schema.JWTPayload(**payload)

        return valid_payload.id

    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)