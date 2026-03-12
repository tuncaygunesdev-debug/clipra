#!/usr/bin/env python3
"""Clipra Desktop Agent"""

import tkinter as tk
import tkinter.ttk
import threading
import time
import requests
import pyperclip
import json
import os
import sys
from PIL import Image, ImageDraw
import pystray

API_URL = "https://clipsync-production-1778.up.railway.app"
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".clipra_config.json")

BG      = "#080810"
SURFACE = "#12121f"
SURFACE2= "#1a1a2e"
ACCENT  = "#5b4eff"
RED     = "#ff4d6d"
TEXT    = "#f0f0ff"
MUTED   = "#5a5a8a"
BORDER  = "#1e1e35"
GREEN   = "#00d68f"

state = {"token": None, "user": None, "running": False, "last_clip": ""}
_tk_root = None

# ── Config ────────────────────────────────────────────────
def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"token": state["token"], "user": state["user"]}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                state["token"] = data.get("token")
                state["user"] = data.get("user")
        except Exception:
            pass

def clear_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    state["token"] = None
    state["user"] = None

# ── API ───────────────────────────────────────────────────
def api_login(email, password):
    r = requests.post(f"{API_URL}/api/auth/login",
                      json={"email": email, "password": password}, timeout=10)
    r.raise_for_status()
    return r.json()

def api_push(text):
    r = requests.post(f"{API_URL}/api/clipboard",
                      json={"text": text, "source": "desktop-agent"},
                      headers={"Authorization": f"Bearer {state['token']}"}, timeout=10)
    r.raise_for_status()

def api_get_history():
    r = requests.get(f"{API_URL}/api/clipboard",
                     headers={"Authorization": f"Bearer {state['token']}"}, timeout=10)
    r.raise_for_status()
    return r.json()

def api_delete(entry_id):
    r = requests.delete(f"{API_URL}/api/clipboard/{entry_id}",
                        headers={"Authorization": f"Bearer {state['token']}"}, timeout=10)
    r.raise_for_status()

def verify_token():
    try:
        r = requests.get(f"{API_URL}/api/clipboard",
                         headers={"Authorization": f"Bearer {state['token']}"}, timeout=5)
        return r.status_code == 200
    except Exception:
        return False

# ── Clipboard Watcher ─────────────────────────────────────
def clipboard_watcher():
    try:
        state["last_clip"] = pyperclip.paste()
    except Exception:
        state["last_clip"] = ""
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

# ── Tray Icon ─────────────────────────────────────────────
def create_tray_icon():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, 63, 63], radius=14, fill=(91, 78, 255, 255))
    draw.rectangle([10, 10, 26, 26], fill=(255, 255, 255, 230))
    draw.rectangle([10, 38, 26, 54], fill=(255, 255, 255, 230))
    draw.rectangle([38, 10, 54, 26], fill=(255, 255, 255, 230))
    draw.line([38, 46, 54, 46], fill=(255, 255, 255, 230), width=3)
    draw.line([46, 38, 46, 54], fill=(255, 255, 255, 230), width=3)
    return img

def get_tk_icon():
    import io, base64
    img = create_tray_icon()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()

# ── Sürüklenebilir Pencere ────────────────────────────────
def make_draggable(widget, window):
    def start(e):
        window._drag_x = e.x
        window._drag_y = e.y
    def drag(e):
        x = window.winfo_x() + e.x - window._drag_x
        y = window.winfo_y() + e.y - window._drag_y
        window.geometry(f"+{x}+{y}")
    widget.bind("<ButtonPress-1>", start)
    widget.bind("<B1-Motion>", drag)

# ── History Penceresi ─────────────────────────────────────
def show_history_window(icon=None, item=None):
    global _tk_root
    if _tk_root is None:
        return

    def _build():
        win = tk.Toplevel(_tk_root)
        win.overrideredirect(True)         # Sistem başlık çubuğunu kaldır
        win.geometry("500x560")
        win.configure(bg=BORDER)           # Çerçeve rengi (yuvarlak için)
        win.resizable(False, False)
        win.attributes("-topmost", False)

        # Ortala
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 250
        y = (win.winfo_screenheight() // 2) - 280
        win.geometry(f"500x560+{x}+{y}")

        # Dış çerçeve (yuvarlak köşe efekti için 1px border)
        outer = tk.Frame(win, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        # İç ana container
        main = tk.Frame(outer, bg=BG)
        main.pack(fill="both", expand=True)

        # ── Özel Başlık Çubuğu ──
        titlebar = tk.Frame(main, bg=SURFACE, height=46)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)

        tk.Label(titlebar, text="◻  Clipboard History", bg=SURFACE, fg=TEXT,
                 font=("Courier", 12, "bold")).pack(side="left", padx=14, pady=12)

        email = state["user"].get("email", "") if state["user"] else ""
        tk.Label(titlebar, text=email, bg=SURFACE, fg=MUTED,
                 font=("Courier", 9)).pack(side="left", padx=6, pady=12)

        # Kapat butonu
        close_btn = tk.Label(titlebar, text="✕", bg=SURFACE, fg=MUTED,
                             font=("Courier", 12), cursor="hand2", padx=14)
        close_btn.pack(side="right", pady=10)
        close_btn.bind("<Button-1>", lambda e: win.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=RED, bg="#1e0a0e"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=MUTED, bg=SURFACE))

        make_draggable(titlebar, win)

        # Ayraç
        tk.Frame(main, bg=BORDER, height=1).pack(fill="x")

        # ── Liste ──
        list_frame = tk.Frame(main, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = tkinter.ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Vertical.TScrollbar",
                        background=SURFACE2,
                        troughcolor=BG,
                        bordercolor=BG,
                        arrowcolor=MUTED,
                        darkcolor=SURFACE2,
                        lightcolor=SURFACE2,
                        relief="flat")
        style.map("Dark.Vertical.TScrollbar",
                  background=[("active", ACCENT)])

        sb = tkinter.ttk.Scrollbar(list_frame, style="Dark.Vertical.TScrollbar")
        sb.pack(side="right", fill="y", padx=(2, 0))

        lb = tk.Listbox(list_frame, bg=SURFACE, fg=TEXT,
                        font=("Courier", 11),
                        selectbackground=ACCENT, selectforeground="white",
                        yscrollcommand=sb.set,
                        borderwidth=0, highlightthickness=0,
                        activestyle="none", relief="flat")
        lb.pack(fill="both", expand=True)
        sb.config(command=lb.yview)

        entries = []

        # ── Status ──
        status_var = tk.StringVar(value="")
        tk.Label(main, textvariable=status_var, bg=BG, fg=GREEN,
                 font=("Courier", 10)).pack(pady=(0, 4))

        def load():
            lb.delete(0, tk.END)
            entries.clear()
            status_var.set("Loading...")
            try:
                data = api_get_history()
                for e in data:
                    preview = e["text"][:85].replace("\n", " ↵ ")
                    lb.insert(tk.END, f"  {preview}")
                    entries.append(e)
                status_var.set(f"{len(entries)} entries")
            except Exception as ex:
                status_var.set(f"Error: {str(ex)[:60]}")

        def copy_selected(event=None):
            sel = lb.curselection()
            if not sel or not entries:
                return
            pyperclip.copy(entries[sel[0]]["text"])
            state["last_clip"] = entries[sel[0]]["text"]
            status_var.set("✓ Copied!")
            win.after(2000, lambda: status_var.set(f"{len(entries)} entries"))

        def delete_selected():
            sel = lb.curselection()
            if not sel or not entries:
                return
            try:
                api_delete(entries[sel[0]]["_id"])
                load()
            except Exception as ex:
                status_var.set(f"Error: {str(ex)[:60]}")

        lb.bind("<Double-Button-1>", copy_selected)

        # ── Butonlar ──
        btn_frame = tk.Frame(main, bg=BG)
        btn_frame.pack(fill="x", padx=10, pady=(0, 12))

        def btn(parent, text, color, cmd):
            b = tk.Label(parent, text=text, bg=color, fg="white",
                         font=("Courier", 10, "bold"), cursor="hand2",
                         padx=14, pady=7)
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>", lambda e, c=color: b.config(bg=_lighten(c)))
            b.bind("<Leave>", lambda e, c=color: b.config(bg=c))
            return b

        def _lighten(hex_color):
            return {"#5b4eff": "#7066ff", "#ff4d6d": "#ff6b82", "#1a1a2e": "#2a2a45"}.get(hex_color, hex_color)

        btn(btn_frame, "Copy", ACCENT, copy_selected).pack(side="left", padx=(0, 6))
        btn(btn_frame, "Delete", RED, delete_selected).pack(side="left", padx=6)
        btn(btn_frame, "Refresh", SURFACE2, load).pack(side="left", padx=6)

        threading.Thread(target=load, daemon=True).start()
        win.lift()
        win.focus_force()

    _tk_root.after(0, _build)

# ── Tray Menüsü ───────────────────────────────────────────
def logout_action(icon, item):
    state["running"] = False
    clear_config()
    icon.stop()
    os.execv(sys.executable, [sys.executable] + sys.argv)

def quit_action(icon, item):
    state["running"] = False
    icon.stop()
    os._exit(0)

def start_tray():
    global _tk_root
    image = create_tray_icon()
    email = state["user"].get("email", "User") if state["user"] else "User"

    menu = pystray.Menu(
        pystray.MenuItem(f"Clipra  ·  {email}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("View History", show_history_window),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sign out", logout_action),
        pystray.MenuItem("Quit", quit_action),
    )

    icon = pystray.Icon("Clipra", image, "Clipra", menu)
    state["tray_icon"] = icon

    state["running"] = True
    threading.Thread(target=clipboard_watcher, daemon=True).start()
    threading.Thread(target=icon.run, daemon=True).start()

    _tk_root = tk.Tk()
    _tk_root.withdraw()
    _tk_root.mainloop()

# ── Giriş Penceresi ───────────────────────────────────────
def show_login_window():
    global _tk_root
    root = tk.Tk()
    _tk_root = root
    root.title("Clipra")
    root.geometry("380x480")
    root.configure(bg=BG)
    root.resizable(False, False)
    try:
        _icon_data = get_tk_icon()
        _icon_photo = tk.PhotoImage(data=_icon_data)
        root.iconphoto(True, _icon_photo)
        root._icon_photo = _icon_photo
    except Exception:
        pass
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 190
    y = (root.winfo_screenheight() // 2) - 240
    root.geometry(f"380x480+{x}+{y}")

    tk.Frame(root, bg=BG, height=20).pack()

    logo_frame = tk.Frame(root, bg=ACCENT, width=52, height=52)
    logo_frame.pack()
    logo_frame.pack_propagate(False)
    tk.Label(logo_frame, text="◻", bg=ACCENT, fg="white",
             font=("Courier", 22, "bold")).pack(expand=True)

    tk.Frame(root, bg=BG, height=12).pack()
    tk.Label(root, text="Clipra", bg=BG, fg=TEXT,
             font=("Courier", 22, "bold")).pack()
    tk.Label(root, text="Clipboard sync across all devices",
             bg=BG, fg=MUTED, font=("Courier", 9)).pack(pady=(4, 28))

    form = tk.Frame(root, bg=BG)
    form.pack(padx=40, fill="x")

    def field(label_text, show=None):
        tk.Label(form, text=label_text, bg=BG, fg=MUTED,
                 font=("Courier", 9), anchor="w").pack(fill="x")
        var = tk.StringVar()
        e = tk.Entry(form, textvariable=var, bg=SURFACE, fg=TEXT,
                     font=("Courier", 12), relief="flat",
                     insertbackground=TEXT,
                     highlightthickness=1,
                     highlightcolor=ACCENT,
                     highlightbackground=BORDER)
        if show:
            e.config(show=show)
        e.pack(fill="x", ipady=9, pady=(3, 14))
        return var, e

    email_var, email_entry = field("EMAIL")
    pass_var, pass_entry = field("PASSWORD", show="●")

    status_var = tk.StringVar()
    tk.Label(form, textvariable=status_var, bg=BG, fg=RED,
             font=("Courier", 10)).pack()

    def do_login():
        email = email_var.get().strip()
        password = pass_var.get().strip()
        if not email or not password:
            status_var.set("Email and password required")
            return
        login_btn.config(text="Signing in...", state="disabled")
        status_var.set("")

        def _login():
            try:
                data = api_login(email, password)
                state["token"] = data["token"]
                state["user"] = data["user"]
                save_config()
                root.after(0, lambda: (root.destroy(), start_tray()))
            except Exception:
                root.after(0, lambda: (
                    status_var.set("Invalid email or password"),
                    login_btn.config(text="Sign in", state="normal")
                ))

        threading.Thread(target=_login, daemon=True).start()

    tk.Frame(root, bg=BG, height=6).pack()
    login_btn = tk.Button(
        form, text="Sign in", bg=ACCENT, fg="white",
        font=("Courier", 12, "bold"), relief="flat",
        activebackground="#7066ff", activeforeground="white",
        cursor="hand2", pady=11, command=do_login, borderwidth=0)
    login_btn.pack(fill="x", pady=(8, 0))

    pass_entry.bind("<Return>", lambda e: do_login())
    email_entry.bind("<Return>", lambda e: pass_entry.focus())
    email_entry.focus()
    root.mainloop()

# ── Başlangıç ─────────────────────────────────────────────
if __name__ == "__main__":
    load_config()
    if state["token"]:
        if verify_token():
            start_tray()
        else:
            clear_config()
            show_login_window()
    else:
        show_login_window()
