import os
import google.generativeai as genai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import logging

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
    exit(1)

# 初始化LINE Bot
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 用戶對話歷史存儲（簡單的內存存儲）
user_conversations = {}

def get_gemini_response(user_id, message):
    """獲取Gemini回應"""
    try:
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
        system_prompt = """你是一個友善的AI助手，請用繁體中文回答問題。
請保持回答簡潔明瞭，適合在LINE聊天中使用。
如果用戶問候你，請友善地回應。"""
        
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
        user_id = event.source.user_id
        user_message = event.message.text
        
        logger.info(f"收到來自 {user_id} 的訊息: {user_message}")
        
        # 獲取AI回應
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
    return {"status": "healthy", "service": "LINE Bot with Gemini"}

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)