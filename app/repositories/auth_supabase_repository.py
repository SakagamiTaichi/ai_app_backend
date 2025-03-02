from datetime import datetime
import uuid
from typing import Optional

from supabase import Client
import bcrypt

from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import UserCreate, UserResponse


class AuthSupabaseRepository(AuthRepository):
    """Supabaseを使用した認証リポジトリの実装"""
    
    def __init__(self, client: Client):
        self.client = client
        self.table_name = "users"  # Supabaseのテーブル名
    
    async def create_user(self, user: UserCreate) -> UserResponse:
        """新規ユーザーを作成する"""
        # パスワードをハッシュ化
        hashed_password = self._hash_password(user.password)
        
        # ユーザーデータの作成
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        user_data = {
            "id": user_id,
            "email": user.email,
            "username": user.username,
            "password_hash": hashed_password,
            "created_at": now,
            "updated_at": now
        }
        
        # データを挿入
        response = self.client.table(self.table_name).insert(user_data).execute()
        
        if not response.data:
            raise Exception("Failed to create user")
        
        # UserResponseオブジェクトに変換して返す
        return UserResponse(
            id=user_id,
            email=user.email,
            username=user.username,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now)
        )
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """メールアドレスからユーザーを取得する"""
        response = self.client.table(self.table_name) \
            .select("*") \
            .eq("email", email) \
            .execute()
        
        if not response.data:
            return None
        
        user_data = response.data[0]
        return UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(user_data["updated_at"].replace('Z', '+00:00'))
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """IDからユーザーを取得する"""
        response = self.client.table(self.table_name) \
            .select("*") \
            .eq("id", user_id) \
            .execute()
        
        if not response.data:
            return None
        
        user_data = response.data[0]
        return UserResponse(
            id=user_data["id"],
            email=user_data["email"],
            username=user_data["username"],
            created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(user_data["updated_at"].replace('Z', '+00:00'))
        )
    
    async def verify_password(self, email: str, password: str) -> bool:
        """パスワードを検証する"""
        response = self.client.table(self.table_name) \
            .select("password_hash") \
            .eq("email", email) \
            .execute()
        
        if not response.data:
            return False
        
        stored_hash = response.data[0]["password_hash"]
        return self._verify_password(password, stored_hash)
    
    def _hash_password(self, password: str) -> str:
        """パスワードをハッシュ化する"""
        # パスワードをバイト列に変換
        password_bytes = password.encode('utf-8')
        # ソルトを生成
        salt = bcrypt.gensalt()
        # パスワードをハッシュ化
        hashed = bcrypt.hashpw(password_bytes, salt)
        # バイト列を文字列に変換して返す
        return hashed.decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証する"""
        # パスワードとハッシュをバイト列に変換
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        # パスワードを検証
        return bcrypt.checkpw(password_bytes, hashed_bytes)