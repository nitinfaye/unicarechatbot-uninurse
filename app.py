# import sys
from flask import Flask, render_template, request, jsonify
# import numpy as np
import requests
from random import randint
import time
# from db.mongo import Person
from addons.sender_id import SenderID
from db import Conversation

from functools import lru_cache


def save_convo(resp, name, phone, flow, sender_id):
    C1 = Conversation.Conversation(sender_id=sender_id, name=name, flow=flow, phone=phone, convo=resp)
    C1.addToDB()


# Function that computes sender ID
# with lru_cache
# @lru_cache(maxsize=512)
# def get_sender_id(name, phone, type):
#     sender_id = randint(1000, 10000)
#     print(f"get_sender_id : name = {name}, phone = {phone}, type = {type}, sender = {sender_id}")
#     return sender_id


# _name = "Nitin"
# _phone = 9873664005
# _type = None
# sender = randint(1000, 10000)
app = Flask(__name__)


# def restart_session():
#     global sender
#     sender = randint(10000, 100000)
#     print(f"\nSender id reset to {sender}\n")
#     return "Success"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat/<string:user_name>/<string:user_phone>/<string:user_flow>/<string:user_text>")
def chat_bot_response(user_name, user_phone, user_flow, user_text):
    user_name = user_name.strip()
    user_phone = user_phone.strip()
    user_text = user_text.strip()
    user_flow = user_flow.strip()
    status, txt, htmlTxt = bot_response(user_name, user_phone, user_flow, user_text)
    D = {'status': status, 'resp': txt}
    return jsonify(D)


@app.route("/get/<string:user_name>/<string:user_phone>/<string:user_flow>/<string:user_text>")
def get_bot_response(user_name, user_phone, user_flow, user_text):
    user_name = user_name.strip()
    user_phone = user_phone.strip()
    user_text = user_text.strip()
    user_flow = user_flow.strip()
    status, txt, htmlTxt = bot_response(user_name, user_phone, user_flow, user_text)
    return htmlTxt


def bot_response(user_name, user_phone,  user_flow, user_text):
    sender_id = None
    text = []
    status = None
    return_this = None
    final_text = None
    try:
        # sender = get_sender_id(user_name, user_phone, user_flow)
        # print(f"\nCurrent input {sender}, {user_flow}, {user_text}, {user_name}, {user_phone} ")

        # if user_flow is not None and user_flow != _type:
        #     restart_session()
        # if user_flow is not None:
        #     _type = user_flow
        if user_flow is None:
            raise Exception("Incorrect flow is selected !!")

        if user_name is None or user_name.strip() == "":
            raise Exception("Name of Patient is Empty")

        if user_phone is None or user_phone.strip() == "":
            raise Exception("Mobile No. of Patient is Empty")

        sender_id = SenderID.createID(user_name, user_phone, user_flow)  # method to get sender_id

        metadata = {"message": user_text, "sender": sender_id, "name": user_name, "phone": user_phone, "flow": user_flow}
        print(f"{user_name} :{sender_id}: {user_text}")
        r = requests.post("http://localhost:5005/webhooks/myio/webhook", json=metadata)
        text = r.json()
        # print("*************** Response from RASA !!!!", text)
        final_text = ""
        for t in text:
            if t['text'] == "EOC":
                SenderID.removeID(user_name, user_phone, user_flow)  # method to remove sender_id
                print(f"EOC for {sender_id}")
            final_text += t['text'] + "\n"

        if final_text == "":
            raise Exception("Empty response !!")

        return_this = '<p class="botText"><span>' + final_text + '</span></p>'
        return_this = return_this.replace("\n", "<br>")
        # print(return_this)
        if len(text) > 0:
            for each in text:
                # print("each:::", each)
                if 'buttons' in each.keys():
                    buttons = each['buttons']
                    # for i in each:
                    #     buttons.extend(i['buttons'])
                    # print("Buttons")
                    # print(buttons)

                    for button in buttons:
                        # print(button)
                        return_this += '<button class="botButtons" mapto="' + button['payload'] +\
                            '" onclick="BotButtonClicked(this);">' + button['title']+'</button>'
        status = True

    except Exception as e:
        # print(f"Exception in response : {e}")
        final_text = f"Exception :: {e}"
        return_this = '<p class="botText"><span>' + final_text + '</span></p>'
        SenderID.removeID(user_name, user_phone, user_flow)  # method to remove sender_id
        status = False

    print(f"Bot :{sender_id}: {final_text}")
    return status, text, return_this


@app.route("/welcome_messages")
def welcome_messages():
    return "Hello, Welcome to the Chatbot"


@app.route("/restart")
def restart():
    return "Hello, Welcome to the Chatbot"


@app.route("/updatePatient")
def updatePatient():
    # global _name, _phone
    #
    # _name = request.args.get('name').strip()
    # _phone = request.args.get('phone').strip()
    # # restart_session()
    return "Hello, Welcome to the Chatbot"


if __name__ == "__main__":
    app.run(debug=True)
