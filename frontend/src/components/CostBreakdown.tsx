'use client';

import React, { useEffect, useState } from 'react';
import { DollarSign, Layers, CheckCircle2, TrendingDown } from 'lucide-react';

interface Alternative {
  name: string;
  type: string;
  reason: string;
  approx_cost_usd: number;
}

interface ComponentItem {
  category: string;
  name: string;
  cost: number;
  notes: string;
  alternatives?: Alternative[];
}

interface CostBreakdownProps {
  components: ComponentItem[];
  costSummary?: {
    total_cost_inr: number;
    subtotals_inr: Record<string, number>;
  };
}

export default function CostBreakdown({ components, costSummary }: CostBreakdownProps) {
  const conversionRate = 83;
  const [selectedCosts, setSelectedCosts] = useState<Record<string, number>>({});

  // Initialize selected costs from components
  useEffect(() => {
    const initial: Record<string, number> = {};
    components.forEach((comp) => {
      initial[comp.name] = comp.cost * conversionRate;
    });
    setSelectedCosts(initial);
  }, [components]);

  // Handle alternative component replacement cost update
  const handleSwapCost = (compName: string, inrCost: number) => {
    setSelectedCosts(prev => ({
      ...prev,
      [compName]: inrCost
    }));
  };

  // Helper to categorize components
  const getCategoryGroup = (category: string, name: string = "") => {
    const cat = (category || "").toLowerCase();
    const nm = (name || "").toLowerCase();
    
    if (anyMatch(cat, ["power", "energy", "solar", "battery", "esc", "charger", "supply", "voltage"]) ||
        anyMatch(nm, ["battery", "solar", "power supply", "charger", "esc"])) {
      return "Power";
    }
    
    if (anyMatch(cat, ["electronics", "navigation", "sensor", "controller", "board", "flight", "gps", "receiver", "mcu", "cpu", "processor", "led", "display", "screen", "wire", "module", "communication", "actuator", "indicator"]) ||
        anyMatch(nm, ["esp32", "arduino", "pico", "sensor", "led", "wire", "gps", "display", "screen", "transceiver", "mcu", "controller"])) {
      return "Electronics";
    }
    
    return "Mechanical";
  };

  const anyMatch = (str: string, keywords: string[]) => {
    return keywords.some(k => str.includes(k));
  };

  // Recalculate subtotals and total dynamically
  const subtotals: Record<string, number> = {
    Electronics: 0,
    Mechanical: 0,
    Power: 0
  };

  components.forEach((comp) => {
    const catGroup = getCategoryGroup(comp.category, comp.name);
    const activeCost = selectedCosts[comp.name] ?? (comp.cost * conversionRate);
    subtotals[catGroup] += Math.round(activeCost);
  });

  const totalCost = Object.values(subtotals).reduce((a, b) => a + b, 0);

  return (
    <div className="glass-panel border border-emerald-500/20 bg-slate-900/10 p-5 space-y-5">
      <div className="flex justify-between items-center border-b border-emerald-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <Layers className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Total Build Cost Engine
          </h3>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 border border-emerald-900/30 rounded uppercase font-bold">
          Live Estimate
        </span>
      </div>

      {/* Large Total Build Cost display */}
      <div className="bg-slate-950/80 border border-emerald-500/10 rounded-lg p-5 text-center space-y-1">
        <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest font-bold">
          Total Estimated Build Cost
        </div>
        <div className="text-3xl font-mono font-extrabold text-emerald-400 glow-emerald tracking-wide">
          ₹{totalCost.toLocaleString('en-IN')}
        </div>
        <div className="text-[9px] font-mono text-slate-400">
          Conversion rate: 1 USD = ₹{conversionRate} INR
        </div>
      </div>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
        {Object.entries(subtotals).map(([category, amt]) => {
          let catBorder = "border-slate-800";
          let catText = "text-slate-400";
          if (category === "Electronics") {
            catBorder = "border-blue-500/20";
            catText = "text-blue-400";
          } else if (category === "Power") {
            catBorder = "border-cyan-500/20";
            catText = "text-cyan-400";
          } else {
            catBorder = "border-amber-500/20";
            catText = "text-amber-400";
          }

          return (
            <div key={category} className={`bg-zinc-950/40 p-4 border ${catBorder} rounded-lg flex flex-col justify-between space-y-2`}>
              <span className={`text-[10px] font-bold uppercase tracking-wider ${catText}`}>
                {category}
              </span>
              <span className="text-lg font-bold text-slate-200">
                ₹{amt.toLocaleString('en-IN')}
              </span>
            </div>
          );
        })}
      </div>

      {/* Dynamic component swapper helper */}
      {components.some(c => c.alternatives && c.alternatives.length > 0) && (
        <div className="space-y-2 font-mono text-[10px] pt-1">
          <span className="text-slate-500 uppercase font-bold tracking-wider">Dynamic Price Optimization Swaps</span>
          <div className="divide-y divide-slate-800/40 max-h-[160px] overflow-y-auto pr-1">
            {components
              .filter(c => c.alternatives && c.alternatives.length > 0)
              .map((comp) => {
                const currentCost = selectedCosts[comp.name] ?? (comp.cost * conversionRate);
                const originalCost = comp.cost * conversionRate;
                
                return (
                  <div key={comp.name} className="flex justify-between items-center py-2">
                    <span className="text-slate-400 font-medium max-w-[200px] truncate">{comp.name}</span>
                    <div className="flex items-center gap-2">
                      <select 
                        value={currentCost}
                        onChange={(e) => handleSwapCost(comp.name, Number(e.target.value))}
                        className="bg-slate-950 border border-slate-800 rounded p-1 text-[9px] text-slate-300 outline-none"
                      >
                        <option value={originalCost}>Original (₹{Math.round(originalCost)})</option>
                        {comp.alternatives?.map((alt, i) => (
                          <option key={i} value={alt.approx_cost_usd * conversionRate}>
                            {alt.name.split(" ")[0]} (₹{Math.round(alt.approx_cost_usd * conversionRate)})
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}
