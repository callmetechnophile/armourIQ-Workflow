'use client';

import React from 'react';
import { Calendar, CheckCircle2, ChevronRight } from 'lucide-react';

interface GanttTask {
  id: string;
  name: string;
  start: string;
  end: string;
  progress: number;
  dependencies: string;
  deliverable: string;
}

interface RoadmapPhase {
  phase: number;
  title: string;
  description: string;
  duration_days: number;
  deliverable: string;
}

interface GanttRoadmapProps {
  roadmap: RoadmapPhase[];
  gantt: GanttTask[];
}

export default function GanttRoadmap({ roadmap, gantt }: GanttRoadmapProps) {
  if (!roadmap || roadmap.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <Calendar className="w-12 h-12 mb-2 stroke-1 text-slate-600" />
        <p>No roadmap details generated yet.</p>
      </div>
    );
  }

  // Calculate coordinates for SVG Gantt Chart
  const taskHeight = 35;
  const gap = 15;
  const paddingLeft = 160;
  const chartHeight = gantt.length * (taskHeight + gap) + 40;
  
  // Estimate time grid
  const daysTotal = roadmap.reduce((sum, r) => sum + r.duration_days, 0) || 20;
  const scale = 22; // pixels per day
  const timelineWidth = daysTotal * scale;
  
  return (
    <div className="space-y-6">
      {/* Gantt Chart SVG */}
      <div className="glass-panel p-6 border border-blue-500/20 overflow-hidden">
        <div className="flex justify-between items-center mb-4 border-b border-blue-900/40 pb-3">
          <h3 className="text-md font-semibold text-cyan-400 glow-cyan flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Execution Timeline (Gantt Schedule)
          </h3>
          <span className="text-xs text-slate-400">Scale: 1 day = 22px</span>
        </div>
        
        <div className="overflow-x-auto pb-2">
          <svg width={paddingLeft + timelineWidth + 50} height={chartHeight} className="text-xs">
            {/* Grid Header Days */}
            {(() => {
              const textInterval = daysTotal > 50 ? 10 : (daysTotal > 20 ? 5 : 2);
              return Array.from({ length: daysTotal + 1 }).map((_, d) => {
                const x = paddingLeft + d * scale;
                return (
                  <g key={`grid-day-${d}`}>
                    <line 
                      x1={x} 
                      y1={25} 
                      x2={x} 
                      y2={chartHeight - 10} 
                      stroke="rgba(59, 130, 246, 0.08)" 
                      strokeWidth={1} 
                    />
                    {d % textInterval === 0 && (
                      <text x={x} y={15} fill="#64748b" textAnchor="middle" className="font-mono text-[9px]">
                        D{d}
                      </text>
                    )}
                  </g>
                );
              });
            })()}

            {/* Gantt Rows */}
            {(() => {
              const parseDate = (dStr: string) => {
                const parts = dStr.split('-');
                return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
              };
              const projectStart = gantt[0] ? parseDate(gantt[0].start) : new Date();

              return gantt.map((task, idx) => {
                const y = 30 + idx * (taskHeight + gap);
                const taskStart = parseDate(task.start);
                const taskEnd = parseDate(task.end);
                
                const dayOffset = Math.round((taskStart.getTime() - projectStart.getTime()) / (1000 * 3600 * 24));
                const duration = Math.round((taskEnd.getTime() - taskStart.getTime()) / (1000 * 3600 * 24)) || 1;
                
                const xStart = paddingLeft + dayOffset * scale;
                const barWidth = duration * scale;

                return (
                  <g key={task.id} className="group">
                    {/* Task Name Label */}
                    <text 
                      x={10} 
                      y={y + taskHeight / 2 + 4} 
                      fill="#e2e8f0" 
                      className="font-semibold text-[11px] select-none"
                    >
                      {task.name.length > 25 ? `${task.name.substring(0, 22)}...` : task.name}
                    </text>
                    
                    {/* Task bar container background */}
                    <rect 
                      x={xStart} 
                      y={y} 
                      width={barWidth} 
                      height={taskHeight} 
                      rx={4} 
                      fill="rgba(59, 130, 246, 0.05)" 
                      stroke="rgba(59, 130, 246, 0.15)"
                    />
                    
                    {/* Task progress fill */}
                    <rect 
                      x={xStart} 
                      y={y} 
                      width={barWidth * (task.progress / 100 || 0.15)} 
                      height={taskHeight} 
                      rx={4} 
                      fill="url(#gantt-gradient)" 
                    />
                    
                    {/* Progress Text overlay on hover */}
                    <text 
                      x={xStart + barWidth / 2} 
                      y={y + taskHeight / 2 + 4} 
                      fill="#ffffff" 
                      textAnchor="middle" 
                      className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-[10px] font-bold"
                    >
                      {task.progress > 0 ? `${task.progress}% Complete` : 'Scheduled'}
                    </text>
                    
                    {/* Connection line dependency arrow */}
                    {task.dependencies && (
                      <path
                        d={`M ${xStart - 10} ${y - gap} L ${xStart - 10} ${y + taskHeight / 2} L ${xStart} ${y + taskHeight / 2}`}
                        fill="none"
                        stroke="#f59e0b"
                        strokeWidth={1.2}
                        strokeDasharray="2 2"
                        className="opacity-70"
                      />
                    )}
                  </g>
                );
              });
            })()}
            
            {/* Defs for gradients */}
            <defs>
              <linearGradient id="gantt-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#2563eb" />
                <stop offset="100%" stopColor="#06b6d4" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>

      {/* Roadmap List View */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {roadmap.map((phase) => (
          <div key={`phase-${phase.phase}`} className="glass-panel p-5 border border-blue-500/10 hover:border-blue-500/30 transition-all duration-300 relative overflow-hidden group">
            {/* Cyber corner highlight */}
            <div className="absolute top-0 right-0 w-8 h-8 bg-blue-500/10 rounded-bl-3xl flex items-center justify-center border-l border-b border-blue-500/20 group-hover:bg-blue-500/20 transition-all duration-300">
              <span className="text-[10px] font-bold text-blue-400 font-mono">P{phase.phase}</span>
            </div>
            
            <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2 mb-2 pr-6">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-900/40 border border-blue-500/30 flex items-center justify-center text-xs text-cyan-400 font-mono">
                {phase.phase}
              </span>
              {phase.title}
            </h4>
            
            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              {phase.description}
            </p>
            
            <div className="border-t border-slate-800/60 pt-3 mt-1 flex flex-col gap-2">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Target Duration:</span>
                <span className="font-semibold text-amber-400 font-mono flex items-center gap-1">
                  {phase.duration_days} Days
                </span>
              </div>
              <div className="flex items-start gap-1.5 text-[11px]">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="text-slate-500 block">Phase Deliverable:</span>
                  <span className="text-emerald-400 font-medium">{phase.deliverable}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
