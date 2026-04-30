import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';
import { Users, TrendingUp, AlertOctagon, Heart } from 'lucide-react';

const API_URL = 'http://localhost:8000';
const COLORS = ['#22c55e', '#94a3b8', '#ef4444']; // Green, Gray, Red

const KPICard = ({ title, value, icon: Icon, colorClass }) => (
  <div className="bg-card p-6 rounded-xl border border-slate-700 shadow-sm flex items-center gap-4">
    <div className={`p-4 rounded-lg ${colorClass}`}>
      <Icon size={24} className="text-white" />
    </div>
    <div>
      <h3 className="text-textSecondary text-sm font-medium">{title}</h3>
      <p className="text-2xl font-bold text-textPrimary">{value}</p>
    </div>
  </div>
);

export default function Dashboard() {
  const [insights, setInsights] = useState(null);
  const [trend, setTrend] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resInsights, resTrend] = await Promise.all([
          axios.get(`${API_URL}/insights`),
          axios.get(`${API_URL}/sentiment-trend`)
        ]);
        setInsights(resInsights.data);
        setTrend(resTrend.data);
      } catch (error) {
        console.error("Error fetching dashboard data", error);
      }
    };
    fetchData();
  }, []);

  const complaintData = [
    { name: 'Pricing', value: 45 },
    { name: 'Support', value: 30 },
    { name: 'Bugs', value: 20 },
    { name: 'UX', value: 15 },
  ];

  const segmentData = [
    { name: 'Happy', value: 60 },
    { name: 'Neutral', value: 25 },
    { name: 'At Risk', value: 15 },
  ];

  if (!insights) return <div className="text-center mt-10">Loading Dashboard...</div>;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold text-textPrimary">Platform Overview</h2>
        <p className="text-textSecondary">Real-time pulse of your customer experience</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard title="Total Customers" value={insights.total_customers} icon={Users} colorClass="bg-blue-500" />
        <KPICard title="Avg Sentiment" value={insights.avg_sentiment} icon={Heart} colorClass="bg-green-500" />
        <KPICard title="Avg Churn Risk" value={`${insights.avg_churn_risk}%`} icon={AlertOctagon} colorClass="bg-red-500" />
        <KPICard title="NPS Score" value={insights.nps_score} icon={TrendingUp} colorClass="bg-purple-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Line Chart */}
        <div className="bg-card p-6 rounded-xl border border-slate-700 col-span-1 lg:col-span-2">
          <h3 className="text-lg font-semibold mb-4">Sentiment Trend (30 Days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={[-1, 1]} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                <Line type="monotone" dataKey="sentiment_score" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="bg-card p-6 rounded-xl border border-slate-700">
          <h3 className="text-lg font-semibold mb-4">Customer Segments</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={segmentData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {segmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-2 text-sm text-textSecondary">
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-green-500"></div>Happy</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-slate-400"></div>Neutral</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-red-500"></div>At Risk</span>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="bg-card p-6 rounded-xl border border-slate-700 col-span-1 lg:col-span-3">
          <h3 className="text-lg font-semibold mb-4">Top Complaint Topics</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={complaintData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} cursor={{ fill: '#334155' }} />
                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
