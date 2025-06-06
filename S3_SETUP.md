# AWS S3設定ガイド

このドキュメントでは、MusePoseアプリケーションでAWS S3を使用するための設定手順を説明します。

## 前提条件

- AWSアカウントを持っていること
- AWS CLIまたはAWSコンソールへのアクセス権限があること

## 1. S3バケットの作成

### AWS コンソールを使用する場合

1. [AWS S3コンソール](https://console.aws.amazon.com/s3/)にアクセス
2. 「バケットを作成」をクリック
3. バケット名を入力（例: `musepose-storage-your-name`）
4. リージョンを選択（推奨: `ap-northeast-1` 東京）
5. 「バケットを作成」をクリック

### AWS CLIを使用する場合

```bash
# バケットを作成
aws s3 mb s3://musepose-storage-your-name --region ap-northeast-1

# バケットの存在確認
aws s3 ls s3://musepose-storage-your-name
```

## 2. バケットポリシーの設定

生成された動画をパブリックに読み取り可能にするため、以下のバケットポリシーを設定します。

### AWS コンソールでの設定

1. 作成したバケットを選択
2. 「アクセス許可」タブをクリック
3. 「バケットポリシー」セクションで「編集」をクリック
4. 以下のポリシーを貼り付け（`your-bucket-name`を実際のバケット名に置換）

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

### AWS CLIでの設定

```bash
# ポリシーファイルを作成
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::musepose-storage-your-name/*"
        }
    ]
}
EOF

# ポリシーを適用
aws s3api put-bucket-policy --bucket musepose-storage-your-name --policy file://bucket-policy.json
```

## 3. IAMユーザーの作成と権限設定

### IAMユーザーの作成

1. [AWS IAMコンソール](https://console.aws.amazon.com/iam/)にアクセス
2. 「ユーザー」→「ユーザーを追加」をクリック
3. ユーザー名を入力（例: `musepose-app-user`）
4. 「プログラムによるアクセス」を選択
5. 「次のステップ」をクリック

### 権限ポリシーの作成

カスタムポリシーを作成して、必要最小限の権限を付与します：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:HeadBucket"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name"
        }
    ]
}
```

### AWS CLIでの権限設定

```bash
# ポリシーファイルを作成
cat > iam-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::musepose-storage-your-name/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:HeadBucket"
            ],
            "Resource": "arn:aws:s3:::musepose-storage-your-name"
        }
    ]
}
EOF

# IAMユーザーを作成
aws iam create-user --user-name musepose-app-user

# ポリシーを作成
aws iam create-policy --policy-name MusePoseS3Policy --policy-document file://iam-policy.json

# ユーザーにポリシーをアタッチ
aws iam attach-user-policy --user-name musepose-app-user --policy-arn arn:aws:iam::YOUR-ACCOUNT-ID:policy/MusePoseS3Policy

# アクセスキーを作成
aws iam create-access-key --user-name musepose-app-user
```

## 4. 環境変数の設定

作成したアクセスキーを使用して、`.env`ファイルを設定します：

```env
# Replicate API Token
REPLICATE_API_TOKEN=your_replicate_api_token_here

# AWS S3設定
AWS_ACCESS_KEY_ID=AKIA...（作成したアクセスキーID）
AWS_SECRET_ACCESS_KEY=...（作成したシークレットアクセスキー）
S3_BUCKET_NAME=musepose-storage-your-name
AWS_REGION=ap-northeast-1
```

## 5. 設定の確認

アプリケーションを起動して、サイドバーでS3設定が正しく認識されているか確認してください：

```bash
streamlit run app.py
```

✅ 正常に設定されている場合：
- サイドバーに「S3が正しく設定されています」と表示
- バケット名とリージョンが表示される

⚠️ 設定に問題がある場合：
- 「S3が設定されていません」と表示
- デモモードで動作

## 6. セキュリティのベストプラクティス

### アクセスキーの管理

- アクセスキーは定期的にローテーションする
- 不要になったアクセスキーは削除する
- `.env`ファイルをGitにコミットしない

### バケットの設定

- バケットのバージョニングを有効にする（推奨）
- ライフサイクルポリシーを設定して古いファイルを自動削除
- CloudTrailでアクセスログを監視

### ネットワークセキュリティ

- 可能であれば、特定のIPアドレスからのアクセスのみ許可
- VPCエンドポイントを使用してプライベート接続を確立

## 7. コスト最適化

### ストレージクラスの選択

```python
# S3アップロード時にストレージクラスを指定
extra_args = {
    'ContentType': content_type,
    'StorageClass': 'STANDARD_IA'  # 低頻度アクセス用
}
```

### ライフサイクルポリシーの設定

```json
{
    "Rules": [
        {
            "ID": "DeleteOldFiles",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "uploads/"
            },
            "Expiration": {
                "Days": 30
            }
        }
    ]
}
```

## 8. トラブルシューティング

### よくあるエラー

1. **AccessDenied エラー**
   - IAM権限を確認
   - バケットポリシーを確認

2. **NoSuchBucket エラー**
   - バケット名のスペルを確認
   - リージョンが正しいか確認

3. **InvalidAccessKeyId エラー**
   - アクセスキーIDが正しいか確認
   - アクセスキーが有効か確認

### デバッグ方法

```python
# S3接続テスト
from s3_utils import s3_manager

if s3_manager.is_configured():
    print("S3設定OK")
    print(f"バケット: {s3_manager.bucket_name}")
    print(f"リージョン: {s3_manager.region}")
else:
    print("S3設定に問題があります")
```

## 9. 参考リンク

- [AWS S3 ドキュメント](https://docs.aws.amazon.com/s3/)
- [AWS IAM ドキュメント](https://docs.aws.amazon.com/iam/)
- [boto3 ドキュメント](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) 