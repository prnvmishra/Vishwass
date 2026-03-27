import React from 'react';
import Link from 'next/link';
import { ShieldAlert, Search, BarChart2, Users } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="w-full border-b border-white/5 bg-slate-900/50 backdrop-blur-xl z-50 sticky top-0">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:bg-blue-500 transition-colors">
            <ShieldAlert className="text-white w-5 h-5" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">VISHWAS</span>
        </Link>
        <div className="flex gap-6 items-center">
          <Link href="/search" className="text-sm font-medium text-slate-300 hover:text-white flex gap-2 items-center transition-colors">
            <Search className="w-4 h-4" /> Company Search
          </Link>
          <Link href="/insights" className="text-sm font-medium text-slate-300 hover:text-white flex gap-2 items-center transition-colors">
            <BarChart2 className="w-4 h-4" /> Scam Insights
          </Link>
          <Link href="/community" className="text-sm font-medium text-slate-300 hover:text-white flex gap-2 items-center transition-colors">
             <Users className="w-4 h-4" /> Community
          </Link>
        </div>
      </div>
    </nav>
  );
}
