import os
import random
import traceback
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# 初始化 Flask & OpenAI
app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_ID = os.getenv("FINE_TUNED_MODEL")  # 你的 fine-tuned 模型 ID

# 讀取系統提示語
with open("prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

# 初始化 Firebase
firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not firebase_json:
    raise RuntimeError("缺少環境變數 FIREBASE_SERVICE_ACCOUNT")

cred = credentials.Certificate(json.loads(firebase_json))
firebase_admin.initialize_app(cred)
db = firestore.client()

MAX_HISTORY = 10  # 只保留最近 10 筆

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_id = data.get("user_id", "default")
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "message is required"}), 400

    try:
        # 1. 從 Firestore 抓最近 10 筆
        messages_ref = db.collection("conversations").document(user_id).collection("messages")
        docs = messages_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(MAX_HISTORY).stream()

        # 2. 只取 role + content，去掉 timestamp
        history = [
            {"role": d["role"], "content": d["content"]}
            for d in (doc.to_dict() for doc in docs)
            if "role" in d and "content" in d
        ]
        history.reverse()  # DESCENDING → 要反轉成時間順序

        # 3. 加上這次的使用者訊息
        history.append({"role": "user", "content": user_input})

        # 4. 準備要送進模型的 messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        # 5. 呼叫 fine-tuned 模型
        resp = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            temperature=0.5,
            max_tokens=500
        )

        assistant_reply = resp.choices[0].message.content

        # 6. 把這次對話存回 Firestore
        messages_ref.add({"role": "user", "content": user_input, "timestamp": firestore.SERVER_TIMESTAMP})
        messages_ref.add({"role": "assistant", "content": assistant_reply, "timestamp": firestore.SERVER_TIMESTAMP})

        return jsonify({"reply": assistant_reply})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/init", methods=["GET"])
def init():
    try:
        greetings = [
            "你好呀！今天想和我聊點什麼呢？😊",
            "嗨嗨～ 有甚麼想跟我討論的嗎？",
            "啊囉哈！🌟 最近在學什麼呢？我們一起討論啊~ ",
            "嘿～👋 今天我們要一起討論什麼？是感知器、決策樹，還是線性迴歸之類的呢？",
            "嗨～很高興見到你！😄 你想從哪個主題開始聊聊呢？",
            "Hey Yo！🎉 今天要聊點什麼？ 你的夥伴已上線～"
        ]

        greeting = random.choice(greetings)
        return jsonify({"reply": greeting})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

