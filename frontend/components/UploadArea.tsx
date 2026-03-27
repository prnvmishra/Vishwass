"use client";
import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileType, CheckCircle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

interface UploadAreaProps {
  onFileSelect: (file: File) => void;
  isAnalyzing: boolean;
}

export default function UploadArea({ onFileSelect, isAnalyzing }: UploadAreaProps) {
  const [file, setFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1,
    disabled: isAnalyzing
  });

  return (
    <div className="w-full max-w-2xl mx-auto mt-10">
      <div 
        {...getRootProps()} 
        className={clsx(
          "glass-panel p-10 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 relative overflow-hidden group hover:border-blue-500/50",
          isDragActive ? "border-blue-500 bg-blue-500/10" : "border-slate-700/50",
          isAnalyzing ? "opacity-70 cursor-not-allowed" : ""
        )}
      >
        <input {...getInputProps()} />
        
        {/* Glow effect */}
        <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl" />
        
        <AnimatePresence mode="wait">
          {isAnalyzing ? (
            <motion.div 
              key="analyzing"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center text-blue-400 z-10"
            >
              <Loader2 className="w-16 h-16 animate-spin mb-4" />
              <h3 className="text-xl font-semibold">Analyzing your offer...</h3>
              <p className="text-slate-400 mt-2 text-center text-sm">
                Running multi-signal risk checks & AI document analysis
              </p>
            </motion.div>
          ) : file ? (
            <motion.div 
              key="success"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center text-green-400 z-10"
            >
              <CheckCircle className="w-16 h-16 mb-4 drop-shadow-[0_0_15px_rgba(74,222,128,0.5)]" />
              <h3 className="text-xl font-semibold text-white">{file.name}</h3>
              <p className="text-slate-400 mt-2 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </motion.div>
          ) : (
            <motion.div 
              key="upload"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex flex-col items-center text-slate-300 z-10"
            >
              <div className="w-20 h-20 rounded-full bg-slate-800/80 flex items-center justify-center mb-6 shadow-inner border border-slate-700/50 group-hover:scale-110 transition-transform duration-300">
                <UploadCloud className="w-10 h-10 text-blue-400" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Drag & drop your offer letter</h3>
              <p className="text-slate-400 text-center mb-6">Support for PDF, PNG, JPG files</p>
              
              <div className="flex gap-4 items-center">
                <span className="flex items-center gap-2 text-sm text-slate-500 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
                  <FileType className="w-4 h-4" /> PDF format
                </span>
                <span className="flex items-center gap-2 text-sm text-slate-500 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
                  <FileType className="w-4 h-4" /> Image format
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
