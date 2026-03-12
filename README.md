# Clipra 📋

Cihazlar arası gerçek zamanlı clipboard senkronizasyon uygulaması.

🌐 **Web:** https://clipra.up.railway.app
⬇️ **Windows Agent:** [Clipra.exe indir](https://github.com/tuncaygunesdev-debug/clipra/releases/download/v1.0.0/Clipra.exe)

---

## Özellikler

- ⚡ Gerçek zamanlı senkronizasyon (Socket.io)
- 🔐 JWT tabanlı kullanıcı sistemi
- 📱 Responsive koyu tema arayüz
- 🖥️ Windows masaüstü agent (otomatik Ctrl+C yakalama)
- 📖 Son 100 clipboard geçmişi
- 🗑️ Tek tek veya toplu silme

---

## Nasıl Kullanılır?

1. https://clipra.up.railway.app adresine git
2. Hesap oluştur veya giriş yap
3. Kopyaladığın metni yapıştır → **Save & sync** butonuna bas
4. Aynı hesapla giriş yapan diğer cihazlarda anında görünür

### Windows Agent
Ctrl+C yaptığın her metni otomatik senkronize etmek için:

1. [Clipra.exe](https://github.com/tuncaygunesdev-debug/clipra/releases/download/v1.0.0/Clipra.exe) dosyasını indir
2. Çift tıkla, e-posta ve şifrenle giriş yap
3. Sistem tepsisinde çalışmaya devam eder

---

## Proje Yapısı

```
clipra/
├── backend/
│   ├── middleware/auth.js       # JWT doğrulama
│   ├── models/
│   │   ├── User.js              # Kullanıcı modeli
│   │   └── Clipboard.js         # Clipboard modeli (max 100)
│   ├── routes/
│   │   ├── auth.js              # Kayıt / giriş
│   │   └── clipboard.js         # CRUD + Socket.io
│   ├── server.js                # Ana sunucu
│   └── .env.example
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.svg
│   └── src/
│       ├── components/
│       │   ├── AuthPage.js      # Giriş / kayıt
│       │   └── Dashboard.js     # Ana uygulama
│       ├── context/AuthContext.js
│       ├── hooks/useSocket.js
│       ├── App.js
│       └── App.css
└── agent/
    ├── clipra_agent.py          # Windows tray uygulaması
    └── requirements.txt
```

---

## Kendi Sunucuna Kur

### Gereksinimler
- Node.js 18+
- MongoDB (yerel veya Atlas)
- Python 3.8+ (agent için)

### Backend
```bash
cd backend
npm install
cp .env.example .env
# .env dosyasını düzenle
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Agent
```bash
cd agent
pip install -r requirements.txt
py clipra_agent.py
```

---

## API

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | /api/auth/register | Kayıt |
| POST | /api/auth/login | Giriş |
| GET | /api/clipboard | Geçmişi getir |
| POST | /api/clipboard | Yeni ekle |
| DELETE | /api/clipboard/:id | Sil |
| DELETE | /api/clipboard | Tümünü sil |

## Socket.io Events

| Event | Yön | Açıklama |
|-------|-----|----------|
| clipboard:new | Server → Client | Yeni giriş |
| clipboard:deleted | Server → Client | Giriş silindi |
| clipboard:cleared | Server → Client | Tümü silindi |

---

## Teknolojiler

**Backend:** Node.js, Express, Socket.io, MongoDB, JWT  
**Frontend:** React, Axios, Socket.io-client  
**Agent:** Python, pystray, Pillow, tkinter  
**Deploy:** Railway, MongoDB Atlas
