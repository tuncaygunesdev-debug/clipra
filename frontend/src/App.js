import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthPage from './components/AuthPage';
import Dashboard from './components/Dashboard';
import './App.css';

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner large" />
      </div>
    );
  }

  return user ? <Dashboard /> : <AuthPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1a1a2e',
            color: '#e2e8f0',
            border: '1px solid #2d2d4e',
            borderRadius: '12px',
            fontFamily: "'JetBrains Mono', monospace",
          },
        }}
      />
      <AppContent />
    </AuthProvider>
  );
}
