import os
import google.generativeai as genai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import logging
import requests  # 新增：用於發送等待動畫API請求

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 環境變數設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 檢查必要的環境變數
if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, GEMINI_API_KEY]):
    logger.error("請設定所有必要的環境變數")
    # 在部署環境中，如果環境變數未設定，我們先讓服務啟動，但會記錄錯誤
    logger.error(f"LINE_CHANNEL_ACCESS_TOKEN: {'已設定' if LINE_CHANNEL_ACCESS_TOKEN else '未設定'}")
    logger.error(f"LINE_CHANNEL_SECRET: {'已設定' if LINE_CHANNEL_SECRET else '未設定'}")
    logger.error(f"GEMINI_API_KEY: {'已設定' if GEMINI_API_KEY else '未設定'}")

# 初始化LINE Bot（只有在環境變數存在時）
line_bot_api = None
handler = None
model = None

if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET:
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化Gemini（只有在API key存在時）
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# 用戶對話歷史存儲（簡單的內存存儲）
user_conversations = {}

# 新增：顯示等待動畫的函數
def show_loading_animation(user_id, loading_seconds=5):
    """顯示LINE等待動畫"""
    try:
        if not LINE_CHANNEL_ACCESS_TOKEN:
            logger.warning("無法顯示等待動畫：LINE Token未設定")
            return False
            
        url = "https://api.line.me/v2/bot/chat/loading/start"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
        }
        data = {
            "chatId": user_id,
            "loadingSeconds": loading_seconds
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 202:
            logger.info(f"等待動畫已開始顯示給用戶 {user_id}，持續 {loading_seconds} 秒")
            return True
        else:
            logger.warning(f"等待動畫顯示失敗：{response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"顯示等待動畫時發生錯誤: {str(e)}")
        return False

def get_gemini_response(user_id, message):
    """獲取Gemini回應"""
    try:
        if not model:
            return "AI服務暫時無法使用，請稍後再試。"
            
        # 獲取或創建用戶對話歷史
        if user_id not in user_conversations:
            user_conversations[user_id] = []
        
        # 添加用戶消息到歷史
        user_conversations[user_id].append(f"用戶: {message}")
        
        # 保持對話歷史在合理長度內（最多10輪對話）
        if len(user_conversations[user_id]) > 20:
            user_conversations[user_id] = user_conversations[user_id][-20:]
        
        # 構建完整的對話上下文
        context = "\n".join(user_conversations[user_id][-10:])  # 最近5輪對話
        
        # 系統提示詞
        system_prompt = """你是一個專業的AI助手，擅長提供簡短且有用的回答。 請用繁體中文回應，並遵循以下原則：
記住對話脈絡，提供連貫的服務
提供重點條列式且結構化的回答
會主動詢問澄清問題以提供更精確的幫助
適時提供額外的相關知識和資源
如果不確定答案，會誠實說明並提供可能的方向適合在LINE聊天中閱讀，但內容要有深度。"""
        
        # 生成回應
        full_prompt = f"{system_prompt}\n\n對話歷史:\n{context}\n\nAI:"
        
        response = model.generate_content(full_prompt)
        ai_response = response.text.strip()
        
        # 添加AI回應到歷史
        user_conversations[user_id].append(f"AI: {ai_response}")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Gemini API錯誤: {str(e)}")
        return "抱歉，我現在無法回應，請稍後再試。"

@app.route("/callback", methods=['POST'])
def callback():
    """LINE Webhook回調函數"""
    if not handler:
        abort(500)
        
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"處理webhook時發生錯誤: {str(e)}")
        abort(500)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """處理文字訊息"""
    try:
        if not line_bot_api:
            logger.error("LINE Bot API 未初始化")
            return
            
        user_id = event.source.user_id
        user_message = event.message.text
        
        logger.info(f"收到來自 {user_id} 的訊息: {user_message}")
        
        # 新增：立即顯示等待動畫（根據訊息長度調整時間）
        loading_seconds = 5  # 預設5秒
        if len(user_message) > 50:
            loading_seconds = 8  # 較長訊息用8秒
        if len(user_message) > 100:
            loading_seconds = 12  # 很長訊息用12秒
            
        # 包含複雜關鍵字的訊息延長等待時間
        complex_keywords = ['分析', '解釋', '詳細', '比較', '計算', '翻譯', '寫作', '創作']
        if any(keyword in user_message for keyword in complex_keywords):
            loading_seconds = 15
            
        show_loading_animation(user_id, loading_seconds)
        
        # 獲取AI回應（原有邏輯不變）
        ai_response = get_gemini_response(user_id, user_message)
        
        # 回傳訊息給用戶
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ai_response)
        )
        
        logger.info(f"回應給 {user_id}: {ai_response}")
        
    except LineBotApiError as e:
        logger.error(f"LINE Bot API錯誤: {e.message}")
        logger.error(f"錯誤詳情: {e.error.details}")
    except Exception as e:
        logger.error(f"處理訊息時發生錯誤: {str(e)}")

@app.route("/", methods=['GET'])
def home():
    """健康檢查端點"""
    return "LINE Bot服務正在運行中！"

@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查"""
    status = {
        "status": "healthy",
        "service": "LINE Bot with Gemini",
        "line_bot_initialized": line_bot_api is not None,
        "gemini_initialized": model is not None,
        "loading_animation_available": LINE_CHANNEL_ACCESS_TOKEN is not None  # 新增
    }
    return status

# 新增：測試等待動畫的端點（可選）
@app.route("/test-loading", methods=['POST'])
def test_loading():
    """測試等待動畫功能"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        seconds = data.get('seconds', 5)
        
        if not user_id:
            return {"success": False, "error": "需要提供 userId"}, 400
            
        success = show_loading_animation(user_id, seconds)
        
        return {
            "success": success,
            "message": f"等待動畫已{'成功' if success else '失敗'}觸發",
            "userId": user_id,
            "seconds": seconds
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
