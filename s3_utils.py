import os
import boto3
import uuid
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional

logger = logging.getLogger(__name__)

class S3Manager:
    """AWS S3ファイル管理クラス"""
    
    def __init__(self):
        """S3クライアントを初期化"""
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.region = os.getenv('AWS_REGION', 'ap-northeast-1')  # デフォルトは東京リージョン
        
        try:
            # AWS認証情報の確認
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            
            # バケットの存在確認
            if self.bucket_name:
                self._verify_bucket_access()
            else:
                logger.warning("S3_BUCKET_NAME環境変数が設定されていません")
                
        except NoCredentialsError:
            logger.error("AWS認証情報が設定されていません")
            self.s3_client = None
        except Exception as e:
            logger.error(f"S3クライアントの初期化エラー: {e}")
            self.s3_client = None
    
    def _verify_bucket_access(self) -> bool:
        """バケットへのアクセス権限を確認"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3バケット '{self.bucket_name}' へのアクセスを確認しました")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"S3バケット '{self.bucket_name}' が見つかりません")
            elif error_code == '403':
                logger.error(f"S3バケット '{self.bucket_name}' へのアクセス権限がありません")
            else:
                logger.error(f"S3バケットアクセスエラー: {e}")
            return False
    
    def is_configured(self) -> bool:
        """S3が正しく設定されているかチェック"""
        return (
            self.s3_client is not None and 
            self.bucket_name is not None and 
            os.getenv('AWS_ACCESS_KEY_ID') is not None and 
            os.getenv('AWS_SECRET_ACCESS_KEY') is not None
        )
    
    def upload_file(self, file_path: str, object_name: Optional[str] = None, 
                   content_type: Optional[str] = None) -> Optional[str]:
        """
        ファイルをS3にアップロード
        
        Args:
            file_path: アップロードするローカルファイルのパス
            object_name: S3オブジェクト名（指定しない場合はUUIDを生成）
            content_type: ファイルのMIMEタイプ
            
        Returns:
            アップロードされたファイルのURL、失敗時はNone
        """
        if not self.is_configured():
            logger.error("S3が正しく設定されていません")
            return None
        
        if not os.path.exists(file_path):
            logger.error(f"ファイルが見つかりません: {file_path}")
            return None
        
        # オブジェクト名を生成
        if object_name is None:
            file_extension = os.path.splitext(file_path)[1]
            object_name = f"uploads/{uuid.uuid4()}{file_extension}"
        
        # Content-Typeを自動判定
        if content_type is None:
            content_type = self._get_content_type(file_path)
        
        try:
            # ファイルをアップロード（ACLは使用しない）
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                object_name,
                ExtraArgs=extra_args if extra_args else None
            )
            
            # パブリックURLを生成
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_name}"
            logger.info(f"ファイルをS3にアップロードしました: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"S3アップロードエラー: {e}")
            return None
    
    def upload_video(self, video_path: str) -> Optional[str]:
        """動画ファイルをS3にアップロード"""
        return self.upload_file(
            video_path, 
            content_type='video/mp4'
        )
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """画像ファイルをS3にアップロード"""
        content_type = self._get_content_type(image_path)
        return self.upload_file(
            image_path,
            content_type=content_type
        )
    
    def _get_content_type(self, file_path: str) -> str:
        """ファイル拡張子からContent-Typeを判定"""
        extension = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp'
        }
        
        return content_types.get(extension, 'application/octet-stream')
    
    def delete_file(self, object_name: str) -> bool:
        """S3からファイルを削除"""
        if not self.is_configured():
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            logger.info(f"S3からファイルを削除しました: {object_name}")
            return True
        except ClientError as e:
            logger.error(f"S3削除エラー: {e}")
            return False
    
    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> Optional[str]:
        """
        署名付きURLを生成（一時的なアクセス用）
        
        Args:
            object_name: S3オブジェクト名
            expiration: URL有効期限（秒）
            
        Returns:
            署名付きURL、失敗時はNone
        """
        if not self.is_configured():
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"署名付きURL生成エラー: {e}")
            return None

# グローバルインスタンス
s3_manager = S3Manager() 