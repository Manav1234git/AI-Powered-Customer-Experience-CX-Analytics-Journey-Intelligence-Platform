import React from 'react';
import { Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MessageSquare, 
  BarChart3, 
  AlertTriangle, 
  Map, 
  Bot, 
  Settings,
  LogOut
} from 'lucide-react';

import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Reviews from './pages/Reviews';
import Analytics from './pages/Analytics';
import ChurnRisk from './pages/ChurnRisk';
import Journey from './pages/Journey';
import Copilot from './pages/Copilot';
import Admin from './pages/Admin';

const SidebarItem = ({ icon: Icon, label, path }) => {
  const location = useLocation();
  const isActive = location.pathname === path;
  
  return (
    <Link 
      to={path} 
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
        isActive 
          ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' 
          : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </Link>
  );
};

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('cx_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function MainLayout({ children }) {
  const navigate = useNavigate();
  const userStr = localStorage.getItem('cx_user');
  const user = userStr ? JSON.parse(userStr) : { name: 'User' };

  const handleLogout = () => {
    localStorage.removeItem('cx_token');
    localStorage.removeItem('cx_user');
    navigate('/login');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#020617] text-slate-200 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/50 backdrop-blur-md border-r border-slate-800 flex flex-col z-20">
        <div className="p-6 border-b border-slate-800">
          <Link to="/">
            <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
              CX Analytics
            </h1>
            <p className="text-xs text-indigo-300/70 mt-1">Production Environment</p>
          </Link>
        </div>
        
        <div className="px-6 py-4 border-b border-slate-800/50 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-white">
            {user.name.charAt(0)}
          </div>
          <div className="text-sm font-medium truncate">{user.name}</div>
        </div>

        <nav className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
          <SidebarItem icon={LayoutDashboard} label="Dashboard" path="/dashboard" />
          <SidebarItem icon={MessageSquare} label="Reviews" path="/dashboard/reviews" />
          <SidebarItem icon={BarChart3} label="Analytics" path="/dashboard/analytics" />
          <SidebarItem icon={AlertTriangle} label="Churn Risk" path="/dashboard/churn" />
          <SidebarItem icon={Map} label="Journey Insights" path="/dashboard/journey" />
          <SidebarItem icon={Bot} label="AI Copilot" path="/dashboard/copilot" />
          <div className="mt-auto">
            <SidebarItem icon={Settings} label="Admin Settings" path="/dashboard/admin" />
            <button 
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors mt-2"
            >
              <LogOut size={20} />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-slate-950/50 relative">
        <div className="absolute top-0 left-0 w-full h-96 bg-indigo-900/10 blur-3xl pointer-events-none"></div>
        <div className="p-8 min-h-full relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected Dashboard Routes */}
      <Route path="/dashboard" element={<ProtectedRoute><MainLayout><Dashboard /></MainLayout></ProtectedRoute>} />
      <Route path="/dashboard/reviews" element={<ProtectedRoute><MainLayout><Reviews /></MainLayout></ProtectedRoute>} />
      <Route path="/dashboard/analytics" element={<ProtectedRoute><MainLayout><Analytics /></MainLayout></ProtectedRoute>} />
      <Route path="/dashboard/churn" element={<ProtectedRoute><MainLayout><ChurnRisk /></MainLayout></ProtectedRoute>} />
      <Route path="/dashboard/journey" element={<ProtectedRoute><MainLayout><Journey /></MainLayout></ProtectedRoute>} />
      <Route path="/dashboard/copilot" element={<ProtectedRoute><MainLayout><Copilot /></MainLayout></ProtectedRoute>} />
      <Route path="/dashboard/admin" element={<ProtectedRoute><MainLayout><Admin /></MainLayout></ProtectedRoute>} />
    </Routes>
  );
}
