# ClipSync 📋

Cihazlar arası gerçek zamanlı clipboard senkronizasyon uygulaması.

## Özellikler

- 🔄 Gerçek zamanlı senkronizasyon (Socket.io)
- 🔐 JWT tabanlı kullanıcı sistemi
- 📱 Mobil uyumlu responsive tasarım
- 🤖 Python masaüstü agent (otomatik Ctrl+C yakalama)
- 📖 Son 100 clipboard geçmişi
- 🗑 Tek tek veya toplu silme

## Proje Yapısı

```
clipSync/
├── backend/
│   ├── middleware/
│   │   └── auth.js          # JWT doğrulama
│   ├── models/
│   │   ├── User.js          # Kullanıcı modeli
│   │   └── Clipboard.js     # Clipboard modeli
│   ├── routes/
│   │   ├── auth.js          # Kayıt/giriş route'ları
│   │   └── clipboard.js     # Clipboard CRUD route'ları
│   ├── server.js            # Ana sunucu + Socket.io
│   ├── package.json
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthPage.js  # Giriş/kayıt sayfası
│   │   │   └── Dashboard.js # Ana uygulama
│   │   ├── context/
│   │   │   └── AuthContext.js
│   │   ├── hooks/
│   │   │   └── useSocket.js
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
└── agent/
    ├── agent.py             # Python masaüstü agent
    ├── requirements.txt
    └── .env.example
```

## Kurulum

### Gereksinimler

- Node.js 18+
- MongoDB (yerel veya MongoDB Atlas)
- Python 3.8+ (masaüstü agent için)

---

### 1. Backend

```bash
cd backend
npm install
cp .env.example .env
# .env dosyasını düzenle (MongoDB URI ve JWT_SECRET)
npm run dev
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

Frontend http://localhost:3000 adresinde açılacak.

### 3. Masaüstü Agent (İsteğe bağlı)

```bash
cd agent
pip install -r requirements.txt
cp .env.example .env
# .env dosyasına API_URL ve (isteğe bağlı) CLIPSYNC_TOKEN ekle
python agent.py
```

Agent ilk çalıştırmada e-posta ve şifre isteyecek, ardından clipboard'u izlemeye başlayacak.

---

## Kullanım

1. Tarayıcıdan http://localhost:3000 aç
2. Hesap oluştur veya giriş yap
3. Kopyaladığın metni textarea'ya yapıştır (Ctrl+V) → Kaydet & Senkronize Et
4. Aynı hesapla giriş yapan diğer cihazlarda anında görünür

### Kısayollar

- `Ctrl+V` – Metni otomatik textarea'ya yapıştırır (sayfa odaklanmışsa)
- `Ctrl+Enter` – Aktif textarea'dayken kaydet
- Masaüstü agent açıksa, `Ctrl+C` yaptığın her metin otomatik senkronize edilir

---

## API Endpoint'leri

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
| clipboard:new | Server → Client | Yeni clipboard girişi |
| clipboard:deleted | Server → Client | Giriş silindi |
| clipboard:cleared | Server → Client | Tümü silindi |

## Üretim Ortamı İçin

1. `.env`'de `JWT_SECRET`'i güçlü bir değerle değiştir
2. MongoDB Atlas kullan
3. `CLIENT_URL`'i production domain'inle güncelle
4. Frontend'i build et: `npm run build`
5. Nginx veya benzeri bir reverse proxy kullan
