from pydantic import BaseModel, Field

class LoginInformationValueObject(BaseModel):
    """認証トークン用のスキーマ"""
    email: str = Field(
        ..., 
        description="メールアドレス",
        min_length=5,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    password: str = Field(
        ..., 
        description="パスワード",
        min_length=8,
        max_length=128,
        # pattern=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$"
    )