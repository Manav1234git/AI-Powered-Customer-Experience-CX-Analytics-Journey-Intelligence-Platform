import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Mail, MessageCircle, Phone, CheckCircle, XCircle } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function Journey() {
  const [customers, setCustomers] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [journey, setJourney] = useState([]);

  useEffect(() => {
    // Fetch customer list for dropdown
    const fetchCustomers = async () => {
      try {
        const res = await axios.get(`${API_URL}/churn-risk`);
        setCustomers(res.data);
        if (res.data.length > 0) {
          setSelectedId(res.data[0].customer_id);
        }
      } catch (error) {
        console.error("Error fetching customers", error);
      }
    };
    fetchCustomers();
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    const fetchJourney = async () => {
      try {
        const res = await axios.get(`${API_URL}/journey/${selectedId}`);
        setJourney(res.data);
      } catch (error) {
        console.error("Error fetching journey", error);
      }
    };
    fetchJourney();
  }, [selectedId]);

  const getChannelIcon = (channel) => {
    switch (channel.toLowerCase()) {
      case 'email': return <Mail size={16} />;
      case 'chat': return <MessageCircle size={16} />;
      case 'phone': return <Phone size={16} />;
      default: return <CheckCircle size={16} />;
    }
  };

  return (
    <div className="flex flex-col gap-8 max-w-3xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold">Journey Intelligence</h2>
        <p className="text-textSecondary">Visualize customer touchpoints and resolutions</p>
      </div>

      <div className="bg-card p-6 rounded-xl border border-slate-700">
        <label className="block text-sm font-medium text-textSecondary mb-2">Select Customer to View Journey</label>
        <select 
          className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-white"
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
        >
          {customers.map(c => (
            <option key={c.customer_id} value={c.customer_id}>{c.name} ({c.customer_id})</option>
          ))}
        </select>
      </div>

      <div className="relative pl-8 border-l border-slate-700 ml-4 py-4 space-y-8">
        {journey.map((point, idx) => (
          <div key={idx} className="relative">
            {/* Timeline dot */}
            <div className={`absolute -left-[41px] w-8 h-8 rounded-full flex items-center justify-center border-4 border-background ${
              point.sentiment === 'Positive' ? 'bg-green-500 text-white' :
              point.sentiment === 'Negative' ? 'bg-red-500 text-white' :
              'bg-slate-500 text-white'
            }`}>
              {getChannelIcon(point.channel)}
            </div>
            
            <div className="bg-card p-5 rounded-xl border border-slate-700 shadow-sm">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-semibold text-lg capitalize">{point.channel} Interaction</h4>
                <span className="text-sm text-textSecondary font-mono">{point.date}</span>
              </div>
              <div className="flex items-center gap-4 text-sm mt-3">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  point.sentiment === 'Positive' ? 'bg-green-500/20 text-green-400' :
                  point.sentiment === 'Negative' ? 'bg-red-500/20 text-red-400' :
                  'bg-slate-500/20 text-slate-400'
                }`}>
                  {point.sentiment} Sentiment
                </span>
                <span className={`flex items-center gap-1 ${point.resolved === 'Y' ? 'text-green-400' : 'text-red-400'}`}>
                  {point.resolved === 'Y' ? <CheckCircle size={14}/> : <XCircle size={14}/>}
                  {point.resolved === 'Y' ? 'Issue Resolved' : 'Unresolved'}
                </span>
              </div>
              {point.note && <p className="mt-3 text-textSecondary text-sm">{point.note}</p>}
            </div>
          </div>
        ))}
        {journey.length === 0 && (
          <div className="text-textSecondary">No touchpoints recorded for this customer yet.</div>
        )}
      </div>
    </div>
  );
}
