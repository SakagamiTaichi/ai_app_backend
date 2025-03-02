from datetime import datetime
from typing import List
from uuid import UUID

from supabase import Client

from app.repositories.english_repository import EnglishRepository
from app.schemas.english_chat import ConversationSet, Message

class EnglishSupabaseRepository(EnglishRepository):
    """SupabaseをバックエンドとしたEnglishRepositoryの実装"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def get_conversation_sets(self) -> List[ConversationSet]:
        """会話セットの一覧を取得する"""
        try:
            response= self.client.table('en_conversation_sets') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()
    
            # レスポンスから履歴リストを作成
            sets = [
                ConversationSet(
                    id=UUID(record['id']),
                    title=record['title'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                )
                for record in response.data
            ]

            return sets
        except Exception as e:
            print(f"Error fetching conversation sets: {str(e)}")
            raise
    
    async def get_messages(self, set_id: UUID) -> List[Message]:
        """特定の会話セットに属するメッセージを取得する"""
        try:
            response = self.client.table('en_messages') \
                .select('*') \
                .eq('set_id', str(set_id)) \
                .order('message_order') \
                .execute()
    
            # レスポンスからメッセージリストを作成
            messages = [
                Message(
                    set_id=UUID(record['set_id']),
                    message_order=record['message_order'],
                    speaker_number=record['speaker_number'],
                    message_en=record['message_en'],
                    message_ja=record['message_ja'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                )
                for record in response.data
            ]

            return messages
        except Exception as e:
            print(f"Error fetching messages: {str(e)}")
            raise
    
    async def create_message(self, message: Message) -> Message:
        """メッセージを作成する"""
        try:
            # Messageオブジェクトから辞書を作成
            message_data = {
                'set_id': str(message.set_id),
                'message_order': message.message_order,
                'speaker_number': message.speaker_number,
                'message_en': message.message_en,
                'message_ja': message.message_ja,
                'created_at': message.created_at.isoformat()
            }
            
            # データを挿入
            response = self.client.table('en_messages').insert(message_data).execute()
            
            if not response.data:
                raise Exception("Failed to create message")
                
            return message
        except Exception as e:
            print(f"Error creating message: {str(e)}")
            raise
    
    async def create_conversation_set(self, conversation_set: ConversationSet) -> ConversationSet:
        """会話セットを作成する"""
        try:
            # ConversationSetオブジェクトから辞書を作成
            set_data = {
                'id': str(conversation_set.id),
                'title': conversation_set.title,
                'created_at': conversation_set.created_at.isoformat()
            }
            
            # データを挿入
            response = self.client.table('en_conversation_sets').insert(set_data).execute()
            
            if not response.data:
                raise Exception("Failed to create conversation set")
                
            return conversation_set
        except Exception as e:
            print(f"Error creating conversation set: {str(e)}")
            raise