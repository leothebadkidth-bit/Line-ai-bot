v1beta os
import requests
from flask import Flask, request

app = Flask(__name__)

LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def home():
    return "LINE AI Bot is running!", 200


def ask_gemini(text):
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.8-flash:generateContent"
    )

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        ]
    }

    response = requests.post(
        url,
        params={"key": GEMINI_KEY},
        json=data,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return result["candidates"][0]["content"]["parts"][0]["text"]


def reply_line(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }

    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text[:5000]
            }
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30
    )

    response.raise_for_status()


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        return "OK", 200

    data = request.get_json(silent=True) or {}

    for event in data.get("events", []):

        if (
            event.get("type") == "message"
            and event.get("message", {}).get("type") == "text"
        ):

            reply_token = event.get("replyToken")
            user_text = event["message"]["text"]

            try:
                answer = ask_gemini(user_text)

            except Exception as e:
                print("Gemini error:", e)
                answer = "ขอโทษนะ ตอนนี้ฉันมีปัญหาชั่วคราว ลองส่งข้อความอีกครั้งนะ"

            if reply_token:
                try:
                    reply_line(reply_token, answer)

                except Exception as e:
                    print("LINE error:", e)

    return "OK", 200
