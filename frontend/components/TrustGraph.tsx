import React from 'react';
import { Share2, Globe, Mail, Building2 } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

export default function TrustGraph({ extractedData, reasons }: { extractedData: any, reasons: string[] }) {
  const hasDomainMismatch = reasons.some(r => r.includes("domain does not match") || r.includes("public domain"));
  const hasNoPresence = reasons.some(r => r.includes("verifiable company website found"));

  const companyColor = hasNoPresence ? "text-red-400 border-red-500/50" : "text-green-400 border-green-500/50 bg-green-900/10";
  const webColor = hasNoPresence ? "text-red-400 border-red-500/50" : "text-green-400 border-green-500/50 bg-green-900/10";
  const emailColor = hasDomainMismatch ? "text-red-400 border-red-500/50" : "text-green-400 border-green-500/50 bg-green-900/10";

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-6 flex items-center gap-2 text-white">
        <Share2 className="w-5 h-5 text-blue-400" /> Entity Consistency Graph
      </h3>
      
      <div className="flex-1 flex flex-col md:flex-row items-center justify-between relative gap-4 py-4">
        
        {/* Company Node */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className={clsx("flex flex-col items-center p-4 glass-panel border z-10 w-32 shadow-lg", companyColor)}
        >
          <Building2 className="w-8 h-8 mb-3" />
          <span className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Company</span>
          <span className="font-semibold text-center mt-1 truncate max-w-[100px] text-sm">
            {extractedData?.company_name || 'Unknown'}
          </span>
        </motion.div>

        {/* Line  */}
        <div className={clsx("h-1 w-16 hidden md:block", hasNoPresence ? "bg-red-500/50" : "bg-green-500/50")} />

        {/* Website Node */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className={clsx("flex flex-col items-center p-4 glass-panel border z-10 w-32 shadow-lg", webColor)}
        >
          <Globe className="w-8 h-8 mb-3" />
          <span className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Website</span>
          <span className="font-medium truncate max-w-[100px] text-xs text-center">
            {extractedData?.website || 'Missing'}
          </span>
        </motion.div>

        {/* Line */}
        <div className={clsx("h-1 w-16 hidden md:block", hasDomainMismatch ? "bg-red-500/50" : "bg-green-500/50")} />

        {/* Email Node */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className={clsx("flex flex-col items-center p-4 glass-panel border z-10 w-32 shadow-lg", emailColor)}
        >
          <Mail className="w-8 h-8 mb-3" />
          <span className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">HR Email</span>
          <span className="font-medium truncate max-w-[100px] text-xs text-center">
            {extractedData?.hr_email || 'Unknown'}
          </span>
        </motion.div>
        
      </div>
      <p className="text-xs text-slate-500 text-center mt-6">
        Red connections indicate suspicious entity relations or mismatching domains.
      </p>
    </div>
  );
}
