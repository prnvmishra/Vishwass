"use client";
import React, { useState } from 'react';
import axios from 'axios';
import { Search, Building, ShieldAlert, AlertTriangle, Briefcase, MapPin, Globe } from 'lucide-react';
import RiskGauge from '@/components/RiskGauge';

export default function SearchCompany() {
   const [query, setQuery] = useState('');
   const [result, setResult] = useState<any>(null);
   const [loading, setLoading] = useState(false);

   const handleSearch = async (e: any) => {
      e.preventDefault();
      if(!query) return;
      setLoading(true);
      try {
         const res = await axios.get(`http://localhost:8000/company/${encodeURIComponent(query)}`);
         setResult(res.data);
      } catch (e) {
         console.error(e);
      }
      setLoading(false);
   }

   return (
    <div className="w-full max-w-3xl mx-auto p-6 md:p-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
      <div className="text-center mb-10">
        <div className="inline-block px-3 py-1 mb-6 rounded-full glass-panel text-sm text-blue-300 border-blue-500/30">
            Entity Search Engine
        </div>
        <h1 className="text-4xl font-bold tracking-tight mb-3">Company <span className="text-blue-500">Security Check</span></h1>
        <p className="text-slate-400">Search for past AI analyzes and community reports tied to a specific organization.</p>
      </div>

      <form onSubmit={handleSearch} className="relative mb-12">
         <div className="absolute inset-y-0 left-4 flex flex-col justify-center">
             <Search className="w-6 h-6 text-slate-400" />
         </div>
         <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a company name (e.g. Acme Corp...)"
            className="w-full bg-slate-900 border-2 border-slate-700 focus:border-blue-500 rounded-2xl py-4 pl-14 pr-32 text-lg text-white placeholder-slate-500 outline-none transition-all shadow-xl shadow-black/20"
         />
         <button type="submit" disabled={loading} className="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl px-6 font-semibold transition-colors disabled:opacity-50">
            {loading ? "Searching..." : "Search"}
         </button>
      </form>

      {result && (
         <div className="glass-card p-6 md:p-8 animate-in fade-in zoom-in-95 duration-500">
             <div className="flex flex-col md:flex-row items-start md:items-center gap-6 mb-8 pb-6 border-b border-slate-700/50">
                 <div className="w-20 h-20 rounded-2xl bg-slate-800 flex items-center justify-center border border-slate-700 shadow-inner shrink-0">
                     <Building className="w-10 h-10 text-slate-400" />
                 </div>
                 <div className="flex-1">
                     <div className="flex items-center gap-3">
                        <h2 className="text-3xl font-bold text-white uppercase tracking-wider">{result.company}</h2>
                        {result.is_verified_entity && (
                            <div className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-bold rounded uppercase tracking-widest border border-green-500/30">Verified Entity</div>
                        )}
                     </div>
                     <p className="text-slate-400 text-sm mt-3 leading-relaxed max-w-3xl">
                        {result.intelligence?.summary || "No massive global profile detected. Falling back to local database algorithms."}
                     </p>
                 </div>
             </div>

             {/* Structural Company Intelligence */}
             {result.intelligence && (
                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                     <div className="p-4 bg-slate-900/50 rounded-xl border border-white/5">
                         <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1 flex items-center gap-2">
                            <Briefcase className="w-3 h-3" /> Industry
                         </div>
                         <div className="text-white font-medium">{result.intelligence.industry}</div>
                     </div>
                     <div className="p-4 bg-slate-900/50 rounded-xl border border-white/5">
                         <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1 flex items-center gap-2">
                            <Building className="w-3 h-3" /> Org Size
                         </div>
                         <div className="text-white font-medium">{result.intelligence.size}</div>
                     </div>
                     <div className="p-4 bg-slate-900/50 rounded-xl border border-white/5">
                         <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1 flex items-center gap-2">
                            <MapPin className="w-3 h-3" /> Headquarters
                         </div>
                         <div className="text-white font-medium">{result.intelligence.headquarters}</div>
                     </div>
                     <div className="p-4 bg-slate-900/50 rounded-xl border border-white/5 md:col-span-2 lg:col-span-1">
                         <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1 flex items-center gap-2">
                            <ShieldAlert className="w-3 h-3 text-green-400" /> MCA Status
                         </div>
                         <div className={`text-sm font-medium ${result.intelligence.mca_registration?.includes('Verified') ? 'text-green-400' : 'text-orange-500'}`}>
                            {result.intelligence.mca_registration || "Validation Pending"}
                         </div>
                     </div>
                     <div className="p-4 bg-blue-900/10 rounded-xl border border-blue-500/20">
                         <div className="text-xs text-blue-400 font-semibold uppercase tracking-wider mb-1 flex items-center gap-2">
                            <Globe className="w-3 h-3" /> Link Graph
                         </div>
                         <div className="flex gap-3 mt-2">
                            {result.links?.website ? (
                                <a href={result.links.website} target="_blank" rel="noreferrer" className="text-sm text-blue-300 hover:text-white underline">Website</a>
                            ) : <span className="text-sm text-slate-600">No Web</span>}
                            {result.links?.linkedin ? (
                                <a href={result.links.linkedin} target="_blank" rel="noreferrer" className="text-sm text-blue-300 hover:text-white underline">LinkedIn</a>
                            ) : <span className="text-sm text-slate-600">No LI</span>}
                         </div>
                     </div>
                 </div>
             )}
             
             {/* Branch Mapping */}
             {result.intelligence && (
                <div className="mb-8 p-4 bg-slate-900/30 rounded-xl border border-white/5">
                    <h3 className="text-sm text-slate-400 font-medium mb-2">Global & India Presence</h3>
                    <p className="text-slate-300 text-sm leading-relaxed">{result.intelligence.branches}</p>
                </div>
             )}

             <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                 <div className="glass-panel p-6 flex flex-col items-center text-center">
                    <h3 className="text-slate-400 font-medium text-sm mb-4">Historical AI Risk Score Average</h3>
                    <RiskGauge score={result.average_risk_score} hideLabels />
                    <p className="text-xs text-slate-500 mt-4">Based on {result.past_scans} previous offers</p>
                 </div>

                 <div className="glass-panel p-6 flex flex-col justify-center text-center">
                    <h3 className="text-slate-400 font-medium text-sm mb-4">Community Flags</h3>
                    <div className="flex items-center justify-center gap-3">
                        {result.community_reports_count > 0 ? (
                            <AlertTriangle className="w-12 h-12 text-red-500" />
                        ) : (
                            <ShieldAlert className="w-12 h-12 text-green-500" />
                        )}
                        <span className={`text-6xl font-black ${result.community_reports_count > 0 ? "text-red-500" : "text-green-500"}`}>
                            {result.community_reports_count}
                        </span>
                    </div>
                    {result.community_reports_count > 0 && (
                        <p className="text-xs text-red-400 mt-4">Warning: This entity has actively reported scams.</p>
                    )}
                 </div>
             </div>
         </div>
      )}
    </div>
   );
}
