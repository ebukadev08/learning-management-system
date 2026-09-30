"""
get_current_user: reads the JWT from the Authorization header,
verifies it, and fetches the matching User.

We use HTTPBearer instead of OAuth2PasswordBearer because our login
endpoint takes JSON (email/password), not the OAuth2 form-data spec
that OAuth2PasswordBearer's Swagger "Authorize" button expects.
HTTPBearer just gives Swagger a plain "paste your token here" box.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_access_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def require_instructor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.instructor, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can perform this action.",
        )
    return current_user







# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.models.user import User
# from app.utils.security import decode_access_token
# from app.models.user import UserRole

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# def get_current_user(
#         token: str = Depends(oauth2_scheme),
#         db: Session = Depends(get_db),
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         payload = decode_access_token(token)
#         user_id = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     user = db.query(User).filter(User.id == int(user_id)).first()
#     if user is None:
#         raise credentials_exception

#     return user

# def require_instructor(current_user: User = Depends(get_current_user)) -> User:

#     if current_user.role not in (UserRole.instructor, UserRole.admin):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Only instructors can perform this action."
#         )

#     return current_user