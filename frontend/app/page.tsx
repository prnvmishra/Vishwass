"use client";
import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, ArrowLeft, ExternalLink, Search, Share, AlertTriangle, Briefcase } from 'lucide-react';
import UploadArea from '@/components/UploadArea';
import RiskGauge from '@/components/RiskGauge';
import TrustGraph from '@/components/TrustGraph';

export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleFileUpload = async (file: File) => {
    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setTimeout(() => {
        setResult(response.data);
        setIsAnalyzing(false);
      }, 1500); // Artificial delay to show the cool loading animation
    } catch (error) {
      console.error(error);
      setIsAnalyzing(false);
      alert('Error analyzing file. Please ensure FastAPI backend is running on port 8000.');
    }
  };

  const handleDemo = async (type: 'real' | 'fake') => {
    // For demo, simulate the response
    setIsAnalyzing(true);
    setTimeout(() => {
      if (type === 'fake') {
        setResult({
          score: 85,
          risk_level: "High Risk",
          extracted_data: {
            company_name: "Global Tech Solutions LLC",
            hr_email: "hr.globaltech@gmail.com",
            salary: "2,500,000",
            role: "Software Developer",
            website: "www.globaltech.com"
          },
          reasons: [
            "Email uses public domain (gmail.com)",
            "Email domain (gmail.com) does not match website domain (globaltech.com)",
            "Suspicious language detected: urgent hiring, registration fee",
            "Salary anomaly: Exceeds expected standard ranges"
          ],
          llm_analysis: "The grammar is unprofessional and the requirement to pay a registration fee before joining is a major red flag typically associated with employment scams."
        });
      } else {
        setResult({
          score: 15,
          risk_level: "Low Risk",
          extracted_data: {
            company_name: "Acme Corp",
            hr_email: "careers@acmecorp.com",
            salary: "120,000",
            role: "Frontend Engineer",
            website: "www.acmecorp.com"
          },
          reasons: [
            "No significant risk signals detected."
          ],
          llm_analysis: "The document is well-structured, professional, and contains no typical scam language. Standard clauses are present."
        });
      }
      setIsAnalyzing(false);
    }, 2000);
  };

  const handleShare = async () => {
    if (!result) return;
    const text = `VISHWAS Analysis for ${result.extracted_data.company_name || 'Offer'}\n\nRisk Level: ${result.risk_level} (${result.score}/100)\nReasons:\n${result.reasons.map((r: string) => '- ' + r).join('\n')}`;
    
    try {
      if (navigator.share) {
        await navigator.share({
          title: 'Job Offer Risk Analysis',
          text: text
        });
      } else {
        await navigator.clipboard.writeText(text);
        alert('Report copied to clipboard!');
      }
    } catch (error) {
      console.warn("Native share failed or was aborted:", error);
      try {
        await navigator.clipboard.writeText(text);
        alert('Report copied to clipboard (Fallback)!');
      } catch (err) {
        console.error("Clipboard copy also failed:", err);
      }
    }
  };

  return (
    <main className="min-h-screen relative p-4 md:p-8 flex flex-col items-center">
      
      {/* Header */}
      <div className="w-full max-w-5xl mx-auto flex items-center justify-between py-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <ShieldAlert className="text-white w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">VISHWAS</h1>
        </div>
        {!result && (
          <div className="flex gap-4 hidden sm:flex">
            <button onClick={() => handleDemo('real')} className="px-4 py-2 text-sm rounded-lg glass-panel hover:bg-white/10 transition-colors">
              Try Real Offer
            </button>
            <button onClick={() => handleDemo('fake')} className="px-4 py-2 text-sm rounded-lg glass-panel hover:bg-red-500/10 transition-colors text-red-300">
              Try Fake Offer
            </button>
          </div>
        )}
      </div>

      <AnimatePresence mode="wait">
        {!result ? (
          <motion.div 
            key="upload-view"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="w-full max-w-5xl mt-12 flex flex-col items-center"
          >
            <div className="text-center mb-10">
               <div className="inline-block px-3 py-1 mb-6 rounded-full glass-panel text-sm text-blue-300 border-blue-500/30">
                 AI-Powered Job Offer Risk Analyzer
               </div>
              <h2 className="text-5xl md:text-6xl font-extrabold pb-4 tracking-tight">
                Instantly detect <span className="gradient-text">Employment Scams</span>
              </h2>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto mt-4">
                Our multi-signal AI engine analyzes job offer letters for inconsistencies, suspicious phrasing, and logical flaws to protect you from fraud.
              </p>
            </div>

            <UploadArea onFileSelect={handleFileUpload} isAnalyzing={isAnalyzing} />

            {/* Mobile demo buttons */}
            <div className="flex gap-4 sm:hidden mt-8">
              <button onClick={() => handleDemo('real')} className="px-4 py-2 text-sm rounded-lg glass-panel hover:bg-white/10 transition-colors">
                Demo: Real
              </button>
              <button onClick={() => handleDemo('fake')} className="px-4 py-2 text-sm rounded-lg glass-panel hover:bg-red-500/10 transition-colors text-red-300">
                Demo: Fake
              </button>
            </div>

            <div className="mt-20 w-full max-w-4xl grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
               <div className="glass-panel p-6 hover:border-blue-500/30 transition-colors">
                  <h3 className="font-semibold text-white text-lg mb-2">Entity Verification</h3>
                  <p className="text-slate-400 text-sm">Cross-references emails and domains for logical consistency.</p>
               </div>
               <div className="glass-panel p-6 hover:border-blue-500/30 transition-colors">
                  <h3 className="font-semibold text-white text-lg mb-2">Linguistic Analysis</h3>
                  <p className="text-slate-400 text-sm">Detects typical scam language, urgency, and unstructured grammar.</p>
               </div>
               <div className="glass-panel p-6 hover:border-blue-500/30 transition-colors">
                  <h3 className="font-semibold text-white text-lg mb-2">Financial Sanity</h3>
                  <p className="text-slate-400 text-sm">Validates salary bumps and flags overly generous unverified offers.</p>
               </div>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="result-view"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-6xl mt-4 space-y-6 pb-20"
          >
            <button 
              onClick={() => setResult(null)} 
              className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6 group"
            >
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" /> Analyze Another Offer
            </button>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Risk Score */}
              <div className="md:col-span-1">
                <RiskGauge score={result.score} />
              </div>

              {/* Data Extracted */}
              <div className="md:col-span-2 glass-card p-6 h-full flex flex-col">
                <h3 className="text-xl font-semibold mb-6 text-white flex items-center gap-2">
                   Extracted Information
                </h3>
                <div className="grid grid-cols-2 gap-4 flex-1">
                  <div className="glass-panel p-4 flex flex-col justify-center">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">Company Name</span>
                    <p className="font-medium text-lg mt-1">{result.extracted_data.company_name || 'N/A'}</p>
                  </div>
                  <div className="glass-panel p-4 flex flex-col justify-center">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">Role</span>
                    <p className="font-medium text-lg mt-1">{result.extracted_data.role || 'N/A'}</p>
                  </div>
                  <div className="glass-panel p-4 flex flex-col justify-center">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">Salary</span>
                    <p className="font-medium text-lg mt-1">{result.extracted_data.salary || 'N/A'}</p>
                  </div>
                  <div className="glass-panel p-4 flex flex-col justify-center">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">HR Email</span>
                    <p className="font-medium text-blue-400 text-lg mt-1 truncate">{result.extracted_data.hr_email || 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* IPQS Live Threat Intel */}
            {result.ipqs_intel && (
               <div className="glass-card p-6 mt-6 bg-slate-900/30 border border-blue-500/20 relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-4 opacity-10">
                    <ShieldAlert className="w-24 h-24 text-blue-500" />
                 </div>
                 <h3 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                    <ShieldAlert className={`${result.ipqs_intel.fraud_score > 60 ? 'text-red-500' : 'text-blue-500'} w-6 h-6`} /> Live IPQS Cyber Threat Intel
                 </h3>
                 <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
                    <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5">
                        <p className="text-xs text-slate-400 uppercase">Fraud Score</p>
                        <p className={`text-2xl font-black mt-1 ${result.ipqs_intel.fraud_score > 70 ? 'text-red-500' : 'text-green-500'}`}>
                           {result.ipqs_intel.fraud_score} <span className="text-sm font-normal text-slate-500">/ 100</span>
                        </p>
                    </div>
                    <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5">
                        <p className="text-xs text-slate-400 uppercase">Disposable Email</p>
                        <p className={`text-xl font-bold mt-1 ${result.ipqs_intel.is_disposable ? 'text-red-500' : 'text-slate-300'}`}>
                           {result.ipqs_intel.is_disposable ? "YES" : "NO"}
                        </p>
                    </div>
                    <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5">
                        <p className="text-xs text-slate-400 uppercase">Recent Abuse</p>
                        <p className={`text-xl font-bold mt-1 ${result.ipqs_intel.recent_abuse ? 'text-red-500' : 'text-slate-300'}`}>
                           {result.ipqs_intel.recent_abuse ? "YES" : "NO"}
                        </p>
                    </div>
                    <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 flex flex-col justify-center">
                        <p className="text-xs text-slate-400 uppercase mb-1">Status</p>
                        {result.ipqs_intel.fraud_score > 60 ? (
                            <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs font-bold rounded uppercase inline-block w-fit">Malicious</span>
                        ) : (
                            <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-bold rounded uppercase inline-block w-fit">Clean</span>
                        )}
                    </div>
                 </div>
                 <p className="text-xs text-slate-500 mt-4">* Email scanned in real-time via IPQualityScore global zero-day threat network.</p>
               </div>
            )}

            {/* RapidAPI LinkedIn Jobs Threat Intel */}
            {result.linkedin_jobs && (
               <div className="glass-card p-6 mt-6 bg-slate-900/30 border border-blue-500/20 relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Briefcase className="w-24 h-24 text-blue-500" />
                 </div>
                 <h3 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                    <Briefcase className={`${result.linkedin_jobs.has_active_listings ? 'text-green-500' : 'text-red-500'} w-6 h-6`} /> Global Job Verification (JSearch)
                 </h3>
                 <div className="relative z-10 flex items-center gap-4">
                    <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 w-full max-w-lg">
                        <p className="text-xs text-slate-400 uppercase">Active Role Match Status</p>
                        <p className={`text-lg font-bold mt-1 ${result.linkedin_jobs.has_active_listings ? 'text-green-500' : 'text-red-500'}`}>
                           {result.linkedin_jobs.message}
                        </p>
                    </div>
                 </div>
               </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
              {/* Reasons & LLM */}
              <div className="space-y-6 h-full">
                <div className="glass-card p-6 h-full flex flex-col">
                  <h3 className="text-xl font-semibold mb-6 text-white flex items-center gap-2">
                     <AlertTriangle className="text-yellow-500 w-5 h-5" /> Risk Factors & Anomalies
                  </h3>
                  <ul className="space-y-4 flex-1">
                    {result.reasons.map((reason: string, i: number) => (
                      <li key={i} className="flex gap-3 text-slate-300 bg-slate-800/50 p-3 rounded-xl border border-slate-700/50">
                        <span className={result.score > 40 ? "text-red-400" : "text-green-400"}>•</span>
                        <span className="text-sm">{reason}</span>
                      </li>
                    ))}
                  </ul>

                  {result.llm_analysis && (
                    <div className="mt-6 p-5 rounded-2xl bg-blue-900/20 border border-blue-500/20 relative overflow-hidden">
                      <div className="absolute top-0 left-0 w-1 h-full bg-blue-500" />
                      <h4 className="text-sm font-semibold text-blue-300 mb-2 uppercase tracking-wide">AI Agent Reasoning</h4>
                      <p className="text-sm text-blue-100/90 leading-relaxed">{result.llm_analysis}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Trust Graph */}
              <div className="h-full">
                <TrustGraph extractedData={result.extracted_data} reasons={result.reasons} />
              </div>
            </div>

            {/* Action Engine */}
            <div className="glass-card p-6 flex flex-col items-start gap-6 mt-4">
               <div className="flex flex-col md:flex-row items-center justify-between w-full gap-6">
                 <div className="text-slate-400 text-sm max-w-md">
                   <p>This tool provides risk indicators based on available signals.</p>
                   <p className="font-semibold text-white/70 mt-1">Please verify independently before making decisions.</p>
                 </div>
                 <div className="flex flex-wrap gap-3">
                   <button 
                     onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(result.extracted_data.company_name || 'company')}`, "_blank")}
                     className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 rounded-xl transition-all active:scale-95 text-sm font-medium border border-slate-700 hover:border-slate-500"
                   >
                     <Search className="w-4 h-4" /> Search Company
                   </button>
                   {result.verified_links?.linkedin ? (
                        <button onClick={() => window.open(result.verified_links.linkedin, "_blank")} className="flex items-center gap-2 px-4 py-2.5 bg-blue-900/40 hover:bg-blue-800/60 rounded-xl transition-all active:scale-95 text-sm font-medium border border-blue-500/30 text-blue-300">
                          <ExternalLink className="w-4 h-4" /> Open LinkedIn
                        </button>
                   ) : (
                        <button className="flex items-center gap-2 px-4 py-2.5 bg-slate-800/50 rounded-xl text-sm font-medium border border-slate-700/50 text-slate-500 cursor-not-allowed">
                          <ExternalLink className="w-4 h-4" /> LinkedIn Not Found
                        </button>
                   )}
                   <button onClick={handleShare} className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl transition-all active:scale-95 text-sm text-white font-medium shadow-lg shadow-blue-500/25">
                     <Share className="w-4 h-4" /> Share Report
                   </button>
                 </div>
               </div>
               
               {/* Display official links if found */}
               {(result.verified_links?.website || result.verified_links?.instagram) && (
                 <div className="w-full pt-4 border-t border-slate-700/50 flex flex-wrap items-center gap-4 text-sm text-slate-300">
                    <span className="text-slate-400">Official Presence Found:</span>
                    {result.verified_links.website && <a href={result.verified_links.website} target="_blank" className="hover:text-blue-400 underline decoration-blue-500/30 underline-offset-4">Official Website</a>}
                    {result.verified_links.instagram && <a href={result.verified_links.instagram} target="_blank" className="hover:text-pink-400 underline decoration-pink-500/30 underline-offset-4">Instagram Profile</a>}
                 </div>
               )}
             </div>
            
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
