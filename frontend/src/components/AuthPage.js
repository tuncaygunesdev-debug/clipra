import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const ClipraLogo = () => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 2H5a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2V4a2 2 0 00-2-2zM9 14H5a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2v-4a2 2 0 00-2-2zM21 2h-4a2 2 0 00-2 2v4a2 2 0 002 2h4a2 2 0 002-2V4a2 2 0 00-2-2zM14 17h8M18 13v8" 
      fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"/>
  </svg>
);

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
        toast.success('Giriş başarılı');
      } else {
        await register(email, password);
        toast.success('Hesap oluşturuldu');
      }
    } catch (err) {
      toast.error(err.response?.data?.error || 'Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="logo-mark">
            <ClipraLogo />
          </div>
          <h1>Clipra</h1>
          <p>Clipboard sync across all your devices</p>
        </div>

        <div className="auth-tabs">
          <button className={`tab-btn ${isLogin ? 'active' : ''}`} onClick={() => setIsLogin(true)}>
            Sign in
          </button>
          <button className={`tab-btn ${!isLogin ? 'active' : ''}`} onClick={() => setIsLogin(false)}>
            Sign up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? <span className="spinner" /> : isLogin ? 'Sign in' : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  );
}
