import os
import tempfile
import cv2
import yt_dlp
import replicate
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import logging
import time
import subprocess
import math
from s3_utils import s3_manager

# 環境変数を読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="MusePose - TikTokダンス動画生成",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# カスタムCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: hsl(0 0% 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: hsl(222.2 84% 4.9%);
            color: hsl(210 40% 98%);
        }
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 0 2rem 0;
        border-bottom: 1px solid hsl(214.3 31.8% 91.4%);
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(to right, hsl(222.2 47.4% 11.2%), hsl(215.4 16.3% 46.9%));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        color: hsl(215.4 16.3% 46.9%);
        font-size: 1.125rem;
        font-weight: 400;
    }
    
    .card {
        background: hsl(0 0% 100%);
        border: 1px solid hsl(214.3 31.8% 91.4%);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    }
    
    @media (prefers-color-scheme: dark) {
        .card {
            background: hsl(222.2 84% 4.9%);
            border: 1px solid hsl(217.2 32.6% 17.5%);
        }
        .main-header {
            border-bottom: 1px solid hsl(217.2 32.6% 17.5%);
        }
    }
    
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: hsl(222.2 47.4% 11.2%);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* テキスト入力とラベルの色を明示的に設定 */
    .stTextInput label, .stFileUploader label {
        color: hsl(222.2 47.4% 11.2%) !important;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input {
        color: hsl(222.2 47.4% 11.2%) !important;
        background: hsl(0 0% 100%) !important;
        border: 1px solid hsl(214.3 31.8% 91.4%) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: hsl(215.4 16.3% 46.9%) !important;
    }
    
    /* ファイルアップローダーのスタイル */
    .stFileUploader > div > div {
        background: hsl(0 0% 100%) !important;
        border: 1px solid hsl(214.3 31.8% 91.4%) !important;
        border-radius: 0.5rem;
    }
    
    /* ヘッダーのスタイル */
    h3 {
        color: hsl(222.2 47.4% 11.2%) !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    h4 {
        color: hsl(222.2 47.4% 11.2%) !important;
        font-weight: 500;
        margin-bottom: 0.75rem;
    }
    
    @media (prefers-color-scheme: dark) {
        .stTextInput label, .stFileUploader label {
            color: hsl(210 40% 98%) !important;
        }
        .stTextInput > div > div > input {
            color: hsl(210 40% 98%) !important;
            background: hsl(222.2 84% 4.9%) !important;
            border: 1px solid hsl(217.2 32.6% 17.5%) !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: hsl(215.4 16.3% 56.9%) !important;
        }
        .stFileUploader > div > div {
            background: hsl(222.2 84% 4.9%) !important;
            border: 1px solid hsl(217.2 32.6% 17.5%) !important;
        }
        h3, h4 {
            color: hsl(210 40% 98%) !important;
        }
    }
    
    .stButton > button {
        background: hsl(222.2 47.4% 11.2%);
        color: hsl(210 40% 98%);
        border: 1px solid hsl(214.3 31.8% 91.4%);
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        width: 100%;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    }
    
    .stButton > button:hover {
        background: hsl(222.2 47.4% 11.2% / 0.9);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    
    .stButton > button:disabled {
        background: hsl(210 40% 96%);
        color: hsl(215.4 16.3% 46.9%);
        cursor: not-allowed;
    }
    
    .primary-button {
        background: hsl(221.2 83.2% 53.3%) !important;
        color: hsl(210 40% 98%) !important;
    }
    
    .primary-button:hover {
        background: hsl(221.2 83.2% 53.3% / 0.9) !important;
    }
    
    .destructive-button {
        background: hsl(0 84.2% 60.2%) !important;
        color: hsl(210 40% 98%) !important;
    }
    
    .destructive-button:hover {
        background: hsl(0 84.2% 60.2% / 0.9) !important;
    }
    
    .stFileUploader {
        border: 2px dashed hsl(214.3 31.8% 91.4%);
        border-radius: 0.75rem;
        padding: 2rem;
        text-align: center;
        background: hsl(210 40% 98%);
        transition: all 0.2s ease-in-out;
    }
    
    .stFileUploader:hover {
        border-color: hsl(221.2 83.2% 53.3%);
        background: hsl(221.2 83.2% 53.3% / 0.05);
    }
    
    .success-alert {
        background: hsl(143 85% 96%);
        border: 1px solid hsl(145 92% 91%);
        color: hsl(140 100% 27%);
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .error-alert {
        background: hsl(0 93% 94%);
        border: 1px solid hsl(0 93% 94%);
        color: hsl(0 84% 37%);
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .warning-alert {
        background: hsl(48 96% 89%);
        border: 1px solid hsl(48 96% 89%);
        color: hsl(25 95% 39%);
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-alert {
        background: hsl(214 95% 93%);
        border: 1px solid hsl(214 95% 93%);
        color: hsl(213 94% 68%);
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .progress-container {
        background: hsl(210 40% 96%);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .stProgress > div > div > div {
        background: hsl(221.2 83.2% 53.3%);
        border-radius: 0.25rem;
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        background: hsl(210 40% 96%);
        color: hsl(215.4 16.3% 46.9%);
    }
    
    .sidebar-section {
        background: hsl(210 40% 98%);
        border: 1px solid hsl(214.3 31.8% 91.4%);
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .sidebar-title {
        font-weight: 600;
        color: hsl(222.2 47.4% 11.2%);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    @media (prefers-color-scheme: dark) {
        .stTextInput > div > div > input {
            background: hsl(222.2 84% 4.9%);
            border-color: hsl(217.2 32.6% 17.5%);
            color: hsl(210 40% 98%);
        }
        .stFileUploader {
            background: hsl(222.2 84% 4.9%);
            border-color: hsl(217.2 32.6% 17.5%);
        }
        .sidebar-section {
            background: hsl(222.2 84% 4.9%);
            border-color: hsl(217.2 32.6% 17.5%);
        }
        .sidebar-title {
            color: hsl(210 40% 98%);
        }
        .progress-container {
            background: hsl(217.2 32.6% 17.5%);
        }
    }
</style>
""", unsafe_allow_html=True)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def download_tiktok_video(self, url):
        """TikTok動画をダウンロード（改良版）"""
        try:
            # より多くのフォーマットオプションを試行
            format_options = [
                'best[height<=720][ext=mp4]/best[height<=720]',  # MP4優先、720p以下
                'best[height<=1080][ext=mp4]/best[height<=1080]', # MP4優先、1080p以下
                'best[ext=mp4]/best',                             # MP4優先、任意の解像度
                'worst[ext=mp4]/worst',                           # 最低品質MP4
                'best/worst'                                      # フォールバック
            ]
            
            for format_option in format_options:
                try:
                    ydl_opts = {
                        'outtmpl': os.path.join(self.temp_dir, 'tiktok_video.%(ext)s'),
                        'format': format_option,
                        'quiet': True,
                        'no_warnings': True,
                        'extractaudio': False,
                        'writesubtitles': False,
                        'writeautomaticsub': False,
                        'ignoreerrors': False,
                        # TikTok特有の設定を追加
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        },
                        'extractor_args': {
                            'tiktok': {
                                'webpage_url_basename': 'video'
                            }
                        }
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        logger.info(f"フォーマット '{format_option}' でダウンロードを試行中...")
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        
                        # ダウンロードされたファイルを探す
                        possible_files = []
                        for ext in ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv']:
                            test_file = filename.replace('.%(ext)s', ext)
                            if os.path.exists(test_file):
                                possible_files.append(test_file)
                        
                        if possible_files:
                            final_file = possible_files[0]
                            logger.info(f"ダウンロード成功: {final_file}")
                            return final_file
                        
                except Exception as e:
                    logger.warning(f"フォーマット '{format_option}' でのダウンロードに失敗: {e}")
                    continue
            
            # すべてのフォーマットで失敗した場合
            raise Exception("利用可能なフォーマットでダウンロードできませんでした。動画が非公開または削除されている可能性があります。")
            
        except Exception as e:
            logger.error(f"TikTok動画のダウンロードエラー: {e}")
            raise Exception(f"TikTok動画のダウンロードに失敗しました: {str(e)}")
    
    def get_video_info(self, video_path):
        """動画の情報を取得"""
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        return {
            'frame_count': frame_count,
            'fps': fps,
            'width': width,
            'height': height,
            'duration': frame_count / fps if fps > 0 else 0
        }
    
    def split_video(self, video_path, max_duration=30):
        """動画を指定秒数で分割"""
        try:
            video_info = self.get_video_info(video_path)
            duration = video_info['duration']
            
            if duration <= max_duration:
                return [video_path]  # 分割不要
            
            # 分割数を計算
            num_segments = math.ceil(duration / max_duration)
            segment_duration = duration / num_segments
            
            segments = []
            for i in range(num_segments):
                start_time = i * segment_duration
                output_path = os.path.join(self.temp_dir, f'segment_{i:03d}.mp4')
                
                # ffmpegで分割
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-ss', str(start_time),
                    '-t', str(segment_duration),
                    '-c', 'copy',
                    '-avoid_negative_ts', 'make_zero',
                    '-y', output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and os.path.exists(output_path):
                    segments.append(output_path)
                    logger.info(f"セグメント {i+1}/{num_segments} を作成: {output_path}")
                else:
                    logger.error(f"セグメント {i+1} の作成に失敗: {result.stderr}")
            
            return segments
            
        except Exception as e:
            logger.error(f"動画分割エラー: {e}")
            return [video_path]  # エラー時は元の動画を返す
    
    def merge_videos(self, video_paths):
        """複数の動画を結合"""
        try:
            if len(video_paths) == 1:
                return video_paths[0]
            
            # 結合リストファイルを作成
            concat_file = os.path.join(self.temp_dir, 'concat_list.txt')
            with open(concat_file, 'w') as f:
                for video_path in video_paths:
                    f.write(f"file '{video_path}'\n")
            
            # 結合された動画の出力パス
            output_path = os.path.join(self.temp_dir, 'merged_output.mp4')
            
            # ffmpegで結合
            cmd = [
                'ffmpeg', '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"動画結合完了: {output_path}")
                return output_path
            else:
                logger.error(f"動画結合に失敗: {result.stderr}")
                return video_paths[0]  # エラー時は最初の動画を返す
                
        except Exception as e:
            logger.error(f"動画結合エラー: {e}")
            return video_paths[0] if video_paths else None
    
    def upload_to_storage(self, file_path: str, file_type: str = 'video') -> str:
        """ファイルをストレージにアップロード（S3またはローカル）"""
        if s3_manager.is_configured():
            # S3にアップロード
            if file_type == 'video':
                url = s3_manager.upload_video(file_path)
            else:
                url = s3_manager.upload_image(file_path)
            
            if url:
                return url
            else:
                raise Exception("S3へのアップロードに失敗しました")
        else:
            # S3が設定されていない場合はローカルファイルパスを返す（デモ用）
            logger.warning("S3が設定されていません。ローカルファイルパスを使用します。")
            return f"file://{file_path}"

def show_s3_status():
    """S3設定状況を表示"""
    if s3_manager.is_configured():
        st.markdown("""
        <div class="success-alert">
            <span>✅</span>
            <div>
                <strong>S3が正しく設定されています</strong><br>
                <small>バケット: {}</small><br>
                <small>リージョン: {}</small>
            </div>
        </div>
        """.format(s3_manager.bucket_name, s3_manager.region), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-alert">
            <span>⚠️</span>
            <div>
                <strong>S3が設定されていません</strong><br>
                <small>デモモードで動作します</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-alert">
            <span>💡</span>
            <div>
                <strong>本番環境での使用には以下の環境変数を設定してください：</strong><br>
                <small>• AWS_ACCESS_KEY_ID</small><br>
                <small>• AWS_SECRET_ACCESS_KEY</small><br>
                <small>• S3_BUCKET_NAME</small><br>
                <small>• AWS_REGION（オプション）</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎬 MusePose</h1>
        <p class="main-subtitle">TikTokダンス動画から魅力的なポーズ駆動動画を生成</p>
    </div>
    """, unsafe_allow_html=True)
    
    # セッション状態の初期化
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'result' not in st.session_state:
        st.session_state.result = None
    
    # サイドバーでS3設定状況を表示
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🔧 設定状況</div>', unsafe_allow_html=True)
        show_s3_status()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # TikTokダウンロードのヒント
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">💡 TikTok動画のヒント</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-alert">
            <span>📋</span>
            <div>
                <strong>推奨する動画の特徴:</strong><br>
                <small>• 公開設定の動画</small><br>
                <small>• 短い動画（15-60秒）</small><br>
                <small>• 明確なダンス動作</small><br>
                <small>• 1人の人物が写っている</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # メインコンテナ
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📹 入力設定")
        
        # TikTok URL入力
        tiktok_url = st.text_input(
            "TikTok動画URL",
            placeholder="https://www.tiktok.com/@username/video/...",
            help="処理したいTikTok動画のURLを入力してください"
        )
        
        # リファレンス画像アップロード
        st.markdown("### 🖼️ リファレンス画像")
        uploaded_file = st.file_uploader(
            "画像を選択",
            type=['png', 'jpg', 'jpeg'],
            help="ポーズを適用したいキャラクターの画像をアップロードしてください"
        )
        
        if uploaded_file is not None:
            # アップロードされた画像を表示
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされた画像", use_column_width=True)
        
        # 処理ボタン
        button_disabled = st.session_state.processing or not tiktok_url or not uploaded_file
        
        if not tiktok_url or not uploaded_file:
            st.markdown("""
            <div class="warning-alert">
                <span>⚠️</span>
                <div>TikTok URLとリファレンス画像の両方を入力してください</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🎬 動画を生成", type="primary", disabled=button_disabled):
            st.session_state.processing = True
            st.session_state.result = None  # 前の結果をクリア
            st.rerun()
    
    with col2:
        # 処理中の表示
        if st.session_state.processing:
            st.markdown("### 🔄 処理中...")
            
            # キャンセルボタン
            col_cancel1, col_cancel2, col_cancel3 = st.columns([1, 1, 1])
            with col_cancel2:
                if st.button("❌ キャンセル", key="cancel_btn"):
                    st.session_state.processing = False
                    st.markdown("""
                    <div class="warning-alert">
                        <span>⚠️</span>
                        <div>処理がキャンセルされました</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
            
            # プログレスバーコンテナ
            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
            progress_bar = st.progress(0)
            status_text = st.empty()
            detail_text = st.empty()
            st.markdown('</div>', unsafe_allow_html=True)
            
            try:
                processor = VideoProcessor()
                
                # ステップ1: TikTok動画をダウンロード
                status_text.markdown("""
                <div class="info-alert">
                    <span>📥</span>
                    <div>TikTok動画をダウンロード中...</div>
                </div>
                """, unsafe_allow_html=True)
                detail_text.markdown('<div class="status-badge">動画URLを解析しています...</div>', unsafe_allow_html=True)
                progress_bar.progress(0.05)
                
                video_path = processor.download_tiktok_video(tiktok_url)
                
                if not os.path.exists(video_path):
                    st.markdown("""
                    <div class="error-alert">
                        <span>❌</span>
                        <div>動画ファイルが見つかりません</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.processing = False
                    st.rerun()
                
                detail_text.markdown('<div class="status-badge">✅ 動画のダウンロードが完了しました</div>', unsafe_allow_html=True)
                progress_bar.progress(0.15)
                
                # ステップ2: 動画情報を取得
                status_text.markdown("""
                <div class="info-alert">
                    <span>📊</span>
                    <div>動画情報を解析中...</div>
                </div>
                """, unsafe_allow_html=True)
                detail_text.markdown('<div class="status-badge">動画のフレーム数、解像度を確認中...</div>', unsafe_allow_html=True)
                progress_bar.progress(0.25)
                
                video_info = processor.get_video_info(video_path)
                detail_text.markdown('<div class="status-badge">動画情報: {}x{}, {}フレーム, {:.1f}秒</div>'.format(video_info['width'], video_info['height'], video_info['frame_count'], video_info['duration']), unsafe_allow_html=True)
                progress_bar.progress(0.25)
                
                # ステップ2.5: 長い動画の場合は分割
                segments_to_process = []
                if video_info['duration'] > 30:
                    status_text.markdown("""
                    <div class="info-alert">
                        <span>✂️</span>
                        <div>長い動画を分割中...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    detail_text.markdown('<div class="status-badge">動画を30秒セグメントに分割しています...</div>', unsafe_allow_html=True)
                    progress_bar.progress(0.30)
                    
                    segments = processor.split_video(video_path, max_duration=30)
                    segments_to_process = segments
                    detail_text.markdown('<div class="status-badge">✅ {}個のセグメントに分割完了</div>'.format(len(segments)), unsafe_allow_html=True)
                else:
                    segments_to_process = [video_path]
                    detail_text.markdown('<div class="status-badge">分割不要（30秒以下）</div>', unsafe_allow_html=True)
                
                progress_bar.progress(0.35)
                
                # ステップ3: S3にアップロード
                status_text.markdown("""
                <div class="info-alert">
                    <span>☁️</span>
                    <div>動画ファイルをクラウドストレージにアップロード中...</div>
                </div>
                """, unsafe_allow_html=True)
                progress_bar.progress(0.40)
                
                # リファレンス画像の処理
                reference_image_url = None
                if uploaded_file is not None:
                    detail_text.markdown('<div class="status-badge">リファレンス画像をアップロード中...</div>', unsafe_allow_html=True)
                    # 一時ファイルとして保存
                    temp_image_path = os.path.join(processor.temp_dir, uploaded_file.name)
                    with open(temp_image_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    reference_image_url = processor.upload_to_storage(temp_image_path, 'image')
                    detail_text.markdown('<div class="status-badge">✅ リファレンス画像のアップロードが完了しました</div>', unsafe_allow_html=True)
                else:
                    # デフォルトの参照画像
                    reference_image_url = "https://replicate.delivery/pbxt/L45Zr9BRxMFeVAUNk23NNrkYLeuXjmmcZIVN7E43FL0M1M7h/ref.png"
                
                progress_bar.progress(0.50)
                
                # ステップ4: 各セグメントをMusePoseで処理
                status_text.markdown("""
                <div class="info-alert">
                    <span>🎨</span>
                    <div>MusePoseで動画を生成中...</div>
                </div>
                """, unsafe_allow_html=True)
                
                processed_segments = []
                total_segments = len(segments_to_process)
                
                for i, segment_path in enumerate(segments_to_process):
                    detail_text.markdown('<div class="status-badge">セグメント {}/{} を処理中...</div>'.format(i+1, total_segments), unsafe_allow_html=True)
                    
                    # セグメントをS3にアップロード
                    segment_url = processor.upload_to_storage(segment_path, 'video')
                    
                    # セグメントの動画情報を取得
                    segment_info = processor.get_video_info(segment_path)
                    max_frames = min(segment_info['frame_count'], 300)
                    image_resolution = min(segment_info['height'], 720)
                    detect_resolution = 512
                    
                    # 進捗を更新
                    base_progress = 0.50 + (i * 0.40 / total_segments)
                    progress_bar.progress(base_progress)
                    
                    if s3_manager.is_configured():
                        # S3が設定されている場合は実際にReplicateを実行
                        detail_text.markdown('<div class="status-badge">セグメント {}/{} の予測を開始...</div>'.format(i+1, total_segments), unsafe_allow_html=True)
                        # 非同期で予測を開始
                        prediction = replicate.predictions.create(
                            "douwantech/musepose:56b9a43be4bdd701bfc4bbdc91b6d0410c81da51e7e7037c790449f34277f84d",
                            input={
                                "vidfn": segment_url,
                                "imgfn_refer": reference_image_url,
                                "detect_resolution": detect_resolution,
                                "image_resolution": image_resolution,
                                "align_frame": 0,
                                "max_frame": max_frames
                            }
                        )
                    
                    # 進捗を監視
                    progress = 0.70
                    step_count = 0
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        prediction.reload()
                        step_count += 1
                        
                        # ログから進捗を推定
                        if prediction.logs:
                            logs_lower = prediction.logs.lower()
                            if "downloading" in logs_lower or "download" in logs_lower:
                                progress = 0.75
                                detail_text.markdown('<div class="status-badge">モデルファイルをダウンロード中...</div>', unsafe_allow_html=True)
                            elif "processing" in logs_lower or "pose" in logs_lower:
                                progress = 0.80 + (step_count * 0.01)  # 徐々に進捗を増加
                                detail_text.markdown('<div class="status-badge">フレームを処理中... ({})</div>'.format(step_count), unsafe_allow_html=True)
                            elif "encoding" in logs_lower or "video" in logs_lower:
                                progress = 0.92
                                detail_text.markdown('<div class="status-badge">動画をエンコード中...</div>', unsafe_allow_html=True)
                            elif "completed" in logs_lower or "finished" in logs_lower:
                                progress = 0.95
                                detail_text.markdown('<div class="status-badge">処理を完了中...</div>', unsafe_allow_html=True)
                        else:
                            # ログがない場合は時間ベースで進捗を推定
                            progress = min(0.70 + (step_count * 0.005), 0.90)
                            detail_text.markdown('<div class="status-badge">処理中... ({})</div>'.format(step_count * 2), unsafe_allow_html=True)
                        
                        progress_bar.progress(min(progress, 0.95))
                        time.sleep(2)  # 2秒ごとにチェック
                        
                        # 長時間処理の場合の表示更新
                        if step_count > 30:  # 1分以上
                            detail_text.markdown('<div class="status-badge">高品質な動画を生成中です... ({})</div>'.format(step_count * 2), unsafe_allow_html=True)
                    
                    if prediction.status == "succeeded":
                        output = prediction.output
                        detail_text.markdown('<div class="status-badge">動画生成が完了しました！</div>', unsafe_allow_html=True)
                    else:
                        raise Exception(f"処理に失敗しました: {prediction.error}")
                    
                else:
                    # デモモードの場合はダミー出力
                    st.warning("⚠️ デモモード: 実際の動画処理には外部ストレージの設定が必要です")
                    for i in range(5):
                        progress_bar.progress(0.70 + (i + 1) * 0.05)
                        detail_text.markdown('<div class="status-badge">デモ処理中... ステップ {}</div>'.format(i+1), unsafe_allow_html=True)
                        time.sleep(0.5)
                    output = "https://replicate.delivery/pbxt/pGhU1BDVZXrLDVl2wvQs77YPjYm6wu2ZH7dGrh0XGB4JGMvE/video_and_audio.mp4"
                
                # 完了
                progress_bar.progress(1.0)
                status_text.markdown("""
                <div class="success-alert">
                    <span>✅</span>
                    <div>処理が完了しました！</div>
                </div>
                """, unsafe_allow_html=True)
                detail_text.markdown('<div class="status-badge">結果を表示しています...</div>', unsafe_allow_html=True)
                
                # 結果を保存
                st.session_state.result = {
                    'output_video': output,
                    'video_info': video_info,
                    'processing_params': {
                        'max_frames': max_frames,
                        'image_resolution': image_resolution,
                        'detect_resolution': detect_resolution
                    },
                    'used_s3': s3_manager.is_configured()
                }
                
                st.session_state.processing = False
                time.sleep(1)  # 成功メッセージを表示
                st.rerun()
                
            except Exception as e:
                st.markdown("""
                <div class="error-alert">
                    <span>❌</span>
                    <div>エラーが発生しました: {}</div>
                </div>
                """.format(str(e)), unsafe_allow_html=True)
                st.session_state.processing = False
                
                # エラーの詳細情報を表示
                with st.expander("エラーの詳細"):
                    st.text(f"エラータイプ: {type(e).__name__}")
                    st.text(f"エラーメッセージ: {str(e)}")
                    
                    # TikTokダウンロードエラーの場合の対処法
                    if "TikTok" in str(e) or "format" in str(e).lower():
                        st.markdown("""
                        <div class="warning-alert">
                            <span>⚠️</span>
                            <div>
                                <strong>TikTok動画ダウンロードエラーの対処法:</strong><br>
                                <small>1. 動画が公開設定になっているか確認</small><br>
                                <small>2. 別のTikTok動画URLを試す</small><br>
                                <small>3. 短い動画（15-60秒）を選ぶ</small><br>
                                <small>4. yt-dlpを最新版に更新: `pip install --upgrade yt-dlp`</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # リトライボタン
                if st.button("🔄 もう一度試す"):
                    st.session_state.processing = False
                    st.rerun()
        
        elif st.session_state.result:
            st.markdown("### ✅ 生成結果")
            
            result = st.session_state.result
            
            # S3使用状況を表示
            if result.get('used_s3'):
                st.markdown("""
                <div class="success-alert">
                    <span>✅</span>
                    <div>🌐 S3ストレージを使用して処理されました</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-alert">
                    <span>💻</span>
                    <div>デモモードで処理されました</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 動画を表示
            st.video(result['output_video'])
            
            # ダウンロードボタン
            st.markdown(f"""
            <a href="{result['output_video']}" download style="text-decoration: none;">
                <div style="background: hsl(221.2 83.2% 53.3%); color: hsl(210 40% 98%); 
                     padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-align: center; 
                     font-weight: 500; margin: 1rem 0; transition: all 0.2s ease-in-out;
                     cursor: pointer; display: inline-block; width: 100%;">
                    📥 動画をダウンロード
                </div>
            </a>
            """, unsafe_allow_html=True)
            
            # 処理情報を表示
            st.markdown("#### 📊 処理情報")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("フレーム数", f"{result['video_info']['frame_count']}")
                st.metric("FPS", f"{result['video_info']['fps']:.2f}")
                st.metric("解像度", f"{result['video_info']['width']}x{result['video_info']['height']}")
            with col2:
                st.metric("処理フレーム数", f"{result['processing_params']['max_frames']}")
                st.metric("出力解像度", f"{result['processing_params']['image_resolution']}px")
                st.metric("検出解像度", f"{result['processing_params']['detect_resolution']}px")
            
            # 新しい動画を処理するボタン
            if st.button("🔄 新しい動画を処理"):
                st.session_state.result = None
                st.rerun()
    
    # フッター
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem 0; 
         border-top: 1px solid hsl(214.3 31.8% 91.4%); 
         color: hsl(215.4 16.3% 46.9%);">
        <p style="margin: 0; font-size: 0.875rem;">
            Powered by MusePose & Replicate | Built with ❤️ using Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 