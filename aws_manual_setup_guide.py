#!/usr/bin/env python3
"""
AWS手動設定ガイド & .env自動生成スクリプト
"""

import os
from dotenv import load_dotenv

def print_aws_setup_guide():
    """AWS設定の詳細ガイドを表示"""
    print("🚀 AWS S3 & IAM 手動設定ガイド")
    print("="*60)
    
    print("\n📋 ステップ1: AWSアカウントにログイン")
    print("-"*40)
    print("1. https://console.aws.amazon.com/ にアクセス")
    print("2. ルートユーザーでサインイン")
    print("3. メールアドレスとパスワードを入力")
    print("4. MFA認証（設定している場合）")
    
    print("\n📦 ステップ2: S3バケットの作成")
    print("-"*40)
    print("1. AWSコンソールで「S3」を検索してアクセス")
    print("2. 「バケットを作成」をクリック")
    print("3. バケット名を入力（例: musepose-storage-yourname）")
    print("4. リージョンを選択（推奨: ap-northeast-1）")
    print("5. 「パブリックアクセスをブロック」の設定:")
    print("   ✅ すべてのチェックを外す")
    print("   ✅ 「現在の設定により、このバケットとその中のオブジェクトが公開される可能性があることを承認します」にチェック")
    print("6. 「バケットを作成」をクリック")
    
    print("\n🔒 ステップ3: バケットポリシーの設定")
    print("-"*40)
    print("1. 作成したバケットをクリック")
    print("2. 「アクセス許可」タブをクリック")
    print("3. 「バケットポリシー」セクションで「編集」をクリック")
    print("4. 以下のポリシーを貼り付け（YOUR_BUCKET_NAMEを実際のバケット名に変更）:")
    print("""
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}""")
    print("5. 「変更の保存」をクリック")
    
    print("\n👤 ステップ4: IAMユーザーの作成")
    print("-"*40)
    print("1. AWSコンソールで「IAM」を検索してアクセス")
    print("2. 左メニューから「ユーザー」をクリック")
    print("3. 「ユーザーを作成」をクリック")
    print("4. ユーザー名を入力（例: musepose-user）")
    print("5. 「次へ」をクリック")
    print("6. 「ポリシーを直接アタッチ」を選択")
    print("7. 「AmazonS3FullAccess」を検索して選択")
    print("8. 「次へ」→「ユーザーの作成」をクリック")
    
    print("\n🔑 ステップ5: アクセスキーの作成")
    print("-"*40)
    print("1. 作成したユーザーをクリック")
    print("2. 「セキュリティ認証情報」タブをクリック")
    print("3. 「アクセスキーを作成」をクリック")
    print("4. 「アプリケーション外で実行されるコード」を選択")
    print("5. 「次へ」をクリック")
    print("6. 説明タグを入力（例: MusePose App）")
    print("7. 「アクセスキーを作成」をクリック")
    print("8. ⚠️ 重要: アクセスキーIDとシークレットアクセスキーをコピー")
    print("   （この画面を閉じると二度と表示されません）")
    
    print("\n✅ 設定完了後の情報")
    print("-"*40)
    print("以下の情報を準備してください:")
    print("• S3バケット名")
    print("• リージョン")
    print("• アクセスキーID")
    print("• シークレットアクセスキー")
    print("• Replicate APIトークン")

def create_env_file():
    """対話的に.envファイルを作成"""
    print("\n🔧 .envファイル作成ウィザード")
    print("="*50)
    
    # 既存の.envファイルをチェック
    if os.path.exists('.env'):
        load_dotenv()
        print("⚠️ 既存の.envファイルが見つかりました")
        overwrite = input("上書きしますか？ (y/N): ")
        if overwrite.lower() != 'y':
            print("❌ 処理を中止しました")
            return
    
    # 設定情報を収集
    print("\n📝 設定情報を入力してください:")
    
    # AWS設定
    aws_access_key = input("🔑 AWS Access Key ID: ").strip()
    aws_secret_key = input("🔐 AWS Secret Access Key: ").strip()
    s3_bucket_name = input("📦 S3バケット名: ").strip()
    aws_region = input("🌏 AWSリージョン (デフォルト: ap-northeast-1): ").strip() or "ap-northeast-1"
    
    # Replicate設定
    replicate_token = input("🤖 Replicate APIトークン: ").strip()
    
    # 入力内容を確認
    print(f"\n📋 設定内容の確認:")
    print(f"   AWS Access Key ID: {aws_access_key[:8]}...")
    print(f"   AWS Secret Access Key: {aws_secret_key[:8]}...")
    print(f"   S3バケット名: {s3_bucket_name}")
    print(f"   AWSリージョン: {aws_region}")
    print(f"   Replicate APIトークン: {replicate_token[:8]}...")
    
    confirm = input("\n設定を保存しますか？ (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 処理を中止しました")
        return
    
    # .envファイルを作成
    env_content = f"""# AWS設定
AWS_ACCESS_KEY_ID={aws_access_key}
AWS_SECRET_ACCESS_KEY={aws_secret_key}
S3_BUCKET_NAME={s3_bucket_name}
AWS_REGION={aws_region}

# Replicate API設定
REPLICATE_API_TOKEN={replicate_token}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .envファイルを作成しました！")
    print("🚀 これでアプリケーションを起動できます:")
    print("   streamlit run app.py")

def test_aws_connection():
    """AWS接続をテスト"""
    print("\n🧪 AWS接続テスト")
    print("="*30)
    
    load_dotenv()
    
    # 環境変数をチェック
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        return False
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # S3クライアントを作成
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'ap-northeast-1')
        )
        
        # バケットの存在確認
        bucket_name = os.getenv('S3_BUCKET_NAME')
        s3_client.head_bucket(Bucket=bucket_name)
        
        print("✅ AWS S3接続成功！")
        print(f"📦 バケット '{bucket_name}' にアクセス可能")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ バケット '{bucket_name}' が見つかりません")
        elif error_code == '403':
            print("❌ アクセス権限がありません")
        else:
            print(f"❌ AWS接続エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 接続テストエラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🎬 MusePose AWS設定ヘルパー")
    print("="*40)
    
    while True:
        print("\n📋 メニュー:")
        print("1. 📖 AWS設定ガイドを表示")
        print("2. 🔧 .envファイルを作成")
        print("3. 🧪 AWS接続をテスト")
        print("4. 🚪 終了")
        
        choice = input("\n選択してください (1-4): ").strip()
        
        if choice == '1':
            print_aws_setup_guide()
        elif choice == '2':
            create_env_file()
        elif choice == '3':
            test_aws_connection()
        elif choice == '4':
            print("👋 お疲れ様でした！")
            break
        else:
            print("❌ 無効な選択です")

if __name__ == "__main__":
    main() 