import React from "react";
import { Thermometer, ShieldAlert, Cpu, HelpCircle } from "lucide-react";

interface ThermalReport {
  component: string;
  estimated_temp: number;
  max_temp: number;
  heat_w: number;
  risk_level: string;
  warning: string;
  cooling_recommendation: string;
}

interface ThermalRiskPanelProps {
  thermalReports?: ThermalReport[];
}

export default function ThermalRiskPanel({ thermalReports = [] }: ThermalRiskPanelProps) {
  return (
    <div className="space-y-6 p-4">
      {/* Overview stats */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4">
        <div className="flex items-center gap-2.5 border-b border-zinc-850 pb-3">
          <div className="p-1.5 bg-amber-950/30 border border-amber-800/40 rounded text-amber-400">
            <Thermometer className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Thermal Risk Analysis</h3>
            <p className="text-xs font-mono text-slate-500">Estimating operating temps and physical enclosure hazards based on datasheet thermal thresholds.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">Critical Risk Items</div>
            <div className="text-2xl font-mono font-black text-red-500">
              {thermalReports.filter(r => r.risk_level === "Critical").length}
            </div>
          </div>
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">High Risk Items</div>
            <div className="text-2xl font-mono font-black text-amber-500">
              {thermalReports.filter(r => r.risk_level === "High").length}
            </div>
          </div>
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">Max Est. Temp</div>
            <div className="text-2xl font-mono font-black text-slate-100">
              {thermalReports.length > 0 ? Math.max(...thermalReports.map(r => r.estimated_temp)) : 25}°C
            </div>
          </div>
          <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-lg text-center space-y-1">
            <div className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">Ambient Reference</div>
            <div className="text-2xl font-mono font-black text-slate-100">25.0°C</div>
          </div>
        </div>
      </div>

      {/* Grid of Component Risk cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {thermalReports.length > 0 ? (
          thermalReports.map((r, idx) => (
            <div key={idx} className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-2.5">
                <div className="flex items-center gap-2 min-w-0">
                  <Cpu className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                  <span className="text-xs font-mono font-bold text-slate-200 truncate">{r.component}</span>
                </div>
                <span className={`text-[9px] font-mono font-bold uppercase tracking-widest px-2 py-0.5 border rounded ${
                  r.risk_level === "Critical" ? "text-red-400 bg-red-950/20 border-red-800/40" :
                  r.risk_level === "High" ? "text-amber-400 bg-amber-950/20 border-amber-800/40" :
                  r.risk_level === "Medium" ? "text-yellow-400 bg-yellow-950/20 border-yellow-800/40" :
                  "text-slate-400 bg-slate-900/20 border-slate-800/40"
                }`}>
                  {r.risk_level}
                </span>
              </div>

              {/* Progress bars */}
              <div className="space-y-3">
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] font-mono">
                    <span className="text-slate-400">Estimated Temp</span>
                    <span className="text-slate-200 font-bold">{r.estimated_temp}°C / {r.max_temp}°C Limit</span>
                  </div>
                  <div className="w-full bg-zinc-900 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all ${
                        r.risk_level === "Critical" ? "bg-red-500" :
                        r.risk_level === "High" ? "bg-amber-500" :
                        r.risk_level === "Medium" ? "bg-yellow-500" :
                        "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.min(100, (r.estimated_temp / r.max_temp) * 100)}%` }}
                    />
                  </div>
                </div>

                <div className="flex justify-between text-[10px] font-mono text-slate-400">
                  <span>Power Dissipation:</span>
                  <span className="text-slate-300">{r.heat_w} W</span>
                </div>
              </div>

              {/* Warnings and Mitigation */}
              <div className="space-y-2 bg-zinc-900/40 p-3 rounded-lg border border-zinc-850">
                <div className="flex gap-2 items-start">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-500 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <div className="text-[9px] font-mono font-bold text-slate-400 uppercase tracking-widest">Warning Status</div>
                    <p className="text-[11px] font-mono text-slate-300">{r.warning}</p>
                  </div>
                </div>
                <div className="flex gap-2 items-start pt-2 border-t border-zinc-900">
                  <HelpCircle className="w-3.5 h-3.5 text-cyan-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0">
                    <div className="text-[9px] font-mono font-bold text-slate-400 uppercase tracking-widest">Cooling Recommendation</div>
                    <p className="text-[11px] font-mono text-cyan-400">{r.cooling_recommendation}</p>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-2 glass-panel p-8 text-center border border-zinc-800 bg-zinc-950/60 rounded-xl">
            <div className="text-sm font-mono text-slate-500 italic">No components available for thermal analysis.</div>
          </div>
        )}
      </div>
    </div>
  );
}
