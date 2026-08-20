from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.database import get_connection
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not configured."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password):

    return pwd_context.hash(password)


def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(username):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def authenticate_user(
    username,
    password
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT username, password_hash
        FROM users
        WHERE username = %s;
        """,
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        return None

    stored_username = user[0]
    password_hash = user[1]

    if password_hash is None:
        return None

    if not verify_password(
        password,
        password_hash
    ):
        return None

    return stored_username
def get_current_username(
    credentials: HTTPAuthorizationCredentials
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return username

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )