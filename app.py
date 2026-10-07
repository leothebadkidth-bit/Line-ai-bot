from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    return "LINE AI Bot is running!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    return "OK", 200
