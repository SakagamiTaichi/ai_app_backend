from app.domain.email.emai_repository import EmailRepository
import resend
from app.core.config import settings


class EmailResendRepository(EmailRepository):
    """EmailRepositoryの実装クラス"""

    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    async def send_verification_code(self, email: str, code: str) -> bool:
        """認証コードを生成してメールで送信する"""
        try:
            # メールで送信
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">認証コードのお知らせ</h2>
                        <p>こんにちは。</p>
                        <p>以下の認証コードを使用してサインインを完了してください：</p>
                        <div style="background-color: #f4f4f4; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h1 style="text-align: center; color: #3498db; letter-spacing: 5px; margin: 0;">{code}</h1>
                        </div>
                        <p>この認証コードは{settings.VERIFICATION_CODE_EXPIRE_MINUTES}分間有効です。</p>
                        <p>このメールに心当たりがない場合は、無視してください。</p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="font-size: 12px; color: #999;">
                            このメールは自動送信されています。返信は受け付けておりません。
                        </p>
                    </div>
                </body>
            </html>
            """

            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [email],
                "subject": "【EIGOAT】認証コード",
                "html": html_content,
            }

            result = resend.Emails.send(params)  # type: ignore
            return result.get("id") is not None

        except Exception as e:
            raise
