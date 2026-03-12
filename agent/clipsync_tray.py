#!/usr/bin/env python3
"""
ClipSync Windows Tray Uygulaması
- Giriş ekranı ile başlar
- Sistem tepsisinde çalışır
- Arka planda clipboard izler
- Tepsi menüsünden geçmişe erişim
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
import pyperclip
import json
import os
import sys
from PIL import Image, ImageDraw
import pystray

# ─── Ayarlar ─────────────────────────────────────────────
API_URL = "https://clipsync-production-1778.up.railway.app"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".clipsync_config.json")

# ─── Durum ───────────────────────────────────────────────
state = {
    "token": None,
    "user": None,
    "running": False,
    "last_clip": "",
}

# ─── Config kaydet/yükle ─────────────────────────────────
def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"token": state["token"], "user": state["user"]}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
            state["token"] = data.get("token")
            state["user"] = data.get("user")

def clear_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    state["token"] = None
    state["user"] = None

# ─── API İşlemleri ───────────────────────────────────────
def api_login(email, password):
    res = requests.post(f"{API_URL}/api/auth/login", json={"email": email, "password": password}, timeout=10)
    res.raise_for_status()
    return res.json()

def api_push(text):
    headers = {"Authorization": f"Bearer {state['token']}"}
    res = requests.post(f"{API_URL}/api/clipboard", json={"text": text, "source": "desktop-agent"}, headers=headers, timeout=10)
    res.raise_for_status()
    return res.json()

def api_get_history():
    headers = {"Authorization": f"Bearer {state['token']}"}
    res = requests.get(f"{API_URL}/api/clipboard", headers=headers, timeout=10)
    res.raise_for_status()
    return res.json()

def api_delete(entry_id):
    headers = {"Authorization": f"Bearer {state['token']}"}
    res = requests.delete(f"{API_URL}/api/clipboard/{entry_id}", headers=headers, timeout=10)
    res.raise_for_status()

# ─── Clipboard İzleyici ──────────────────────────────────
def clipboard_watcher():
    state["last_clip"] = pyperclip.paste()
    while state["running"]:
        try:
            current = pyperclip.paste()
            if current and current != state["last_clip"] and state["token"]:
                state["last_clip"] = current
                try:
                    api_push(current)
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(1)

# ─── Tepsi İkonu ─────────────────────────────────────────
def create_icon_image():
    img = Image.new("RGB", (64, 64), color=(13, 13, 26))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=(108, 99, 255))
    draw.text((20, 18), "C", fill="white")
    return img

def show_history_window(icon=None, item=None):
    def _open():
        root = tk.Tk()
        root.title("Clipra — History")
        root.geometry("520x560")
        root.configure(bg="#080810")
        root.lift()
        root.focus_force()

        tk.Label(root, text="Clipboard History", bg="#080810", fg="#f0f0ff",
                 font=("Inter", 14, "bold")).pack(pady=14)

        frame = tk.Frame(root, bg="#080810")
        frame.pack(fill="both", expand=True, padx=14, pady=4)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, bg="#12121f", fg="#f0f0ff", font=("Courier", 10),
                             selectbackground="#5b4eff", yscrollcommand=scrollbar.set,
                             borderwidth=0, highlightthickness=0, activestyle="none")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        entries = []

        def load():
            listbox.delete(0, tk.END)
            entries.clear()
            try:
                data = api_get_history()
                for e in data:
                    text = e["text"][:90].replace("\n", " ")
                    listbox.insert(tk.END, f"  {text}")
                    entries.append(e)
            except Exception as ex:
                listbox.insert(tk.END, f"Error: {ex}")

        def copy_selected():
            sel = listbox.curselection()
            if sel and entries:
                pyperclip.copy(entries[sel[0]]["text"])
                state["last_clip"] = entries[sel[0]]["text"]
                tk.messagebox.showinfo("Clipra", "Copied!", parent=root)

        def delete_selected():
            sel = listbox.curselection()
            if sel and entries:
                try:
                    api_delete(entries[sel[0]]["_id"])
                    load()
                except Exception as ex:
                    tk.messagebox.showerror("Error", str(ex), parent=root)

        btn_frame = tk.Frame(root, bg="#080810")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Copy", bg="#5b4eff", fg="white",
                  font=("Inter", 10), relief="flat", padx=14, pady=7,
                  command=copy_selected, cursor="hand2").pack(side="left", padx=6)

        tk.Button(btn_frame, text="Delete", bg="#ff4d6d", fg="white",
                  font=("Inter", 10), relief="flat", padx=14, pady=7,
                  command=delete_selected, cursor="hand2").pack(side="left", padx=6)

        tk.Button(btn_frame, text="Refresh", bg="#1a1a2e", fg="#f0f0ff",
                  font=("Inter", 10), relief="flat", padx=14, pady=7,
                  command=load, cursor="hand2").pack(side="left", padx=6)

        load()
        root.mainloop()

    threading.Thread(target=_open, daemon=True).start()
```

Değiştirdikten sonra tekrar exe oluştur:
```
py -m PyInstaller --onefile --windowed --name "Clipra" clipsync_tray.py
# ─── Giriş Penceresi ─────────────────────────────────────
def show_login_window():
    root = tk.Tk()
    root.title("Clipra")
    root.geometry("380x460")
    root.configure(bg="#0d0d1a")
    root.resizable(False, False)

    # Ortala
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (380 // 2)
    y = (root.winfo_screenheight() // 2) - (460 // 2)
    root.geometry(f"380x460+{x}+{y}")

    # Logo
    tk.Label(root, text="⌘", bg="#0d0d1a", fg="#6c63ff",
             font=("Courier", 40)).pack(pady=(30, 5))
    tk.Label(root, text="Clipra", bg="#0d0d1a", fg="#e2e8f0",
             font=("Courier", 22, "bold")).pack()
    tk.Label(root, text="Cihazlar arası clipboard senkronizasyonu",
             bg="#0d0d1a", fg="#7c8db5", font=("Courier", 9)).pack(pady=(4, 24))

    # Form
    form = tk.Frame(root, bg="#0d0d1a")
    form.pack(padx=40, fill="x")

    tk.Label(form, text="E-posta", bg="#0d0d1a", fg="#7c8db5",
             font=("Courier", 10)).pack(anchor="w")
    email_var = tk.StringVar()
    email_entry = tk.Entry(form, textvariable=email_var, bg="#13132a", fg="#e2e8f0",
                           font=("Courier", 11), relief="flat", insertbackground="white",
                           highlightthickness=1, highlightcolor="#6c63ff",
                           highlightbackground="#2a2a50")
    email_entry.pack(fill="x", ipady=8, pady=(4, 14))

    tk.Label(form, text="Şifre", bg="#0d0d1a", fg="#7c8db5",
             font=("Courier", 10)).pack(anchor="w")
    pass_var = tk.StringVar()
    pass_entry = tk.Entry(form, textvariable=pass_var, show="●", bg="#13132a", fg="#e2e8f0",
                          font=("Courier", 11), relief="flat", insertbackground="white",
                          highlightthickness=1, highlightcolor="#6c63ff",
                          highlightbackground="#2a2a50")
    pass_entry.pack(fill="x", ipady=8, pady=(4, 20))

    status_label = tk.Label(form, text="", bg="#0d0d1a", fg="#ff6584",
                             font=("Courier", 9))
    status_label.pack()

    def do_login():
        email = email_var.get().strip()
        password = pass_var.get().strip()
        if not email or not password:
            status_label.config(text="E-posta ve şifre gerekli")
            return

        login_btn.config(text="Giriş yapılıyor...", state="disabled")
        status_label.config(text="")

        def _login():
            try:
                data = api_login(email, password)
                state["token"] = data["token"]
                state["user"] = data["user"]
                save_config()
                root.after(0, lambda: (root.destroy(), start_tray()))
            except Exception as e:
                msg = "Hatalı e-posta veya şifre"
                root.after(0, lambda: (
                    status_label.config(text=msg),
                    login_btn.config(text="Giriş Yap", state="normal")
                ))

        threading.Thread(target=_login, daemon=True).start()

    login_btn = tk.Button(form, text="Giriş Yap", bg="#6c63ff", fg="white",
                          font=("Courier", 12, "bold"), relief="flat",
                          activebackground="#7c75ff", activeforeground="white",
                          cursor="hand2", pady=10, command=do_login)
    login_btn.pack(fill="x", pady=(8, 0))

    pass_entry.bind("<Return>", lambda e: do_login())
    email_entry.bind("<Return>", lambda e: pass_entry.focus())
    email_entry.focus()

    root.mainloop()

# ─── Ana Giriş ───────────────────────────────────────────
if __name__ == "__main__":
    load_config()

    # Daha önce giriş yapılmışsa direkt tepside başlat
    if state["token"]:
        try:
            # Token geçerli mi test et
            headers = {"Authorization": f"Bearer {state['token']}"}
            r = requests.get(f"{API_URL}/api/clipboard", headers=headers, timeout=5)
            if r.status_code == 200:
                # Tkinter root oluştur (arka planda)
                root = tk.Tk()
                root.withdraw()
                start_tray()
            else:
                clear_config()
                show_login_window()
        except Exception:
            show_login_window()
    else:
        show_login_window()
