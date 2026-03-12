import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthPage from './components/AuthPage';
import Dashboard from './components/Dashboard';
import './App.css';

function AppContent() {
  const { user, loading } = useAuth();
  if (loading) return <div className="app-loading"><div className="spinner large" /></div>;
  return user ? <Dashboard /> : <AuthPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#12121f',
            color: '#f0f0ff',
            border: '1px solid #1e1e35',
            borderRadius: '10px',
            fontFamily: "'Inter', sans-serif",
            fontSize: '13px',
          },
          success: { iconTheme: { primary: '#00d68f', secondary: '#12121f' } },
          error: { iconTheme: { primary: '#ff4d6d', secondary: '#12121f' } },
        }}
      />
      <AppContent />
    </AuthProvider>
  );
}
