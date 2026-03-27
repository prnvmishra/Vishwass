"use client";
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Users, AlertCircle, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function CommunityReports() {
  const [reports, setReports] = useState<any[]>([]);
  const [company, setCompany] = useState('');
  const [desc, setDesc] = useState('');

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await axios.get('http://localhost:8000/community');
      setReports(res.data);
    } catch(e) { console.error(e); }
  }

  const submitReport = async (e: any) => {
    e.preventDefault();
    if(!company || !desc) return;
    try {
        await axios.post('http://localhost:8000/report-scam', {
        company_name: company,
        description: desc,
        reporter_email: 'anonymous@vishwas.com'
        });
        setCompany('');
        setDesc('');
        fetchReports();
    } catch(err) { console.error(err); }
  }

  return (
    <div className="w-full max-w-5xl mx-auto p-6 md:p-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
      <div className="mb-10">
        <h1 className="text-4xl font-bold tracking-tight mb-3">Community <span className="text-blue-500">Reports</span></h1>
        <p className="text-slate-400">Crowdsourced intelligence protecting job seekers globally.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Submit Form */}
        <div className="md:col-span-1">
          <div className="glass-card p-6 sticky top-24">
            <h2 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
               <AlertCircle className="w-5 h-5 text-red-400" /> Report a Scam
            </h2>
            <form onSubmit={submitReport} className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Company Name</label>
                <input 
                  type="text" 
                  value={company}
                  onChange={e => setCompany(e.target.value)}
                  className="w-full mt-1 bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500 transition-colors"
                  placeholder="e.g. Global Tech LLC"
                  required
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Scam Description</label>
                <textarea 
                  value={desc}
                  onChange={e => setDesc(e.target.value)}
                  className="w-full mt-1 bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500 transition-colors h-32 resize-none"
                  placeholder="They asked for a 2000 INR registration fee for a Macbook..."
                  required
                ></textarea>
              </div>
              <button type="submit" className="w-full py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-lg font-medium transition-colors">
                 Submit Warning
              </button>
            </form>
          </div>
        </div>

        {/* Feed */}
        <div className="md:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
             <Users className="w-5 h-5 text-blue-400" /> Recent Warnings
          </h2>
          {reports.length === 0 ? (
             <div className="text-center py-12 text-slate-500 border border-dashed border-slate-700 rounded-2xl">
                 No community reports yet.
             </div>
          ) : (
            reports.map(report => (
              <div key={report.id} className="glass-panel p-5 rounded-2xl hover:border-blue-500/30 transition-colors">
                 <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-lg text-white">{report.company_name}</h3>
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                       <Calendar className="w-3 h-3" /> 
                       {formatDistanceToNow(new Date(report.timestamp), { addSuffix: true })}
                    </span>
                 </div>
                 <p className="text-slate-300 text-sm leading-relaxed">{report.description}</p>
                 <div className="mt-3 inline-block px-2.5 py-1 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold">
                    Community Flag
                 </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
