import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { useSocket } from '../hooks/useSocket';

function formatTime(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  if (diff < 60000) return 'Az önce';
  if (diff < 3600000) return `${Math.floor(diff / 60000)} dk önce`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} sa önce`;
  return date.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

export default function Dashboard() {
  const { user, token, logout } = useAuth();
  const [entries, setEntries] = useState([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const textareaRef = useRef(null);

  const fetchEntries = useCallback(async () => {
    try {
      const res = await axios.get('/api/clipboard');
      setEntries(res.data);
    } catch {
      toast.error('Geçmiş yüklenemedi');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  // Clipboard paste detection
  useEffect(() => {
    const handlePaste = (e) => {
      if (document.activeElement === textareaRef.current) return;
      const pastedText = e.clipboardData?.getData('text');
      if (pastedText) setText(pastedText);
    };
    document.addEventListener('paste', handlePaste);
    return () => document.removeEventListener('paste', handlePaste);
  }, []);

  const onNew = useCallback((entry) => {
    setEntries((prev) => {
      if (prev.find((e) => e._id === entry._id)) return prev;
      return [entry, ...prev].slice(0, 100);
    });
    toast.success('Yeni clipboard girişi senkronize edildi', { icon: '📋' });
  }, []);

  const onDeleted = useCallback((id) => {
    setEntries((prev) => prev.filter((e) => e._id !== id));
  }, []);

  const onCleared = useCallback(() => {
    setEntries([]);
  }, []);

  useSocket(token, onNew, onDeleted, onCleared);

  const handleSave = async () => {
    if (!text.trim()) {
      toast.error('Metin boş olamaz');
      return;
    }
    setSaving(true);
    try {
      const res = await axios.post('/api/clipboard', { text: text.trim(), source: 'web' });
      setEntries((prev) => {
        if (prev.find((e) => e._id === res.data._id)) return prev;
        return [res.data, ...prev].slice(0, 100);
      });
      setText('');
      toast.success('Kaydedildi!');
    } catch {
      toast.error('Kaydedilemedi');
    } finally {
      setSaving(false);
    }
  };

  const handleCopy = async (entry) => {
    try {
      await navigator.clipboard.writeText(entry.text);
      setCopiedId(entry._id);
      toast.success('Kopyalandı!');
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      toast.error('Kopyalanamadı');
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/api/clipboard/${id}`);
      setEntries((prev) => prev.filter((e) => e._id !== id));
      toast.success('Silindi');
    } catch {
      toast.error('Silinemedi');
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Tüm clipboard geçmişi silinsin mi?')) return;
    try {
      await axios.delete('/api/clipboard');
      setEntries([]);
      toast.success('Geçmiş temizlendi');
    } catch {
      toast.error('Temizlenemedi');
    }
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSave();
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-logo">
          <span className="logo-icon">⌘</span>
          <span>ClipSync</span>
        </div>
        <div className="header-right">
          <span className="user-email">{user?.email}</span>
          <button className="logout-btn" onClick={logout}>Çıkış</button>
        </div>
      </header>

      <main className="main">
        <section className="input-section">
          <div className="input-label">
            <span>📋 Metni buraya yapıştır veya yaz</span>
            <span className="shortcut-hint">Ctrl+Enter ile kaydet</span>
          </div>
          <textarea
            ref={textareaRef}
            className="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Kopyaladığın metni buraya yapıştır (Ctrl+V)..."
            rows={5}
          />
          <div className="input-actions">
            <span className="char-count">{text.length} karakter</span>
            <button
              className="save-btn"
              onClick={handleSave}
              disabled={saving || !text.trim()}
            >
              {saving ? (
                <span className="spinner" />
              ) : (
                <>💾 Kaydet & Senkronize Et</>
              )}
            </button>
          </div>
        </section>

        <section className="history-section">
          <div className="history-header">
            <h2>
              📖 Geçmiş
              <span className="count-badge">{entries.length}</span>
            </h2>
            {entries.length > 0 && (
              <button className="clear-btn" onClick={handleClearAll}>
                🗑 Tümünü Sil
              </button>
            )}
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="spinner large" />
              <p>Yükleniyor...</p>
            </div>
          ) : entries.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">📭</span>
              <p>Henüz clipboard geçmişin yok</p>
              <small>Metin ekleyince burada görünecek</small>
            </div>
          ) : (
            <ul className="entry-list">
              {entries.map((entry) => (
                <li key={entry._id} className="entry-item">
                  <div className="entry-meta">
                    <span className="entry-source">{entry.source}</span>
                    <span className="entry-time">{formatTime(entry.createdAt)}</span>
                  </div>
                  <p className="entry-text">{entry.text}</p>
                  <div className="entry-actions">
                    <button
                      className={`action-btn copy ${copiedId === entry._id ? 'copied' : ''}`}
                      onClick={() => handleCopy(entry)}
                    >
                      {copiedId === entry._id ? '✓ Kopyalandı' : '📋 Kopyala'}
                    </button>
                    <button
                      className="action-btn delete"
                      onClick={() => handleDelete(entry._id)}
                    >
                      🗑 Sil
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}
