#!/usr/bin/env python3
"""
AWS CLI自動設定スクリプト
S3バケット作成、IAMユーザー作成、ポリシー設定をCLIで自動化
"""

import os
import json
import subprocess
import sys
from dotenv import load_dotenv
import uuid

class AWSCLISetup:
    def __init__(self):
        self.bucket_name = None
        self.region = "ap-northeast-1"
        self.user_name = "musepose-user"
        self.policy_name = "MusePoseS3Policy"
        self.account_id = None

    def check_aws_cli(self):
        """AWS CLIがインストールされているかチェック"""
        try:
            result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
            print(f"✅ AWS CLI確認: {result.stdout.strip()}")
            return True
        except FileNotFoundError:
            print("❌ AWS CLIがインストールされていません")
            print("📥 インストール方法:")
            print("   macOS: brew install awscli")
            print("   Linux: pip install awscli")
            print("   Windows: https://aws.amazon.com/cli/")
            return False

    def check_aws_credentials(self):
        """AWS認証情報をチェック"""
        try:
            result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                                   capture_output=True, text=True, check=True)
            identity = json.loads(result.stdout)
            self.account_id = identity['Account']
            print(f"✅ AWS認証確認: {identity['Arn']}")
            print(f"📋 アカウントID: {self.account_id}")
            return True
        except subprocess.CalledProcessError:
            print("❌ AWS認証に失敗しました")
            print("🔧 設定方法:")
            print("   aws configure")
            print("   または環境変数を設定:")
            print("   export AWS_ACCESS_KEY_ID=your_key")
            print("   export AWS_SECRET_ACCESS_KEY=your_secret")
            return False

    def create_s3_bucket(self):
        """S3バケットを作成"""
        print(f"\n📦 S3バケット '{self.bucket_name}' を作成中...")
        
        try:
            # バケットが既に存在するかチェック
            subprocess.run(['aws', 's3', 'ls', f's3://{self.bucket_name}'], 
                          capture_output=True, check=True)
            print(f"⚠️ バケット '{self.bucket_name}' は既に存在します")
            return True
        except subprocess.CalledProcessError:
            pass  # バケットが存在しない場合は新規作成

        try:
            # バケットを作成
            if self.region == 'us-east-1':
                # us-east-1の場合はLocationConstraintを指定しない
                subprocess.run(['aws', 's3', 'mb', f's3://{self.bucket_name}'], 
                              check=True)
            else:
                subprocess.run(['aws', 's3', 'mb', f's3://{self.bucket_name}', 
                              '--region', self.region], check=True)
            
            print("✅ S3バケット作成完了")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ バケット作成失敗: {e}")
            return False

    def setup_bucket_policy(self):
        """バケットポリシーを設定"""
        print("\n🔒 バケットポリシーを設定中...")
        
        # バケットポリシーを作成
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }
            ]
        }
        
        # 一時ファイルに保存
        policy_file = f"/tmp/bucket-policy-{uuid.uuid4()}.json"
        with open(policy_file, 'w') as f:
            json.dump(policy, f, indent=2)
        
        try:
            # パブリックアクセスブロックを解除
            subprocess.run([
                'aws', 's3api', 'delete-public-access-block',
                '--bucket', self.bucket_name
            ], check=True)
            
            # ポリシーを適用
            subprocess.run([
                'aws', 's3api', 'put-bucket-policy',
                '--bucket', self.bucket_name,
                '--policy', f'file://{policy_file}'
            ], check=True)
            
            print("✅ バケットポリシー設定完了")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ポリシー設定失敗: {e}")
            return False
        finally:
            # 一時ファイルを削除
            if os.path.exists(policy_file):
                os.remove(policy_file)

    def create_iam_user(self):
        """IAMユーザーを作成"""
        print(f"\n👤 IAMユーザー '{self.user_name}' を作成中...")
        
        try:
            # ユーザーが既に存在するかチェック
            subprocess.run(['aws', 'iam', 'get-user', '--user-name', self.user_name], 
                          capture_output=True, check=True)
            print(f"⚠️ ユーザー '{self.user_name}' は既に存在します")
        except subprocess.CalledProcessError:
            # ユーザーが存在しない場合は新規作成
            try:
                subprocess.run(['aws', 'iam', 'create-user', '--user-name', self.user_name], 
                              check=True)
                print("✅ IAMユーザー作成完了")
            except subprocess.CalledProcessError as e:
                print(f"❌ ユーザー作成失敗: {e}")
                return False
        
        return True

    def create_iam_policy(self):
        """IAMポリシーを作成"""
        print(f"\n🔐 IAMポリシー '{self.policy_name}' を作成中...")
        
        # ポリシードキュメントを作成
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket",
                        "s3:HeadBucket"
                    ],
                    "Resource": f"arn:aws:s3:::{self.bucket_name}"
                }
            ]
        }
        
        # 一時ファイルに保存
        policy_file = f"/tmp/iam-policy-{uuid.uuid4()}.json"
        with open(policy_file, 'w') as f:
            json.dump(policy_document, f, indent=2)
        
        try:
            # ポリシーが既に存在するかチェック
            policy_arn = f"arn:aws:iam::{self.account_id}:policy/{self.policy_name}"
            subprocess.run(['aws', 'iam', 'get-policy', '--policy-arn', policy_arn], 
                          capture_output=True, check=True)
            print(f"⚠️ ポリシー '{self.policy_name}' は既に存在します")
        except subprocess.CalledProcessError:
            # ポリシーが存在しない場合は新規作成
            try:
                subprocess.run([
                    'aws', 'iam', 'create-policy',
                    '--policy-name', self.policy_name,
                    '--policy-document', f'file://{policy_file}'
                ], check=True)
                print("✅ IAMポリシー作成完了")
            except subprocess.CalledProcessError as e:
                print(f"❌ ポリシー作成失敗: {e}")
                return False
        
        # ポリシーをユーザーにアタッチ
        try:
            policy_arn = f"arn:aws:iam::{self.account_id}:policy/{self.policy_name}"
            subprocess.run([
                'aws', 'iam', 'attach-user-policy',
                '--user-name', self.user_name,
                '--policy-arn', policy_arn
            ], check=True)
            print("✅ ポリシーアタッチ完了")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ポリシーアタッチ失敗: {e}")
            return False
        finally:
            # 一時ファイルを削除
            if os.path.exists(policy_file):
                os.remove(policy_file)

    def create_access_key(self):
        """アクセスキーを作成"""
        print("\n🔑 アクセスキーを作成中...")
        
        try:
            # 既存のアクセスキーをチェック
            result = subprocess.run([
                'aws', 'iam', 'list-access-keys',
                '--user-name', self.user_name
            ], capture_output=True, text=True, check=True)
            
            keys = json.loads(result.stdout)
            if keys['AccessKeyMetadata']:
                print("⚠️ アクセスキーが既に存在します")
                for key in keys['AccessKeyMetadata']:
                    if key['Status'] == 'Active':
                        print(f"   アクティブなキー: {key['AccessKeyId']}")
                
                use_existing = input("既存のキーを使用しますか？ (y/N): ")
                if use_existing.lower() == 'y':
                    access_key_id = keys['AccessKeyMetadata'][0]['AccessKeyId']
                    secret_key = input("🔐 Secret Access Keyを入力してください: ")
                    return access_key_id, secret_key
                else:
                    print("新しいアクセスキーを作成します...")
            
            # 新しいアクセスキーを作成
            result = subprocess.run([
                'aws', 'iam', 'create-access-key',
                '--user-name', self.user_name
            ], capture_output=True, text=True, check=True)
            
            key_info = json.loads(result.stdout)
            access_key = key_info['AccessKey']
            
            print("✅ アクセスキー作成完了")
            print(f"🔑 Access Key ID: {access_key['AccessKeyId']}")
            print(f"🔐 Secret Access Key: {access_key['SecretAccessKey']}")
            print("⚠️ 重要: Secret Access Keyは二度と表示されません！")
            
            return access_key['AccessKeyId'], access_key['SecretAccessKey']
            
        except subprocess.CalledProcessError as e:
            print(f"❌ アクセスキー作成失敗: {e}")
            return None, None

    def create_env_file(self, access_key_id, secret_access_key):
        """環境変数ファイルを作成"""
        print("\n📝 .envファイルを作成中...")
        
        # Replicate APIトークンを取得
        replicate_token = input("🤖 Replicate APIトークンを入力してください: ").strip()
        
        env_content = f"""# AWS設定
AWS_ACCESS_KEY_ID={access_key_id}
AWS_SECRET_ACCESS_KEY={secret_access_key}
S3_BUCKET_NAME={self.bucket_name}
AWS_REGION={self.region}

# Replicate API設定
REPLICATE_API_TOKEN={replicate_token}
"""
        
        # 既存の.envファイルをバックアップ
        if os.path.exists('.env'):
            backup_file = f'.env.backup.{uuid.uuid4().hex[:8]}'
            os.rename('.env', backup_file)
            print(f"📄 既存の.envファイルを {backup_file} にバックアップしました")
        
        # 新しい.envファイルを作成
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .envファイル作成完了")

    def test_configuration(self):
        """設定をテスト"""
        print("\n🧪 設定テスト中...")
        
        load_dotenv()
        
        try:
            # .envファイルから設定を読み込み
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION')
            )
            
            # バケットへのアクセステスト
            bucket_name = os.getenv('S3_BUCKET_NAME')
            s3_client.head_bucket(Bucket=bucket_name)
            
            # テストファイルをアップロード
            test_content = "MusePose Test File"
            s3_client.put_object(
                Bucket=bucket_name,
                Key='test/test.txt',
                Body=test_content.encode(),
                ContentType='text/plain'
            )
            
            # テストファイルを削除
            s3_client.delete_object(Bucket=bucket_name, Key='test/test.txt')
            
            print("✅ S3設定テスト成功！")
            return True
            
        except Exception as e:
            print(f"❌ 設定テスト失敗: {e}")
            return False

    def setup(self):
        """メインのセットアップ処理"""
        print("🚀 AWS CLI自動設定を開始します")
        print("="*50)
        
        # 前提条件チェック
        if not self.check_aws_cli():
            return False
        
        if not self.check_aws_credentials():
            return False
        
        # 設定情報を取得
        print("\n📝 設定情報を入力してください:")
        self.bucket_name = input("📦 S3バケット名: ").strip()
        self.region = input(f"🌏 リージョン (デフォルト: {self.region}): ").strip() or self.region
        
        # 確認
        print(f"\n📋 設定内容:")
        print(f"   バケット名: {self.bucket_name}")
        print(f"   リージョン: {self.region}")
        print(f"   IAMユーザー: {self.user_name}")
        
        confirm = input("\n続行しますか？ (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 処理を中止しました")
            return False
        
        # AWS リソースを作成
        steps = [
            ("S3バケット作成", self.create_s3_bucket),
            ("バケットポリシー設定", self.setup_bucket_policy),
            ("IAMユーザー作成", self.create_iam_user),
            ("IAMポリシー作成", self.create_iam_policy),
        ]
        
        for step_name, step_func in steps:
            print(f"\n⏳ {step_name}中...")
            if not step_func():
                print(f"❌ {step_name}に失敗しました")
                return False
        
        # アクセスキーを作成
        access_key_id, secret_access_key = self.create_access_key()
        if not access_key_id:
            return False
        
        # .envファイルを作成
        self.create_env_file(access_key_id, secret_access_key)
        
        # 設定をテスト
        if self.test_configuration():
            print("\n🎉 AWS設定が完了しました！")
            print("🚀 アプリケーションを起動できます:")
            print("   streamlit run app.py")
            return True
        else:
            print("\n⚠️ 設定は完了しましたが、テストに失敗しました")
            print("手動で設定を確認してください")
            return False

def main():
    """メイン関数"""
    setup = AWSCLISetup()
    setup.setup()

if __name__ == "__main__":
    main() 