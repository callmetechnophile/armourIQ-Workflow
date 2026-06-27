'use client';

import React from 'react';
import { Activity, ShieldAlert, Zap } from 'lucide-react';

interface ExecutionReadinessProps {
  readiness: number;
  risk: number;
  optimization: number;
}

export default function ExecutionReadiness({ readiness = 80, risk = 30, optimization = 90 }: ExecutionReadinessProps) {
  // Helper to render radial circle paths
  const renderCircle = (val: number, strokeColor: string, size = 80, strokeWidth = 8) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (val / 100) * circumference;

    return (
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg className="transform -rotate-90" width={size} height={size}>
          {/* Background circle */}
          <circle
            className="text-slate-800"
            strokeWidth={strokeWidth}
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx={size / 2}
            cy={size / 2}
          />
          {/* Progress circle */}
          <circle
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            stroke={strokeColor}
            fill="transparent"
            r={radius}
            cx={size / 2}
            cy={size / 2}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <span className="absolute text-sm font-extrabold font-mono text-slate-100">
          {val}%
        </span>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Readiness Dial */}
      <div className="glass-panel p-5 border border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300 flex items-center gap-4 bg-cyan-950/5">
        {renderCircle(readiness, "#06b6d4", 90)}
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-cyan-400">
            <Activity className="w-4 h-4" />
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono">Readiness Index</h4>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug">
            {readiness >= 80 
              ? "All critical subsystems resolved. Recommended for staging prototype." 
              : "Subsystems contain critical mismatches. Review warnings."}
          </p>
        </div>
      </div>

      {/* Risk Dial */}
      <div className="glass-panel p-5 border border-red-500/20 hover:border-red-500/40 transition-all duration-300 flex items-center gap-4 bg-red-950/5">
        {renderCircle(risk, "#ef4444", 90)}
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-red-400">
            <ShieldAlert className="w-4 h-4" />
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono">Risk Index</h4>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug">
            {risk > 40 
              ? "High engineering conflict score. High risk of electrical/mechanical failure." 
              : "Low structural failure profile. Standard operating guidelines apply."}
          </p>
        </div>
      </div>

      {/* Optimization Dial */}
      <div className="glass-panel p-5 border border-amber-500/20 hover:border-amber-500/40 transition-all duration-300 flex items-center gap-4 bg-amber-950/5">
        {renderCircle(optimization, "#f59e0b", 90)}
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-amber-400">
            <Zap className="w-4 h-4" />
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono">Efficiency Index</h4>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug">
            {optimization >= 85 
              ? "Cost reduction suggestions integrated. Peak efficiency ratio achieved." 
              : "Additional cost savings possible by replacing high-end controllers."}
          </p>
        </div>
      </div>
    </div>
  );
}
