'use client';

import React, { useState, useEffect, useRef } from 'react';
import { GitBranch, Info, Zap, Radio, Sliders, Shield } from 'lucide-react';

interface Node {
  id: string;
  label: string;
  type: string;
  category: string;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  type: string;
  label: string;
}

interface DependencyGraphProps {
  data: {
    nodes: Node[];
    edges: Edge[];
  };
}

export default function DependencyGraph({ data }: DependencyGraphProps) {
  const [nodePositions, setNodePositions] = useState<{ [key: string]: { x: number; y: number } }>({});
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  
  const containerRef = useRef<SVGSVGElement | null>(null);
  const draggingNodeRef = useRef<string | null>(null);
  const offsetRef = useRef({ x: 0, y: 0 });

  // Initialize node positions hierarchically
  useEffect(() => {
    if (!data || !data.nodes) return;
    
    const positions: { [key: string]: { x: number; y: number } } = {};
    const sources = data.nodes.filter(n => n.type === 'source');
    const controllers = data.nodes.filter(n => n.type === 'controller');
    const drivers = data.nodes.filter(n => n.type === 'driver');
    const mechanical = data.nodes.filter(n => n.type === 'mechanical');
    const peripherals = data.nodes.filter(n => n.type === 'peripheral' || n.type === 'default');

    // Layout configuration
    const width = 800;
    const height = 450;

    // Layer 1: Sources (top)
    sources.forEach((n, idx) => {
      positions[n.id] = {
        x: width / 2 + (idx - (sources.length - 1) / 2) * 200,
        y: 60
      };
    });

    // Layer 2: Controllers & Drivers
    const midLayer = [...controllers, ...drivers];
    midLayer.forEach((n, idx) => {
      positions[n.id] = {
        x: width / 2 + (idx - (midLayer.length - 1) / 2) * 180,
        y: 160
      };
    });

    // Layer 3: Peripherals
    peripherals.forEach((n, idx) => {
      positions[n.id] = {
        x: width / 2 + (idx - (peripherals.length - 1) / 2) * 140,
        y: 280
      };
    });

    // Layer 4: Mechanical (bottom or side)
    mechanical.forEach((n, idx) => {
      positions[n.id] = {
        x: width / 2 + (idx - (mechanical.length - 1) / 2) * 150,
        y: 380
      };
    });

    // Handle single nodes or edge cases
    data.nodes.forEach(n => {
      if (!positions[n.id]) {
        positions[n.id] = { x: 100 + Math.random() * 500, y: 100 + Math.random() * 200 };
      }
    });

    setNodePositions(positions);
  }, [data]);

  if (!data || !data.nodes) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <GitBranch className="w-12 h-12 mb-2 stroke-1 text-slate-600 animate-pulse" />
        <p>No dependency graphs compiled yet.</p>
      </div>
    );
  }

  // Mouse Drag Handlers
  const handleMouseDown = (nodeId: string, e: React.MouseEvent<SVGGElement>) => {
    draggingNodeRef.current = nodeId;
    const pos = nodePositions[nodeId];
    if (pos && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      // Mouse coordinates relative to SVG coordinate space
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      offsetRef.current = {
        x: mouseX - pos.x,
        y: mouseY - pos.y
      };
    }
    const clickedNode = data.nodes.find(n => n.id === nodeId);
    if (clickedNode) setSelectedNode(clickedNode);
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const draggingId = draggingNodeRef.current;
    if (draggingId && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      setNodePositions(prev => ({
        ...prev,
        [draggingId]: {
          x: Math.max(40, Math.min(rect.width - 40, mouseX - offsetRef.current.x)),
          y: Math.max(30, Math.min(rect.height - 30, mouseY - offsetRef.current.y))
        }
      }));
    }
  };

  const handleMouseUpOrLeave = () => {
    draggingNodeRef.current = null;
  };

  // Filtered edges
  const filteredEdges = data.edges.filter(edge => {
    if (activeFilter === "all") return true;
    return edge.type === activeFilter;
  });

  const getEdgeColor = (type: string) => {
    switch (type) {
      case "power": return "#ef4444"; // Red
      case "signal": return "#3b82f6"; // Blue
      case "communication": return "#eab308"; // Yellow
      case "mechanical": return "#a855f7"; // Purple
      default: return "#64748b"; // Slate
    }
  };

  const getNodeBorderColor = (type: string) => {
    switch (type) {
      case "source": return "border-red-500 text-red-400 bg-red-950/20";
      case "controller": return "border-blue-500 text-blue-400 bg-blue-950/20";
      case "driver": return "border-yellow-500 text-yellow-400 bg-yellow-950/20";
      case "mechanical": return "border-purple-500 text-purple-400 bg-purple-950/20";
      default: return "border-slate-700 text-slate-300 bg-slate-900/30";
    }
  };

  return (
    <div className="space-y-4">
      {/* Graph Toolbar Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-1.5 bg-slate-900/50 border border-slate-800 p-1 rounded-md">
          {["all", "power", "signal", "communication", "mechanical"].map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`text-[10px] font-mono uppercase tracking-wider px-3 py-1 rounded transition-all cursor-pointer ${
                activeFilter === filter
                  ? "bg-cyan-950/50 border border-cyan-800 text-cyan-400 font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
        <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
          <Info className="w-3.5 h-3.5 text-cyan-400" />
          <span>Interactive Diagram: drag nodes to re-organize connection layout.</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SVG Drawing Board */}
        <div className="lg:col-span-3 border border-slate-800/80 bg-zinc-950/60 rounded-xl relative overflow-hidden h-[480px]">
          <svg
            ref={containerRef}
            className="w-full h-full cursor-grab active:cursor-grabbing"
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUpOrLeave}
            onMouseLeave={handleMouseUpOrLeave}
          >
            {/* Gradients */}
            <defs>
              <linearGradient id="edge-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#0891b2" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.4" />
              </linearGradient>
            </defs>

            {/* Draw Connection Edges */}
            {filteredEdges.map((edge) => {
              const start = nodePositions[edge.source];
              const end = nodePositions[edge.target];
              if (!start || !end) return null;

              // Compute SVG path with Bezier curve
              const dx = end.x - start.x;
              const dy = end.y - start.y;
              const midY = start.y + dy / 2;
              const pathData = `M ${start.x} ${start.y} C ${start.x} ${midY}, ${end.x} ${midY}, ${end.x} ${end.y}`;

              const color = getEdgeColor(edge.type);

              return (
                <g key={edge.id} className="group">
                  <path
                    d={pathData}
                    fill="none"
                    stroke={color}
                    strokeWidth="1.5"
                    strokeOpacity="0.6"
                    className="transition-all duration-300 group-hover:stroke-opacity-100 group-hover:stroke-[2px]"
                  />
                  {/* Glowing layer */}
                  <path
                    d={pathData}
                    fill="none"
                    stroke={color}
                    strokeWidth="4"
                    strokeOpacity="0.15"
                    className="blur-xs pointer-events-none"
                  />
                  {/* Edge label */}
                  <text
                    x={start.x + dx / 2}
                    y={start.y + dy / 2 - 5}
                    textAnchor="middle"
                    fill={color}
                    fontSize="8"
                    fontFamily="monospace"
                    className="opacity-0 group-hover:opacity-100 transition-all pointer-events-none fill-slate-300 bg-slate-900"
                  >
                    {edge.label}
                  </text>
                </g>
              );
            })}

            {/* Draw Interactive Nodes */}
            {data.nodes.map((node) => {
              const pos = nodePositions[node.id];
              if (!pos) return null;

              const isSelected = selectedNode?.id === node.id;
              let fill = "#09090b";
              let stroke = "#3b82f6";
              if (node.type === 'source') { fill = "#ef444420"; stroke = "#ef4444"; }
              else if (node.type === 'controller') { fill = "#3b82f620"; stroke = "#3b82f6"; }
              else if (node.type === 'driver') { fill = "#eab30820"; stroke = "#eab308"; }
              else if (node.type === 'mechanical') { fill = "#a855f720"; stroke = "#a855f7"; }
              else { fill = "#1e293b50"; stroke = "#64748b"; }

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  onMouseDown={(e) => handleMouseDown(node.id, e)}
                  className="cursor-pointer group"
                >
                  {/* Glowing border if selected */}
                  <rect
                    x="-90"
                    y="-20"
                    width="180"
                    height="40"
                    rx="6"
                    fill="none"
                    stroke={stroke}
                    strokeWidth={isSelected ? 3 : 1}
                    className="transition-all group-hover:stroke-cyan-400 group-hover:shadow-lg"
                    style={{
                      filter: isSelected ? 'drop-shadow(0 0 4px ' + stroke + ')' : 'none'
                    }}
                  />
                  <rect
                    x="-90"
                    y="-20"
                    width="180"
                    height="40"
                    rx="6"
                    fill={fill}
                    className="transition-all fill-zinc-950/80"
                  />
                  {/* Label */}
                  <text
                    x="0"
                    y="3"
                    textAnchor="middle"
                    fill="#f8fafc"
                    fontSize="9"
                    fontFamily="monospace"
                    fontWeight="semibold"
                    className="pointer-events-none select-none text-slate-100"
                  >
                    {node.label.length > 28 ? `${node.label.substring(0, 25)}...` : node.label}
                  </text>
                  {/* Small Type Icon indicator */}
                  <circle
                    cx="-75"
                    cy="0"
                    r="4"
                    fill={stroke}
                  />
                </g>
              );
            })}
          </svg>
        </div>

        {/* Selected Node Details Card */}
        <div className="lg:col-span-1 space-y-4">
          <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/40 font-mono h-full flex flex-col justify-between">
            <div>
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-cyan-400" />
                Node Properties
              </h4>
              {selectedNode ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-[10px] text-slate-500 block">Component Name</span>
                    <span className="text-xs text-slate-200 font-bold block">{selectedNode.label}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Logical Role</span>
                    <span className="text-xs uppercase tracking-wider block font-bold" style={{ color: getEdgeColor(selectedNode.type === 'source' ? 'power' : selectedNode.type === 'controller' ? 'signal' : selectedNode.type === 'driver' ? 'communication' : 'mechanical') }}>
                      {selectedNode.type}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Category</span>
                    <span className="text-xs text-slate-300 block">{selectedNode.category}</span>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-500 italic p-2 border border-slate-900 border-dashed rounded text-center">
                  Click on any node block to view connection properties and specs.
                </div>
              )}
            </div>

            {/* Legend info */}
            <div className="border-t border-slate-800 pt-4 mt-4 space-y-2">
              <h5 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Dependency Types</h5>
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="w-3 h-1 bg-[#ef4444] rounded"></span>
                  <span className="text-slate-300">Power (Sinks/Sources)</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="w-3 h-1 bg-[#3b82f6] rounded"></span>
                  <span className="text-slate-300">Signal (Analog/PWM)</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="w-3 h-1 bg-[#eab308] rounded"></span>
                  <span className="text-slate-300">Communication (I2C/SPI)</span>
                </div>
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="w-3 h-1 bg-[#a855f7] rounded"></span>
                  <span className="text-slate-300">Mechanical Mounting</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
