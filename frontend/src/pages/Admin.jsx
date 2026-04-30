import React, { useState } from 'react';
import axios from 'axios';
import { KeyRound, Database, Save } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function Admin() {
  const [apiKey, setApiKey] = useState('');
  const [keyStatus, setKeyStatus] = useState('');

  const handleSaveKey = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/admin/api-key`, { api_key: apiKey });
      setKeyStatus('API Key updated successfully.');
      setTimeout(() => setKeyStatus(''), 3000);
    } catch (error) {
      setKeyStatus('Error updating API Key.');
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold">Admin Settings</h2>
        <p className="text-textSecondary">Manage platform configurations and integrations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* API Key Form */}
        <div className="bg-card p-6 rounded-xl border border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2"><KeyRound size={20} className="text-blue-400" /> AI Integration Settings</h3>
          <p className="text-sm text-textSecondary mb-6">Configure your external AI provider API key (e.g., OpenAI) if you want to switch from the local rule-based model.</p>
          
          <form onSubmit={handleSaveKey} className="flex flex-col gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">API Key</label>
              <input 
                type="password" 
                placeholder="sk-..." 
                className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono"
                value={apiKey}
                onChange={e => setApiKey(e.target.value)}
              />
            </div>
            <button type="submit" className="bg-accent hover:bg-blue-600 text-white py-2 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 w-full mt-2">
              <Save size={18} /> Save Configuration
            </button>
            {keyStatus && <p className="text-sm text-green-400 text-center">{keyStatus}</p>}
          </form>
        </div>

        {/* System Status */}
        <div className="bg-card p-6 rounded-xl border border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2"><Database size={20} className="text-blue-400" /> System Status</h3>
          <div className="flex flex-col gap-4">
            <div className="bg-slate-900 p-4 rounded-lg flex justify-between items-center">
              <span className="text-sm text-textSecondary">Database Connection</span>
              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-bold border border-green-500/30">Active</span>
            </div>
            <div className="bg-slate-900 p-4 rounded-lg flex justify-between items-center">
              <span className="text-sm text-textSecondary">Sentiment Engine</span>
              <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs font-bold border border-blue-500/30">Local Rules</span>
            </div>
            <div className="bg-slate-900 p-4 rounded-lg flex justify-between items-center">
              <span className="text-sm text-textSecondary">Data Storage</span>
              <span className="px-2 py-1 bg-slate-500/20 text-slate-400 rounded text-xs font-bold border border-slate-500/30">In-Memory</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
