import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { useSocket } from '../hooks/useSocket';

function formatTime(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now - date;
  if (diff < 60000) return 'just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString('en', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

const ClipraLogo = () => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 2H5a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2V4a2 2 0 00-2-2zM9 14H5a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2v-4a2 2 0 00-2-2zM21 2h-4a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2V4a2 2 0 00-2-2zM14 17h8M18 13v8"
      fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

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
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchEntries(); }, [fetchEntries]);

  useEffect(() => {
    const handlePaste = (e) => {
      if (document.activeElement === textareaRef.current) return;
      const pasted = e.clipboardData?.getData('text');
      if (pasted) setText(pasted);
    };
    document.addEventListener('paste', handlePaste);
    return () => document.removeEventListener('paste', handlePaste);
  }, []);

  const onNew = useCallback((entry) => {
    setEntries((prev) => {
      if (prev.find((e) => e._id === entry._id)) return prev;
      return [entry, ...prev].slice(0, 100);
    });
    toast('New entry synced', { icon: '⚡' });
  }, []);

  const onDeleted = useCallback((id) => setEntries((prev) => prev.filter((e) => e._id !== id)), []);
  const onCleared = useCallback(() => setEntries([]), []);

  useSocket(token, onNew, onDeleted, onCleared);

  const handleSave = async () => {
    if (!text.trim()) { toast.error('Text is empty'); return; }
    setSaving(true);
    try {
      const res = await axios.post('/api/clipboard', { text: text.trim(), source: 'web' });
      setEntries((prev) => {
        if (prev.find((e) => e._id === res.data._id)) return prev;
        return [res.data, ...prev].slice(0, 100);
      });
      setText('');
      toast.success('Saved & synced');
    } catch {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleCopy = async (entry) => {
    try {
      await navigator.clipboard.writeText(entry.text);
      setCopiedId(entry._id);
      toast.success('Copied');
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      toast.error('Copy failed');
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`/api/clipboard/${id}`);
      setEntries((prev) => prev.filter((e) => e._id !== id));
    } catch {
      toast.error('Delete failed');
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Clear all clipboard history?')) return;
    try {
      await axios.delete('/api/clipboard');
      setEntries([]);
      toast.success('Cleared');
    } catch {
      toast.error('Failed to clear');
    }
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleSave();
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-mark"><ClipraLogo /></div>
          <span>Clipra</span>
        </div>
        <div className="header-right">
          <div className="status-dot">synced</div>
          <span className="user-email">{user?.email}</span>
          <button className="logout-btn" onClick={logout}>Sign out</button>
        </div>
      </header>

      <main className="main">
        <section className="input-section">
          <div className="input-header">
            <span className="input-title">New entry</span>
            <span className="shortcut-badge">⌘ Enter to save</span>
          </div>
          <textarea
            ref={textareaRef}
            className="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Paste or type anything..."
            rows={4}
          />
          <div className="input-footer">
            <span className="char-count">{text.length} chars</span>
            <button className="save-btn" onClick={handleSave} disabled={saving || !text.trim()}>
              {saving ? <span className="spinner" /> : <>Save & sync</>}
            </button>
          </div>
        </section>

        <section className="history-section">
          <div className="history-header">
            <div className="history-title">
              History
              <span className="count-badge">{entries.length}</span>
            </div>
            {entries.length > 0 && (
              <button className="clear-btn" onClick={handleClearAll}>Clear all</button>
            )}
          </div>

          {loading ? (
            <div className="loading-state"><div className="spinner large" /></div>
          ) : entries.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">◻</span>
              <p>No clipboard history yet</p>
              <small>Save something to get started</small>
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
                      {copiedId === entry._id ? '✓ Copied' : 'Copy'}
                    </button>
                    <button className="action-btn delete" onClick={() => handleDelete(entry._id)}>
                      Delete
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
