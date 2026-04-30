import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BarChart3, Users, Bot, ShieldCheck } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans selection:bg-indigo-500/30">
      {/* Navbar */}
      <nav className="container mx-auto px-6 py-6 flex justify-between items-center relative z-10">
        <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 flex items-center gap-2">
          <ShieldCheck size={28} className="text-indigo-500" />
          CX Analytics
        </div>
        <div className="hidden md:flex space-x-8 text-sm font-medium text-slate-300">
          <a href="#features" className="hover:text-white transition">Platform</a>
          <a href="#about" className="hover:text-white transition">Solutions</a>
        </div>
        <div className="flex items-center gap-4">
          <Link 
            to="/login" 
            className="text-slate-300 hover:text-white font-medium transition-colors"
          >
            Log in
          </Link>
          <Link 
            to="/register" 
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-full font-medium transition-all shadow-[0_0_15px_rgba(79,70,229,0.5)] hover:shadow-[0_0_25px_rgba(79,70,229,0.7)]"
          >
            Sign up
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative pt-32 pb-32 overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[500px] opacity-40 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-indigo-600/30 rounded-full blur-[120px]"></div>
          <div className="absolute top-1/2 left-1/3 -translate-y-1/2 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[100px]"></div>
        </div>

        <div className="container mx-auto px-6 relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700 text-sm text-indigo-300 mb-8 backdrop-blur-md">
            <span className="flex h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>
            Production Database Connected
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8">
            Intelligence for the <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              Modern Customer Journey
            </span>
          </h1>
          <p className="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Predict churn, analyze sentiment, and chat with your production database in real-time. 
            A robust, scalable platform designed for proactive CX management.
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <Link 
              to="/register" 
              className="flex items-center gap-2 bg-white text-slate-900 px-8 py-4 rounded-full font-bold text-lg hover:bg-slate-100 transition-all hover:scale-105 shadow-xl shadow-white/10"
            >
              Get Started <ArrowRight size={20} />
            </Link>
            <Link 
              to="/login" 
              className="flex items-center gap-2 bg-slate-800/50 backdrop-blur-md border border-slate-700 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-slate-700 transition-all"
            >
              Log in
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="container mx-auto px-6 py-24 relative z-10 border-t border-slate-800/50 bg-slate-900/20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Enterprise-Grade Features</h2>
          <p className="text-slate-400 max-w-xl mx-auto">Everything you need to turn customer feedback into actionable intelligence.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<BarChart3 size={32} className="text-indigo-400" />}
            title="Real-time Analytics"
            description="Monitor live sentiment trends, NPS, and overall customer health metrics at a glance using our robust SQLite backend."
          />
          <FeatureCard 
            icon={<Users size={32} className="text-purple-400" />}
            title="Churn Prediction"
            description="Our advanced ML models identify at-risk customers before they leave, allowing proactive intervention."
          />
          <FeatureCard 
            icon={<Bot size={32} className="text-pink-400" />}
            title="AI Copilot"
            description="Chat directly with your SQL database. Ask natural language questions and get immediate, data-backed insights."
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-slate-800/30 backdrop-blur-md border border-slate-700/50 p-8 rounded-3xl hover:border-indigo-500/50 transition-all duration-300 hover:-translate-y-2 hover:shadow-[0_10px_30px_-15px_rgba(79,70,229,0.3)]">
      <div className="bg-slate-900/80 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}
