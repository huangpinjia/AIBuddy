import os
import random
import traceback
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore

# -----------------------------
# 初始化 Flask + CORS + dotenv
# -----------------------------
load_dotenv()
app = Flask(__name__)
CORS(app)

# -----------------------------
# 初始化 OpenAI
# -----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_ID = os.getenv("FINE_TUNED_MODEL")  # fine-tuned 模型 ID

# -----------------------------
# 讀取系統提示語
# -----------------------------
SYSTEM_PROMPT = ""
if os.path.exists("prompt.txt"):
    with open("prompt.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read().strip()
else:
    SYSTEM_PROMPT = "你是一個溫柔有禮的聊天助理，請自然地回覆使用者。"

# -----------------------------
# 初始化 Firebase（環境變數 JSON）
# -----------------------------
firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not firebase_json:
    raise RuntimeError("❌ 缺少環境變數 FIREBASE_SERVICE_ACCOUNT")

try:
    # 修復 Render 貼上的 JSON 格式
    try:
        cred_dict = json.loads(firebase_json)
    except json.JSONDecodeError:
        fixed = firebase_json.replace('\\"', '"').replace("\\n", "\n")
        cred_dict = json.loads(fixed)

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print("🔥 Firebase 初始化失敗：", e)
    db = None

# -----------------------------
# 常數
# -----------------------------
MAX_HISTORY = 10  # 只保留最近 10 筆


# -----------------------------
# 首頁（回傳 index.html）
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# 初始化對話（隨機問候語）
# -----------------------------
@app.route("/init", methods=["GET"])
def init():
    try:
        greetings = [
            "你好呀！今天想和我聊點什麼呢？😊",
            "嗨嗨～ 有甚麼想跟我討論的嗎？",
            "啊囉哈！🌟 最近在學什麼呢？我們一起討論啊~",
            "嘿～👋 今天我們要一起討論什麼？",
            "嗨～很高興見到你！😄 你想從哪個主題開始聊聊呢？",
            "Hey Yo！🎉 今天要聊點什麼？ 你的夥伴已上線～"
        ]
        greeting = random.choice(greetings)
        return jsonify({"reply": greeting})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# -----------------------------
# 聊天主功能
# -----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    print("📩 收到請求")  # Debug log
    data = request.get_json(force=True)
    print("🧠 使用者輸入：", data)

    user_id = data.get("user_id", "default")
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "message is required"}), 400

    try:
        # 1️⃣ 讀取 Firestore 歷史紀錄
        history = []
        if db:
            messages_ref = db.collection("conversations").document(user_id).collection("messages")
            docs = messages_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(MAX_HISTORY).stream()
            history = [
                {"role": d["role"], "content": d["content"]}
                for d in (doc.to_dict() for doc in docs)
                if "role" in d and "content" in d
            ]
            history.reverse()  # DESC → 正序

        # 2️⃣ 新增當前使用者輸入
        history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        # 3️⃣ 呼叫 OpenAI fine-tuned 模型
        print("🚀 呼叫 OpenAI 模型中...")
        resp = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.5,
            max_tokens=500
        )
        assistant_reply = resp.choices[0].message.content
        print("✅ OpenAI 回傳成功")

        # 4️⃣ 儲存到 Firestore
        if db:
            messages_ref.add({"role": "user", "content": user_input, "timestamp": firestore.SERVER_TIMESTAMP})
            messages_ref.add({"role": "assistant", "content": assistant_reply, "timestamp": firestore.SERVER_TIMESTAMP})

        # 5️⃣ 回傳前端
        return jsonify({"reply": assistant_reply})

    except Exception as e:
        traceback.print_exc()
        print("❌ 發生錯誤：", e)
        return jsonify({"error": str(e)}), 500


# -----------------------------
# 啟動伺服器
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
