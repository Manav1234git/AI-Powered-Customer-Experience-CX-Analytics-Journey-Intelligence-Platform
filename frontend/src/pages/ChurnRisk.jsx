import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Filter } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function ChurnRisk() {
  const [customers, setCustomers] = useState([]);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    fetchChurnRisk();
  }, []);

  const fetchChurnRisk = async () => {
    try {
      const res = await axios.get(`${API_URL}/churn-risk`);
      setCustomers(res.data);
    } catch (error) {
      console.error("Error fetching churn risk data", error);
    }
  };

  const filteredCustomers = customers.filter(c => filter === 'All' || c.risk_level === filter);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold">Churn Risk Analysis</h2>
          <p className="text-textSecondary">Predictive customer retention scoring</p>
        </div>
        <div className="flex items-center gap-2 bg-card p-2 rounded-lg border border-slate-700">
          <Filter size={16} className="text-textSecondary ml-2" />
          <select 
            className="bg-transparent text-sm text-white outline-none px-2"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="All">All Risks</option>
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/50 border-b border-slate-700 text-textSecondary text-sm">
                <th className="py-4 px-6">Customer</th>
                <th className="py-4 px-6">Avg Sentiment</th>
                <th className="py-4 px-6">Tickets</th>
                <th className="py-4 px-6">Inactive Days</th>
                <th className="py-4 px-6">Risk Score</th>
                <th className="py-4 px-6">Level</th>
              </tr>
            </thead>
            <tbody>
              {filteredCustomers.map(c => (
                <tr key={c.customer_id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors">
                  <td className="py-4 px-6">
                    <div className="font-medium text-textPrimary">{c.name}</div>
                    <div className="text-xs text-textSecondary">{c.customer_id}</div>
                  </td>
                  <td className="py-4 px-6 text-sm">{c.sentiment_score}</td>
                  <td className="py-4 px-6 text-sm">{c.ticket_count}</td>
                  <td className="py-4 px-6 text-sm">{c.inactive_days} days</td>
                  <td className="py-4 px-6 font-mono text-sm">{c.churn_risk_pct}%</td>
                  <td className="py-4 px-6">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      c.risk_level === 'High' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                      c.risk_level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                      'bg-green-500/20 text-green-400 border border-green-500/30'
                    }`}>
                      {c.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
              {filteredCustomers.length === 0 && (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-textSecondary">No customers match the current filter.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
