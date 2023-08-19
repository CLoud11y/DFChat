from pydantic import BaseModel
from database import User
from fastapi import APIRouter, HTTPException
import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

user_router = APIRouter()

# 用户注册请求体模型
class UserSignupRequest(BaseModel):
    username: str
    password: str
    email: str

# 用户登录请求体模型
class UserLoginRequest(BaseModel):
    username: str
    password: str

# 用户信息响应体模型
class UserInfoResponse(BaseModel):
    username: str
    email: str

def create_access_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 用户登录API
@user_router.post("/login")
async def login(user_login_request: UserLoginRequest):
    user = User.get_user_by_user_name(user_login_request.username)
    if user and user.password == user_login_request.password:
        access_token = create_access_token(data={"sub": user.username}, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)
        return {"access_token": access_token}
    else:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
# 用户注册API
@user_router.post("/signup")
async def signup(user_signup_request: UserSignupRequest):
    user_check = User.get_user_by_user_name(user_signup_request.username)
    if user_check is None:
        user = User.create_user(user_signup_request.username, user_signup_request.password, user_signup_request.email)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)
        return {"access_token": access_token}
    else:
        raise HTTPException(status_code=400, detail="用户名已存在")

# 获取用户信息API
@user_router.get("/users/{username}")
async def get_user_info(username: str):
    user = User.get_user_by_user_name(username)
    if user:
        return UserInfoResponse(username=user.username, email=user.email)
    else:
        raise HTTPException(status_code=404, detail="用户不存在")

