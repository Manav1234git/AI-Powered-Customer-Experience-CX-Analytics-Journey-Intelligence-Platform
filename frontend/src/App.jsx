import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MessageSquare, 
  BarChart3, 
  AlertTriangle, 
  Map, 
  Bot, 
  Settings 
} from 'lucide-react';

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
          ? 'bg-accent text-white' 
          : 'text-textSecondary hover:bg-card hover:text-textPrimary'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </Link>
  );
};

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-slate-700 flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">
            CX Analytics
          </h1>
          <p className="text-xs text-textSecondary mt-1">Journey Intelligence</p>
        </div>
        
        <nav className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
          <SidebarItem icon={LayoutDashboard} label="Dashboard" path="/" />
          <SidebarItem icon={MessageSquare} label="Reviews" path="/reviews" />
          <SidebarItem icon={BarChart3} label="Analytics" path="/analytics" />
          <SidebarItem icon={AlertTriangle} label="Churn Risk" path="/churn" />
          <SidebarItem icon={Map} label="Journey Insights" path="/journey" />
          <SidebarItem icon={Bot} label="AI Copilot" path="/copilot" />
          <div className="mt-auto">
            <SidebarItem icon={Settings} label="Admin Settings" path="/admin" />
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-background">
        <div className="p-8 h-full">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/reviews" element={<Reviews />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/churn" element={<ChurnRisk />} />
            <Route path="/journey" element={<Journey />} />
            <Route path="/copilot" element={<Copilot />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
