from flask import Flask, request, abort

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "LINE Bot 健康檢查（測試用）", 200

@app.route("/callback", methods=["POST"])
def callback():
    return "OK", 200
