'use client';

import React from 'react';
import { ShieldAlert, Zap, BatteryCharging, AlertTriangle } from 'lucide-react';

interface PowerItem {
  component: string;
  voltage: number;
  nominal_current: number;
  peak_current: number;
  standby_current: number;
  is_source: boolean;
}

interface PowerSummary {
  total_power_load_w: number;
  peak_current_a: number;
  peak_power_load_w: number;
  standby_load_ma: number;
  battery_voltage_v: number;
  battery_capacity_ah: number;
  estimated_runtime_hours: number;
  voltage_domains_count: number;
}

interface PowerAnalysisProps {
  data: {
    power_items: PowerItem[];
    summary: PowerSummary;
    warnings: string[];
  };
}

export default function PowerAnalysis({ data }: PowerAnalysisProps) {
  if (!data || !data.summary) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <Zap className="w-12 h-12 mb-2 stroke-1 text-slate-600 animate-pulse" />
        <p>No power analysis data compiled yet.</p>
      </div>
    );
  }

  const { power_items, summary, warnings } = data;

  return (
    <div className="space-y-6">
      {/* Warnings Banner */}
      {warnings && warnings.length > 0 && (
        <div className="border border-red-500/20 bg-red-950/20 p-4 rounded-lg flex items-start gap-3 shadow-lg shadow-red-950/20">
          <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider font-mono">Electrical Audit Alerts</h4>
            <ul className="list-disc pl-4 text-xs text-red-200/80 font-mono space-y-1">
              {warnings.map((warn, i) => (
                <li key={i}>{warn}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Summary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Total Power Load</div>
          <div className="text-2xl font-bold text-cyan-400">{summary.total_power_load_w} W</div>
          <div className="text-[9px] text-slate-500 mt-1">Based on nominal currents</div>
        </div>
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Peak Current Limit</div>
          <div className="text-2xl font-bold text-amber-400">{summary.peak_current_a} A</div>
          <div className="text-[9px] text-slate-500 mt-1">Peak transient limit: {summary.peak_power_load_w}W</div>
        </div>
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Battery Runtime</div>
          <div className="text-2xl font-bold text-emerald-400">
            {summary.battery_capacity_ah > 0 ? `${summary.estimated_runtime_hours} hrs` : "N/A"}
          </div>
          <div className="text-[9px] text-slate-500 mt-1">
            {summary.battery_capacity_ah > 0 
              ? `Capacity: ${summary.battery_capacity_ah}Ah @ ${summary.battery_voltage_v}V` 
              : "No battery source connected"}
          </div>
        </div>
        <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/30 font-mono">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Voltage Domains</div>
          <div className="text-2xl font-bold text-indigo-400">{summary.voltage_domains_count} rails</div>
          <div className="text-[9px] text-slate-500 mt-1">Isolate domains to prevent noise</div>
        </div>
      </div>

      {/* Components power table */}
      <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40">
        <h3 className="text-sm font-semibold text-cyan-400 glow-cyan mb-4 flex items-center gap-2 font-mono">
          <BatteryCharging className="w-4 h-4" />
          Component Operating Currents & Thresholds
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Component</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3 text-right">Rail Voltage</th>
                <th className="py-2.5 px-3 text-right">Nominal Draw</th>
                <th className="py-2.5 px-3 text-right">Peak Draw</th>
                <th className="py-2.5 px-3 text-right">Standby Draw</th>
              </tr>
            </thead>
            <tbody>
              {power_items.map((item, idx) => (
                <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/20 transition-all">
                  <td className="py-3 px-3 text-slate-200 font-semibold">{item.component}</td>
                  <td className="py-3 px-3">
                    {item.is_source ? (
                      <span className="text-[10px] bg-emerald-950/60 border border-emerald-800 text-emerald-400 px-2 py-0.5 rounded font-bold">SOURCE</span>
                    ) : (
                      <span className="text-[10px] bg-blue-950/60 border border-blue-800 text-blue-400 px-2 py-0.5 rounded font-bold">SINK</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-right text-slate-300 font-bold">{item.voltage} V</td>
                  <td className="py-3 px-3 text-right text-cyan-400">
                    {item.is_source ? "—" : `${item.nominal_current} mA`}
                  </td>
                  <td className="py-3 px-3 text-right text-amber-400">
                    {item.is_source ? "—" : `${item.peak_current} mA`}
                  </td>
                  <td className="py-3 px-3 text-right text-slate-400">
                    {item.is_source ? "—" : `${item.standby_current} mA`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Component Power Ratings list */}
      <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40 space-y-4">
        <h3 className="text-sm font-semibold text-cyan-400 glow-cyan flex items-center gap-2 font-mono">
          <Zap className="w-4 h-4 text-cyan-400" />
          Component Power Ratings list
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Component name</th>
                <th className="py-2.5 px-3 text-right">voltage rating</th>
                <th className="py-2.5 px-3 text-right">current rating</th>
                <th className="py-2.5 px-3 text-right">power rating</th>
              </tr>
            </thead>
            <tbody>
              {power_items.map((item, idx) => {
                const currentRating = item.is_source ? "—" : `${item.nominal_current} mA`;
                const powerRating = item.is_source 
                  ? "—" 
                  : `${((item.voltage * item.nominal_current) / 1000).toFixed(3)} W`;
                
                return (
                  <tr key={idx} className="border-b border-slate-900/60 hover:bg-slate-900/20 transition-all">
                    <td className="py-3 px-3 text-slate-200 font-semibold">{item.component}</td>
                    <td className="py-3 px-3 text-right text-slate-300">{item.voltage} V</td>
                    <td className="py-3 px-3 text-right text-cyan-400">{currentRating}</td>
                    <td className="py-3 px-3 text-right text-emerald-400 font-bold">{powerRating}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Copyable Markdown Format Area */}
        <div className="space-y-2 pt-2">
          <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase block">Copyable Markdown Format</span>
          <pre className="p-3 bg-slate-950 border border-slate-900 rounded text-[11px] text-slate-400 font-mono overflow-x-auto select-all max-h-[160px]">
{`Component name | voltage rating | current rating | power rating |\n` +
`---|---|---|---|\n` +
power_items.map(item => {
  const currentRating = item.is_source ? "—" : `${item.nominal_current} mA`;
  const powerRating = item.is_source 
    ? "—" 
    : `${((item.voltage * item.nominal_current) / 1000).toFixed(3)} W`;
  return `${item.component} | ${item.voltage} V | ${currentRating} | ${powerRating} |`;
}).join('\n')}
          </pre>
        </div>
      </div>
    </div>
  );
}
