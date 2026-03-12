#!/usr/bin/env python3
"""
ClipSync Desktop Agent
Monitors clipboard changes and syncs to ClipSync backend.
"""

import time
import os
import sys
import requests
import pyperclip
import socketio
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:5000")
TOKEN = os.getenv("CLIPSYNC_TOKEN", "")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))  # seconds

sio = socketio.Client()
last_text = ""
connected_socket = False


def get_token():
    """Get token from env or prompt user."""
    token = TOKEN
    if not token:
        print("ClipSync Desktop Agent")
        print("=" * 40)
        email = input("E-posta: ").strip()
        password = input("Şifre: ").strip()
        try:
            res = requests.post(
                f"{API_URL}/api/auth/login",
                json={"email": email, "password": password},
                timeout=10,
            )
            res.raise_for_status()
            token = res.json()["token"]
            print(f"\n✓ Giriş başarılı!")
            print(f"Token'ı .env dosyasına kaydedebilirsiniz: CLIPSYNC_TOKEN={token}\n")
        except requests.exceptions.RequestException as e:
            print(f"✗ Giriş başarısız: {e}")
            sys.exit(1)
    return token


def push_clipboard(text, token):
    """Send clipboard text to backend."""
    try:
        res = requests.post(
            f"{API_URL}/api/clipboard",
            json={"text": text, "source": "desktop-agent"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        res.raise_for_status()
        print(f"[SYNC] Gönderildi: {text[:60]}{'...' if len(text) > 60 else ''}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Gönderilemedi: {e}")


def connect_socket(token):
    """Connect to Socket.io for real-time updates."""
    global connected_socket
    try:
        sio.connect(API_URL, auth={"token": token}, transports=["websocket"])
        connected_socket = True

        @sio.on("clipboard:new")
        def on_new(data):
            if data.get("source") != "desktop-agent":
                print(f"[INCOMING] Yeni metin: {data.get('text', '')[:60]}")

        @sio.on("disconnect")
        def on_disconnect():
            global connected_socket
            connected_socket = False
            print("[SOCKET] Bağlantı kesildi")

        print("[SOCKET] Bağlandı")
    except Exception as e:
        print(f"[SOCKET] Bağlanamadı: {e}")


def main():
    global last_text

    token = get_token()

    print("ClipSync Desktop Agent başlatılıyor...")
    print(f"Sunucu: {API_URL}")
    print(f"Kontrol aralığı: {POLL_INTERVAL}s")
    print("Durdurmak için Ctrl+C\n")

    connect_socket(token)

    # Initialize with current clipboard content
    try:
        last_text = pyperclip.paste()
    except Exception:
        last_text = ""

    print("Clipboard izleniyor...\n")

    try:
        while True:
            try:
                current_text = pyperclip.paste()
                if current_text and current_text != last_text and len(current_text.strip()) > 0:
                    last_text = current_text
                    push_clipboard(current_text, token)
            except Exception as e:
                print(f"[ERROR] Clipboard okuma hatası: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nAgent durduruldu.")
        if connected_socket:
            sio.disconnect()


if __name__ == "__main__":
    main()
