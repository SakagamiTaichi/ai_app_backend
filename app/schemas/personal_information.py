from __future__ import annotations 
# from_db_dictにおける戻り値の型ヒントのPersonalInformationResponseの前方参照を許可するための記述
from typing import Any, Dict, Optional
from pydantic import BaseModel

class PersonalInformation(BaseModel):
    id: Optional[int]
    name: Optional[str]
    name_kana: Optional[str]
    sex: Optional[str]
    phone_number: Optional[int]  # strからintに変更
    mail: Optional[str]
    postcode: Optional[str]     # postcordからpostcodeに修正
    address: Optional[str]
    birthday: Optional[str]
    age: Optional[int]
    blood_type: Optional[str]

    @classmethod
    def from_db_dict(cls, db_dict: Dict[str, Any]) -> PersonalInformation:
        """
        データベースの結果辞書からモデルを作成
        存在しないフィールドは自動的にNoneとして扱われる
        """
        model_fields = cls.model_fields.keys()
        # 辞書内包表記
        filtered_dict = {
            field: db_dict.get(field)
            for field in model_fields
            if field in db_dict
        }
        return cls(**filtered_dict)
