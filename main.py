from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

user_state = {}
question_set = {
    "q1": "หน่วยงานของคุณคือประเภทใด?\n1. ส่วนราชการ\n2. อปท.\n3. องค์การมหาชน\n4. รัฐวิสาหกิจ",
    "q2": "โครงการของคุณมีลักษณะใด?\n1. พัฒนาการบริหารจัดการองค์กร\n2. การให้บริการประชาชน\n3. การส่งเสริมการมีส่วนร่วม",
    "q3": "ดำเนินมาแล้วเกิน 1 ปีหรือไม่?\n1. ใช่\n2. ไม่ใช่"
}

result_logic = {
    ("1", "1", "1"): "✅ คุณเหมาะกับรางวัล PMQA",
    ("2", "2", "1"): "✅ คุณเหมาะกับรางวัลบริการภาครัฐ",
    ("3", "3", "1"): "✅ คุณเหมาะกับรางวัลบริหารราชการแบบมีส่วนร่วม"
}

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if user_id not in user_state:
        user_state[user_id] = {"step": 0, "answers": []}
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=question_set["q1"]))
        return

    state = user_state[user_id]
    state["answers"].append(text)
    state["step"] += 1

    if state["step"] == 1:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=question_set["q2"]))
    elif state["step"] == 2:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=question_set["q3"]))
    elif state["step"] == 3:
        key = tuple(state["answers"])
        result = result_logic.get(key, "❗ ยังไม่ตรงกับรางวัลใดโดยเฉพาะ")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        user_state.pop(user_id)
