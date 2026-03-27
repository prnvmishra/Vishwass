import React from 'react';
import { motion } from 'framer-motion';

export default function RiskGauge({ score, hideLabels = false }: { score: number, hideLabels?: boolean }) {
  const getRiskColor = (s: number) => {
    if (s < 40) return 'text-green-500';
    if (s < 70) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getRiskStroke = (s: number) => {
    if (s < 40) return 'stroke-green-500';
    if (s < 70) return 'stroke-yellow-500';
    return 'stroke-red-500';
  };

  const getRiskLabel = (s: number) => {
    if (s < 40) return 'Low Risk';
    if (s < 70) return 'Medium Risk';
    return 'High Risk';
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 glass-card relative overflow-hidden h-full">
      <div className="relative w-56 h-56 flex items-center justify-center">
        {/* SVG Circle Gauge */}
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" fill="none" className="stroke-slate-800" strokeWidth="8" />
          <motion.circle 
            cx="50" cy="50" r="45" fill="none" 
            className={`${getRiskStroke(score)}`} 
            strokeWidth="8" strokeLinecap="round"
            initial={{ strokeDasharray: "0 283" }}
            animate={{ strokeDasharray: `${(score / 100) * 283} 283` }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-6xl font-bold font-mono text-white">{score}</span>
          <span className="text-sm text-slate-400 mt-1">/ 100</span>
        </div>
      </div>
      {!hideLabels && (
        <motion.h2 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1 }}
          className={`text-3xl font-bold mt-6 ${getRiskColor(score)}`}
        >
          {getRiskLabel(score)}
        </motion.h2>
      )}
    </div>
  );
}
