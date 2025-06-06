#!/usr/bin/env python3
"""
AWS設定自動化スクリプト（Playwright使用）
S3バケット作成、IAMユーザー作成、ポリシー設定を自動化
"""

import asyncio
import json
import os
import time
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class AWSSetupAutomation:
    def __init__(self):
        self.aws_email = None
        self.aws_password = None
        self.bucket_name = None
        self.region = "us-east-1"
        self.iam_username = "musepose-user"
        
    async def setup_aws_resources(self, aws_email: str, aws_password: str, bucket_name: str, region: str = "us-east-1"):
        """AWS リソースの自動セットアップ"""
        self.aws_email = aws_email
        self.aws_password = aws_password
        self.bucket_name = bucket_name
        self.region = region
        
        async with async_playwright() as p:
            # ブラウザを起動
            browser = await p.chromium.launch(headless=False, slow_mo=1000)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            try:
                # AWS Management Consoleにログイン
                await self.login_to_aws(page)
                
                # S3バケットを作成
                bucket_created = await self.create_s3_bucket(page)
                
                # IAMユーザーを作成
                access_key, secret_key = await self.create_iam_user(page)
                
                # バケットポリシーを設定
                await self.setup_bucket_policy(page)
                
                # 結果を表示
                await self.display_results(access_key, secret_key)
                
                return {
                    'success': True,
                    'bucket_name': self.bucket_name,
                    'region': self.region,
                    'access_key': access_key,
                    'secret_key': secret_key
                }
                
            except Exception as e:
                print(f"❌ エラーが発生しました: {str(e)}")
                return {'success': False, 'error': str(e)}
            
            finally:
                await browser.close()
    
    async def login_to_aws(self, page):
        """AWS Management Consoleにログイン"""
        print("🔐 AWS Management Consoleにログイン中...")
        
        # AWS Console にアクセス
        await page.goto("https://console.aws.amazon.com/")
        await page.wait_for_load_state('networkidle')
        
        try:
            # ルートユーザーでサインインを選択
            try:
                await page.wait_for_selector('text=Root user', timeout=10000)
                await page.click('text=Root user')
                print("✅ ルートユーザーを選択")
            except:
                print("⚠️ ルートユーザー選択をスキップ（既に選択済みの可能性）")
            
            # メール入力フィールドを探す
            email_selectors = [
                'input[name="username"]',
                'input[id="username"]', 
                'input[id="resolving_input"]',
                'input[type="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]',
                'input[aria-label*="email" i]',
                'input[data-testid="username"]',
                'input[autocomplete="username"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    email_input = selector
                    print(f"✅ メール入力フィールド発見: {selector}")
                    break
                except:
                    continue
            
            if not email_input:
                # ページ内容をデバッグ出力
                print("🔍 利用可能な入力フィールドを検索中...")
                inputs = await page.query_selector_all('input')
                for i, inp in enumerate(inputs):
                    attrs = await inp.evaluate('el => ({name: el.name, id: el.id, type: el.type, placeholder: el.placeholder, autocomplete: el.autocomplete})')
                    print(f"  Input {i}: {attrs}")
                
                # 最初のテキスト入力フィールドを使用
                first_text_input = await page.query_selector('input[type="text"], input[type="email"]')
                if first_text_input:
                    email_input = 'input[type="text"], input[type="email"]'
                    print("⚠️ 最初のテキスト入力フィールドを使用")
                else:
                    raise Exception("メール入力フィールドが見つかりません")
            
            # メールアドレスを入力
            await page.fill(email_input, self.aws_email)
            print("✅ メールアドレス入力完了")
            
            # Next/Continue/Sign Inボタンを探してクリック
            button_selectors = [
                'button[type="submit"]',
                'button:has-text("Next")',
                'button:has-text("Continue")',
                'button:has-text("Sign")',
                'input[type="submit"]',
                '[data-testid="signin-continue-button"]',
                'button[id="next_button"]'
            ]
            
            button_clicked = False
            for selector in button_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    button_clicked = True
                    print(f"✅ ボタンクリック成功: {selector}")
                    break
                except:
                    continue
            
            if not button_clicked:
                print("⚠️ Nextボタンが見つかりません。Enterキーを試行します...")
                await page.press(email_input, 'Enter')
            
            # パスワード入力画面を待機
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)  # 追加の待機時間
            
            # パスワード入力フィールドを探す
            password_selectors = [
                'input[name="password"]',
                'input[id="password"]',
                'input[type="password"]',
                'input[placeholder*="password" i]',
                'input[aria-label*="password" i]',
                'input[data-testid="password"]',
                'input[autocomplete="current-password"]'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=10000)
                    password_input = selector
                    print(f"✅ パスワード入力フィールド発見: {selector}")
                    break
                except:
                    continue
            
            if not password_input:
                print("🔍 パスワードフィールドを再検索中...")
                inputs = await page.query_selector_all('input')
                for i, inp in enumerate(inputs):
                    attrs = await inp.evaluate('el => ({name: el.name, id: el.id, type: el.type, placeholder: el.placeholder})')
                    print(f"  Input {i}: {attrs}")
                raise Exception("パスワード入力フィールドが見つかりません")
            
            # パスワードを入力
            await page.fill(password_input, self.aws_password)
            print("✅ パスワード入力完了")
            
            # サインインボタンをクリック
            signin_selectors = [
                'button[type="submit"]',
                'button:has-text("Sign")',
                'input[type="submit"]',
                '[data-testid="signin-submit-button"]',
                'button[id="signin_button"]'
            ]
            
            signin_clicked = False
            for selector in signin_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    signin_clicked = True
                    print(f"✅ サインインボタンクリック成功: {selector}")
                    break
                except:
                    continue
            
            if not signin_clicked:
                print("⚠️ サインインボタンが見つかりません。Enterキーを試行します...")
                await page.press(password_input, 'Enter')
            
            # ダッシュボードの読み込みを待機（複数のパターンを許可）
            print("🔄 ダッシュボードの読み込みを待機中...")
            dashboard_selectors = [
                'text=AWS Management Console',
                'text=Console Home',
                '[data-testid="console-nav"]',
                '.awsui-context-content-header',
                '#consoleNavPanel',
                '[data-testid="awsc-nav-header"]',
                '.awsui-app-layout'
            ]
            
            dashboard_loaded = False
            for selector in dashboard_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=30000)
                    dashboard_loaded = True
                    print(f"✅ ダッシュボード読み込み完了: {selector}")
                    break
                except:
                    continue
            
            if not dashboard_loaded:
                # MFAやその他の認証が必要な場合
                print("⚠️ 追加認証が必要な可能性があります。手動で認証を完了してください...")
                print("⏰ 60秒待機します...")
                await page.wait_for_timeout(60000)
                
                # 再度ダッシュボードの確認
                for selector in dashboard_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        dashboard_loaded = True
                        print(f"✅ 認証後ダッシュボード確認: {selector}")
                        break
                    except:
                        continue
            
            if dashboard_loaded:
                print("✅ ログイン成功")
            else:
                print("⚠️ ダッシュボードの確認ができませんが、処理を続行します")
            
        except Exception as e:
            print(f"❌ ログインエラー: {str(e)}")
            
            # 現在のページ情報を出力
            current_url = page.url
            title = await page.title()
            print(f"現在のURL: {current_url}")
            print(f"ページタイトル: {title}")
            
            # スクリーンショットを保存（デバッグ用）
            await page.screenshot(path="debug_login_error.png")
            print("デバッグ用スクリーンショットを保存しました: debug_login_error.png")
            
            raise e
    
    async def create_s3_bucket(self, page):
        """S3バケットを作成"""
        print(f"📦 S3バケット '{self.bucket_name}' を作成中...")
        
        # S3サービスに移動
        await page.goto("https://s3.console.aws.amazon.com/s3/")
        
        # バケット作成ボタンをクリック
        await page.wait_for_selector('text=Create bucket')
        await page.click('text=Create bucket')
        
        # バケット名を入力
        await page.wait_for_selector('input[name="bucketName"]')
        await page.fill('input[name="bucketName"]', self.bucket_name)
        
        # リージョンを選択
        if self.region != "us-east-1":
            await page.click('select[name="region"]')
            await page.select_option('select[name="region"]', self.region)
        
        # パブリックアクセス設定を変更
        await page.uncheck('input[name="blockPublicAcls"]')
        await page.uncheck('input[name="blockPublicPolicy"]')
        await page.uncheck('input[name="ignorePublicAcls"]')
        await page.uncheck('input[name="restrictPublicBuckets"]')
        
        # 確認チェックボックス
        await page.check('input[name="confirmBucketNotPublic"]')
        
        # バケットを作成
        await page.click('button[type="submit"]')
        
        # 作成完了を待機
        await page.wait_for_selector(f'text={self.bucket_name}', timeout=30000)
        print("✅ S3バケット作成完了")
        return True
    
    async def create_iam_user(self, page):
        """IAMユーザーを作成してアクセスキーを取得"""
        print(f"👤 IAMユーザー '{self.iam_username}' を作成中...")
        
        # IAMサービスに移動
        await page.goto("https://console.aws.amazon.com/iam/")
        
        # ユーザーセクションに移動
        await page.click('text=Users')
        
        # ユーザー作成ボタンをクリック
        await page.click('text=Create user')
        
        # ユーザー名を入力
        await page.fill('input[name="userName"]', self.iam_username)
        
        # プログラムによるアクセスを選択
        await page.check('input[value="programmatic-access"]')
        
        # 次へ
        await page.click('text=Next')
        
        # ポリシーを直接アタッチ
        await page.click('text=Attach policies directly')
        
        # S3FullAccessポリシーを検索して選択
        await page.fill('input[placeholder="Search"]', 'AmazonS3FullAccess')
        await page.check('input[value="arn:aws:iam::aws:policy/AmazonS3FullAccess"]')
        
        # 次へ
        await page.click('text=Next')
        
        # レビューして作成
        await page.click('text=Create user')
        
        # アクセスキーとシークレットキーを取得
        access_key = await page.text_content('[data-testid="access-key-id"]')
        secret_key = await page.text_content('[data-testid="secret-access-key"]')
        
        print("✅ IAMユーザー作成完了")
        return access_key, secret_key
    
    async def setup_bucket_policy(self, page):
        """S3バケットポリシーを設定"""
        print("🔒 バケットポリシーを設定中...")
        
        # S3バケットの詳細ページに移動
        await page.goto(f"https://s3.console.aws.amazon.com/s3/buckets/{self.bucket_name}")
        
        # Permissionsタブをクリック
        await page.click('text=Permissions')
        
        # Bucket policyセクションを編集
        await page.click('text=Edit', selector='[data-testid="bucket-policy"] button')
        
        # バケットポリシーを設定
        bucket_policy = {
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
        
        await page.fill('textarea[name="policyDocument"]', json.dumps(bucket_policy, indent=2))
        
        # 保存
        await page.click('text=Save changes')
        
        print("✅ バケットポリシー設定完了")
    
    async def display_results(self, access_key: str, secret_key: str):
        """設定結果を表示"""
        print("\n" + "="*60)
        print("🎉 AWS設定が完了しました！")
        print("="*60)
        print(f"📦 S3バケット名: {self.bucket_name}")
        print(f"🌏 リージョン: {self.region}")
        print(f"🔑 アクセスキーID: {access_key}")
        print(f"🔐 シークレットアクセスキー: {secret_key}")
        print("\n📝 .envファイルに以下を追加してください:")
        print("-"*40)
        print(f"AWS_ACCESS_KEY_ID={access_key}")
        print(f"AWS_SECRET_ACCESS_KEY={secret_key}")
        print(f"S3_BUCKET_NAME={self.bucket_name}")
        print(f"AWS_REGION={self.region}")
        print("="*60)

async def main():
    """メイン関数"""
    print("🚀 AWS設定自動化スクリプトを開始します")
    print("="*50)
    
    # ユーザー入力を取得
    aws_email = input("📧 AWSアカウントのメールアドレス: ")
    aws_password = input("🔒 AWSアカウントのパスワード: ")
    bucket_name = input("📦 作成するS3バケット名: ")
    region = input("🌏 リージョン (デフォルト: us-east-1): ") or "us-east-1"
    
    # 確認
    print(f"\n📋 設定内容:")
    print(f"   メール: {aws_email}")
    print(f"   バケット名: {bucket_name}")
    print(f"   リージョン: {region}")
    
    confirm = input("\n続行しますか？ (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 処理を中止しました")
        return
    
    # 自動化を実行
    automation = AWSSetupAutomation()
    result = await automation.setup_aws_resources(aws_email, aws_password, bucket_name, region)
    
    if result['success']:
        print("\n✅ すべての設定が完了しました！")
        
        # .envファイルを自動更新
        env_content = f"""
# AWS設定
AWS_ACCESS_KEY_ID={result['access_key']}
AWS_SECRET_ACCESS_KEY={result['secret_key']}
S3_BUCKET_NAME={result['bucket_name']}
AWS_REGION={result['region']}

# Replicate API設定
REPLICATE_API_TOKEN=your_replicate_token_here
"""
        
        with open('.env', 'w') as f:
            f.write(env_content.strip())
        
        print("📝 .envファイルを自動更新しました")
        print("🔑 Replicate APIトークンを手動で設定してください")
        
    else:
        print(f"❌ 設定に失敗しました: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main()) 