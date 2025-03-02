from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import Token, TokenData, UserCreate, UserResponse


class AuthService:
    """認証サービス"""
    
    def __init__(self, repository: AuthRepository):
        self.repository = repository
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    async def register(self, user: UserCreate) -> Token:
        """新規ユーザー登録"""
        # メールアドレスが既に登録されているか確認
        existing_user = await self.repository.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # ユーザー作成
        created_user = await self.repository.create_user(user)
        
        # トークン生成
        access_token = self._create_access_token(created_user.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=created_user
        )
    
    async def login(self, email: str, password: str) -> Token:
        """ユーザーログイン"""
        # ユーザーの存在確認
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # パスワード検証
        if not await self.repository.verify_password(email, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # トークン生成
        access_token = self._create_access_token(user.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    
    async def get_current_user(self, token: str) -> UserResponse:
        """トークンからユーザー情報を取得"""
        try:
            # トークンの検証とデコード
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            exp: datetime = datetime.fromtimestamp(payload.get("exp"))
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            token_data = TokenData(user_id=user_id, exp=exp)
            
            # 有効期限の検証
            if token_data.exp and token_data.exp < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # ユーザー情報の取得
        user = await self.repository.get_user_by_id(token_data.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    def _create_access_token(self, user_id: str) -> str:
        """アクセストークンを生成"""
        expire = datetime.now() + timedelta(minutes=self.token_expire_minutes)
        to_encode = {
            "sub": user_id,  # JWTの「sub」クレームにユーザーIDを設定
            "exp": expire.timestamp()  # 有効期限
        }
        # トークン生成
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt