#!/bin/bash

# MusePose TikTokダンス動画生成アプリ起動スクリプト

echo "🎬 MusePose TikTokダンス動画生成アプリを起動中..."

# 仮想環境の確認と作成
if [ ! -d "venv" ]; then
    echo "⚠️  仮想環境が見つかりません。作成中..."
    python3 -m venv venv
fi

# 仮想環境を有効化
echo "📦 仮想環境を有効化中..."
source venv/bin/activate

# 依存関係をインストール
echo "📚 依存関係をインストール中..."
pip install -r requirements.txt

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo "⚠️  .envファイルが見つかりません。"
    echo ""
    echo "🤖 AWS設定を自動化する場合は以下を実行してください:"
    echo "   python aws_cli_setup.py      # 推奨：CLI自動設定"
    echo "   python aws_manual_setup_guide.py  # 手動設定ガイド"
    echo ""
    echo "📝 手動で設定する場合:"
    echo "   cp env_example.txt .env"
    echo "   .envファイルを編集してAPIキーを設定"
    echo ""
    
    # ユーザーに選択を求める
    echo "どの方法で設定しますか？"
    echo "1) CLI自動設定を実行"
    echo "2) 手動設定ガイドを表示" 
    echo "3) スキップしてアプリを起動（デモモード）"
    read -p "選択してください (1-3): " choice
    
    case $choice in
        1)
            echo "🚀 CLI自動設定を開始します..."
            python aws_cli_setup.py
            ;;
        2)
            echo "📖 手動設定ガイドを表示します..."
            python aws_manual_setup_guide.py
            ;;
        3)
            echo "⚠️ デモモードでアプリを起動します"
            ;;
        *)
            echo "❌ 無効な選択です。デモモードで起動します。"
            ;;
    esac
fi

# AWS CLIの確認
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI が利用可能です"
else
    echo "💡 AWS CLIをインストールすると自動設定が利用できます:"
    echo "   macOS: brew install awscli"
    echo "   Linux: pip install awscli"
fi

# Streamlitアプリを起動
echo "🚀 Streamlitアプリを起動中..."
streamlit run app.py 