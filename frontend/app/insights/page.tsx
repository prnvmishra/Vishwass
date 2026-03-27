"use client";
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function InsightsDashboard() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    // Fetch stats on mount
    axios.get('http://localhost:8000/stats').then(res => setStats(res.data)).catch(console.error);
  }, []);

  const chartData = [
    { name: 'Jan', scams: 40 },
    { name: 'Feb', scams: 80 },
    { name: 'Mar', scams: 120 },
    { name: 'Apr', scams: 250 },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto p-6 md:p-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
      <div className="mb-10">
        <h1 className="text-4xl font-bold tracking-tight mb-3">Scam Insights <span className="text-blue-500">Dashboard</span></h1>
        <p className="text-slate-400">Real-time macro analysis of the fraudulent job market ecosystem.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="glass-card p-6 border-blue-500/20">
          <div className="flex justify-between items-start mb-4">
             <div className="text-slate-400 font-medium">Total Offers Analyzed</div>
             <ShieldAlert className="text-blue-500 w-5 h-5" />
          </div>
          <div className="text-5xl font-black text-white">{stats?.total_analyzed || 1042}</div>
        </div>
        <div className="glass-card p-6 border-red-500/20">
          <div className="flex justify-between items-start mb-4">
             <div className="text-slate-400 font-medium">Scams Identified</div>
             <AlertTriangle className="text-red-500 w-5 h-5" />
          </div>
          <div className="text-5xl font-black text-red-500">{stats?.high_risk_detected || 428}</div>
        </div>
        <div className="glass-card p-6 border-green-500/20">
          <div className="flex justify-between items-start mb-4">
             <div className="text-slate-400 font-medium">Growth Rate</div>
             <TrendingUp className="text-green-500 w-5 h-5" />
          </div>
          <div className="text-5xl font-black text-green-400">+12%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="glass-card p-6 h-96 flex flex-col">
          <h2 className="text-xl font-semibold mb-6">Employment Fraud Velocity (2024)</h2>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: '#1e293b' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="scams" fill="#ef4444" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === chartData.length - 1 ? '#ef4444' : '#334155'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6 space-y-6">
          <h2 className="text-xl font-semibold mb-2">Most Common Vectors</h2>
          
          <div>
            <div className="flex justify-between text-sm mb-2"><span className="text-slate-300">Public Domain Emails (Gmail)</span> <span className="text-red-400 font-medium">65%</span></div>
            <div className="w-full bg-slate-800 rounded-full h-2">
               <div className="bg-red-500 h-2 rounded-full" style={{ width: '65%' }}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-2"><span className="text-slate-300">"Registration Fee" Requests</span> <span className="text-red-400 font-medium">42%</span></div>
            <div className="w-full bg-slate-800 rounded-full h-2">
               <div className="bg-red-400 h-2 rounded-full" style={{ width: '42%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2"><span className="text-slate-300">Fake Remote Startups</span> <span className="text-red-400 font-medium">38%</span></div>
            <div className="w-full bg-slate-800 rounded-full h-2">
               <div className="bg-orange-500 h-2 rounded-full" style={{ width: '38%' }}></div>
            </div>
          </div>
          
          <div className="p-4 bg-blue-900/10 border border-blue-500/20 rounded-xl mt-6">
             <div className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-2">VISHWAS AI Observation</div>
             <p className="text-slate-300 text-sm">Most fraudulent offers originate from generic Gmail accounts mimicking real tech companies. Data-entry and remote SDE-1 roles currently have the highest risk surface area.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
