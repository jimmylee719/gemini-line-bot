# LINE AI 聊天機器人 🤖

基於 Google Gemini 1.5 的 LINE 聊天機器人，提供 24 小時智能對話服務，完全免費部署方案。

## ✨ 功能特色

- 🚀 **24/7 運行**：全天候智能回應
- 🧠 **對話記憶**：記住最近 10 輪對話內容
- 🇹🇼 **繁體中文優化**：專為中文使用者設計
- 💰 **完全免費**：使用免費服務搭建
- 🛡️ **穩定可靠**：完整錯誤處理機制
- ⚡ **快速回應**：基於 Gemini 1.5 Flash 模型

## 🏗️ 技術架構

- **AI 模型**：Google Gemini 1.5 Flash
- **後端框架**：Python Flask
- **聊天平台**：LINE Messaging API
- **部署平台**：Render.com (免費方案)

## 📋 前置需求

### 1. LINE Developers 帳號
- 前往 [LINE Developers Console](https://developers.line.biz/)
- 建立 Messaging API Channel
- 取得 Channel Access Token 和 Channel Secret

### 2. Google Gemini API
- 前往 [Google AI Studio](https://aistudio.google.com/)
- 建立 API Key
- 每月享有免費額度

### 3. Render.com 帳號
- 註冊 [Render.com](https://render.com/)
- 連接 GitHub 帳號

## 🚀 快速開始

### 步驟 1：複製專案

```bash
git clone https://github.com/your-username/line-bot-gemini.git
cd line-bot-gemini
```

### 步驟 2：環境設定

建立 `.env` 檔案並設定環境變數：

```env
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
GEMINI_API_KEY=your_gemini_api_key
```

### 步驟 3：本地測試

```bash
# 安裝依賴套件
pip install -r requirements.txt

# 運行應用程式
python app.py
```

### 步驟 4：部署到 Render

1. 將程式碼推送到 GitHub
2. 在 Render.com 建立新的 Web Service
3. 連接 GitHub repository
4. 設定環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET` 
   - `GEMINI_API_KEY`
5. 部署完成

### 步驟 5：設定 LINE Webhook

1. 回到 LINE Developers Console
2. 設定 Webhook URL：`https://your-app.onrender.com/callback`
3. 啟用 "Use webhook"
4. 關閉 "Auto-reply messages" 和 "Greeting messages"

## 📁 專案結構

```
line-bot-gemini/
├── app.py              # 主應用程式
├── requirements.txt    # Python 依賴套件
├── render.yaml        # Render 部署設定
├── .env.example       # 環境變數範例
├── README.md          # 專案說明
└── .gitignore         # Git 忽略檔案
```

## 🔧 設定說明

### 環境變數

| 變數名稱 | 說明 | 取得方式 |
|---------|------|---------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot 存取權杖 | LINE Developers Console |
| `LINE_CHANNEL_SECRET` | LINE Bot 頻道密鑰 | LINE Developers Console |
| `GEMINI_API_KEY` | Gemini API 金鑰 | Google AI Studio |

### API 端點

- `GET /` - 健康檢查
- `GET /health` - 服務狀態檢查
- `POST /callback` - LINE Webhook 回調

## 💡 使用說明

1. **加好友**：掃描 LINE Developers Console 中的 QR Code
2. **開始對話**：直接發送訊息給機器人
3. **智能回應**：機器人會基於 Gemini AI 回應
4. **對話記憶**：機器人會記住最近的對話內容

## 🎯 自訂功能

### 修改 AI 個性

在 `app.py` 中的 `system_prompt` 變數：

```python
system_prompt = """你是一個友善的AI助手，請用繁體中文回答問題。
請保持回答簡潔明瞭，適合在LINE聊天中使用。
如果用戶問候你，請友善地回應。"""
```

### 調整對話記憶長度

修改 `get_gemini_response` 函數中的參數：

```python
# 保持對話歷史在合理長度內（最多20條記錄）
if len(user_conversations[user_id]) > 20:
    user_conversations[user_id] = user_conversations[user_id][-20:]
```

## 📊 免費額度限制

### LINE Messaging API
- 免費：每月 500 則訊息
- 超過後：每則訊息 $0.05 USD

### Google Gemini 1.5 Flash
- 免費：每分鐘 15 個請求，每天 1,500 個請求
- 每月：1M tokens 免費

### Render.com
- 免費：每月 750 小時運行時間
- 限制：30 分鐘無活動後休眠

## ⚠️ 注意事項

1. **服務休眠**：Render 免費方案會在無活動 30 分鐘後休眠
2. **首次喚醒**：休眠後首次回應可能需要 10-30 秒
3. **對話記憶**：重啟後對話歷史會清空
4. **速率限制**：注意 Gemini API 的使用限制

## 🔍 故障排除

### 常見問題

**Q: 機器人沒有回應？**
- 檢查 Webhook URL 是否正確設定
- 確認環境變數是否正確配置
- 查看 Render 服務日誌

**Q: 回應很慢？**
- 可能是服務休眠，等待喚醒
- 檢查 Gemini API 是否達到限制

**Q: 出現錯誤訊息？**
- 檢查 API 金鑰是否有效
- 確認服務是否正常運行

### 除錯模式

本地開發時啟用除錯：

```python
if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 專案
2. 建立功能分支
3. 送出變更
4. 提交 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡資訊

如有問題或建議，歡迎透過以下方式聯絡：

- GitHub Issues: [專案 Issues 頁面]
- Email: your-email@example.com

---

**⭐ 如果這個專案對你有幫助，請給個星星支持！**

# 在 app.py 中的 get_gemini_response 函數內修改這個部分：

# 選項 1：專業助手模式
system_prompt = """你是一個專業的AI助手，擅長提供詳細且有用的回答。
請用繁體中文回應，並遵循以下原則：
- 提供詳細且結構化的回答
- 當回答較長時，使用條列或分段方式整理
- 包含實用的建議和具體的步驟
- 必要時提供相關的背景知識
- 保持友善且專業的語調
- 如果不確定答案，會誠實說明並提供可能的方向
適合在LINE聊天中閱讀，但內容要有深度。"""

# 選項 2：創意聊天機器人模式
system_prompt = """你是一個富有創意且有個性的AI助手，名叫「小杰」。
個性特點：
- 幽默風趣，偶爾會開玩笑
- 善於用生動的比喻和例子說明複雜概念
- 會根據話題調整回應風格（正式/輕鬆）
- 記得之前的對話內容，能延續話題
- 用繁體中文回應，語氣自然親切
- 會適時使用表情符號增加趣味性
- 當用戶心情不好時，會給予鼓勵和安慰"""

# 選項 3：專門領域助手模式（以程式設計為例）
system_prompt = """你是一位經驗豐富的程式設計導師，專精於多種程式語言。
回應原則：
- 用繁體中文詳細解釋程式概念
- 提供實用的程式碼範例
- 說明最佳實踐和常見陷阱
- 根據用戶程度調整解釋深度
- 推薦相關的學習資源
- 能幫助除錯和優化程式碼
- 保持耐心和鼓勵的態度"""

# 選項 4：生活顧問模式
system_prompt = """你是一位溫暖的生活顧問，擅長給予實用的生活建議。
特色：
- 用繁體中文親切地回應
- 提供實用且可行的建議
- 考慮台灣的文化背景和生活習慣
- 在健康、職涯、人際關係等方面給予指導
- 會分享相關的小知識和技巧
- 語氣溫暖且充滿正能量
- 必要時會建議尋求專業協助"""

# 選項 5：個人化智能助手模式
system_prompt = """你是用戶的個人智能助手，致力於提供最有價值的幫助。
服務特點：
- 用繁體中文提供專業且詳細的回答
- 能處理各種類型的問題：工作、學習、生活、技術等
- 提供結構化的回答，包含背景、步驟、建議
- 會主動詢問澄清問題以提供更精確的幫助
- 記住對話脈絡，提供連貫的服務
- 適時提供額外的相關資訊和資源
- 保持專業但不失親切的語調"""
