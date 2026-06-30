'use client';

import React from 'react';
import { Cpu, Download, RefreshCw } from 'lucide-react';

interface PinConnection {
  component: string;
  pin: string;
  connected_to: string;
  type: string; // "I2C", "SPI", "UART", "PWM", "Analog", "Digital"
}

interface PinMappingTableProps {
  pins?: PinConnection[];
}

export default function PinMappingTable({ pins }: PinMappingTableProps) {
  const downloadCSV = () => {
    if (!pins || pins.length === 0) return;
    const headers = ["Component", "Pin", "Connected To", "Type"];
    const csvContent = [
      headers.join(","),
      ...pins.map(p => `"${p.component}","${p.pin}","${p.connected_to}","${p.type}"`)
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "pin_mapping_config.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="glass-panel border border-blue-500/20 bg-slate-900/10 p-5 space-y-4">
      <div className="flex justify-between items-center border-b border-blue-900/40 pb-3">
        <div className="flex items-center gap-2.5">
          <Cpu className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wider">
            Pin Configuration Table
          </h3>
        </div>
        
        {pins && pins.length > 0 && (
          <button 
            onClick={downloadCSV}
            className="text-[10px] font-mono flex items-center gap-1.5 bg-blue-950/40 px-2.5 py-1.5 border border-blue-900/30 rounded text-cyan-400 hover:bg-blue-900/40 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            Download Pin CSV
          </button>
        )}
      </div>

      {!pins || pins.length === 0 ? (
        <div className="text-center py-6 text-xs text-slate-500 font-mono">
          [SYSTEM NOTICE]: Pin connection configuration is idle. Submit a query to generate wiring boards.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-widest text-[9px]">
                <th className="py-2.5 px-3">Controller Component</th>
                <th className="py-2.5 px-3">Controller Pin</th>
                <th className="py-2.5 px-3">Connected Peripheral</th>
                <th className="py-2.5 px-3 text-right">Protocol Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/30">
              {pins.map((pin, idx) => {
                let badgeColor = "bg-slate-950/60 border-slate-800 text-slate-400";
                if (pin.type === "I2C") badgeColor = "bg-blue-950/30 border-blue-900/30 text-blue-400";
                else if (pin.type === "SPI") badgeColor = "bg-purple-950/30 border-purple-900/30 text-purple-400";
                else if (pin.type === "UART") badgeColor = "bg-cyan-950/30 border-cyan-900/30 text-cyan-400";
                else if (pin.type === "PWM") badgeColor = "bg-amber-950/30 border-amber-900/30 text-amber-400";
                else if (pin.type === "Analog") badgeColor = "bg-emerald-950/30 border-emerald-900/30 text-emerald-400";

                return (
                  <tr key={idx} className="hover:bg-slate-900/30 transition-all">
                    <td className="py-3.5 px-3 text-slate-400">{pin.component}</td>
                    <td className="py-3.5 px-3 font-semibold text-slate-200">{pin.pin}</td>
                    <td className="py-3.5 px-3 text-cyan-300 font-medium">{pin.connected_to}</td>
                    <td className="py-3.5 px-3 text-right">
                      <span className={`inline-block text-[9px] font-extrabold px-2 py-0.5 border rounded uppercase ${badgeColor}`}>
                        {pin.type}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
