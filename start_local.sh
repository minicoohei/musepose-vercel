#!/bin/bash

# MusePose ローカルデプロイメント起動スクリプト

echo "🎬 MusePose ローカルデプロイメントを開始します..."

# 既存のプロセスを停止
echo "📋 既存のプロセスを停止中..."
pkill -f "next dev" 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true

# ポートの確認
echo "🔍 ポートの使用状況を確認中..."
if lsof -i :3001 > /dev/null 2>&1; then
    echo "⚠️  ポート3001が使用中です。別のポートを使用します。"
    NEXT_PORT=3002
else
    NEXT_PORT=3001
fi

if lsof -i :8503 > /dev/null 2>&1; then
    echo "⚠️  ポート8503が使用中です。別のポートを使用します。"
    STREAMLIT_PORT=8504
else
    STREAMLIT_PORT=8503
fi

echo "📱 使用ポート:"
echo "  Next.js: $NEXT_PORT"
echo "  Streamlit: $STREAMLIT_PORT"

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "📦 仮想環境を作成中..."
    python3 -m venv venv
fi

# 依存関係のインストール
echo "📚 依存関係をインストール中..."
npm install --silent
source venv/bin/activate
pip install -r requirements.txt --quiet

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo "⚠️  .envファイルが見つかりません。env_example.txtからコピーします。"
    cp env_example.txt .env
fi

# バックグラウンドでStreamlitを起動
echo "🚀 Streamlitアプリを起動中（ポート: $STREAMLIT_PORT）..."
source venv/bin/activate && streamlit run app.py --server.port $STREAMLIT_PORT --server.headless true &
STREAMLIT_PID=$!

# 少し待ってからNext.jsを起動
sleep 3
echo "🚀 Next.jsアプリを起動中（ポート: $NEXT_PORT）..."
npm run dev -- -p $NEXT_PORT &
NEXT_PID=$!

# 起動完了メッセージ
sleep 5
echo ""
echo "🎉 ローカルデプロイメントが完了しました！"
echo ""
echo "📱 アクセスURL:"
echo "  🌐 メインアプリ: http://localhost:$NEXT_PORT"
echo "  ⚙️  バックエンド: http://localhost:$STREAMLIT_PORT"
echo ""
echo "🛑 停止するには Ctrl+C を押してください"
echo ""

# プロセスの監視
trap 'echo "🛑 アプリケーションを停止中..."; kill $STREAMLIT_PID $NEXT_PID 2>/dev/null; exit' INT

# プロセスが生きている間は待機
wait 