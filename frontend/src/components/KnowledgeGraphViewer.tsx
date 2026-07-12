'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Network, Info, Sliders, Shield, Zap, Search, HelpCircle, Layers } from 'lucide-react';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: any;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

interface KnowledgeGraphViewerProps {
  projectName: string;
  apiBase: string;
}

export default function KnowledgeGraphViewer({ projectName, apiBase }: KnowledgeGraphViewerProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const containerRef = useRef<SVGSVGElement | null>(null);
  const simulationRef = useRef<number | null>(null);
  const draggingNodeRef = useRef<string | null>(null);
  const dragOffsetRef = useRef({ x: 0, y: 0 });

  // Pan and Zoom State
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const isPanningRef = useRef(false);
  const panStartRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    async function fetchGraph() {
      setLoading(true);
      setError(null);
      try {
        const cleanName = projectName.replace(/ /g, "_");
        const res = await fetch(`${apiBase}/api/graph/project/${cleanName}`);
        if (!res.ok) throw new Error("Failed to fetch graph data");
        const data = await res.json();
        
        // Initialize positions
        const initializedNodes = (data.nodes || []).map((node: any) => ({
          ...node,
          x: 400 + (Math.random() - 0.5) * 300,
          y: 250 + (Math.random() - 0.5) * 200,
          vx: 0,
          vy: 0
        }));

        setNodes(initializedNodes);
        setEdges(data.edges || []);
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setLoading(false);
      }
    }
    if (projectName) {
      fetchGraph();
    }
  }, [projectName, apiBase]);

  // Force-directed layout simulation loop
  useEffect(() => {
    if (nodes.length === 0) return;

    const width = 800;
    const height = 500;
    const strengthRepulsion = 400; // Coulomb repulsion between nodes
    const strengthAttraction = 0.05; // Spring attraction along edges
    const centerAttraction = 0.01; // Attraction to center
    const damping = 0.85;

    function step() {
      // 1. Repulsion force between all nodes
      for (let i = 0; i < nodes.length; i++) {
        const nodeA = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const nodeB = nodes[j];
          if (!nodeA.x || !nodeA.y || !nodeB.x || !nodeB.y) continue;

          const dx = nodeB.x - nodeA.x;
          const dy = nodeB.y - nodeA.y;
          const distSq = dx * dx + dy * dy + 0.1;
          const dist = Math.sqrt(distSq);

          if (dist < 200) {
            const force = strengthRepulsion / distSq;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            if (nodeA.id !== draggingNodeRef.current) {
              nodeA.vx = (nodeA.vx || 0) - fx;
              nodeA.vy = (nodeA.vy || 0) - fy;
            }
            if (nodeB.id !== draggingNodeRef.current) {
              nodeB.vx = (nodeB.vx || 0) + fx;
              nodeB.vy = (nodeB.vy || 0) + fy;
            }
          }
        }
      }

      // 2. Attraction force along edges
      edges.forEach(edge => {
        const sourceNode = nodes.find(n => n.id === edge.source);
        const targetNode = nodes.find(n => n.id === edge.target);

        if (sourceNode && targetNode && sourceNode.x && sourceNode.y && targetNode.x && targetNode.y) {
          const dx = targetNode.x - sourceNode.x;
          const dy = targetNode.y - sourceNode.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 0.1;
          
          // Optimal spring length = 120px
          const force = (dist - 120) * strengthAttraction;
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;

          if (sourceNode.id !== draggingNodeRef.current) {
            sourceNode.vx = (sourceNode.vx || 0) + fx;
            sourceNode.vy = (sourceNode.vy || 0) + fy;
          }
          if (targetNode.id !== draggingNodeRef.current) {
            targetNode.vx = (targetNode.vx || 0) - fx;
            targetNode.vy = (targetNode.vy || 0) - fy;
          }
        }
      });

      // 3. Gravity center pull and update positions
      nodes.forEach(node => {
        if (node.id === draggingNodeRef.current) return;

        if (node.x && node.y) {
          const dx = width / 2 - node.x;
          const dy = height / 2 - node.y;

          node.vx = ((node.vx || 0) + dx * centerAttraction) * damping;
          node.vy = ((node.vy || 0) + dy * centerAttraction) * damping;

          node.x += node.vx;
          node.y += node.vy;

          // Boundary limits
          node.x = Math.max(50, Math.min(width - 50, node.x));
          node.y = Math.max(50, Math.min(height - 50, node.y));
        }
      });

      // React state update
      setNodes([...nodes]);
      simulationRef.current = requestAnimationFrame(step);
    }

    simulationRef.current = requestAnimationFrame(step);

    return () => {
      if (simulationRef.current) cancelAnimationFrame(simulationRef.current);
    };
  }, [edges]); // Re-run whenever topology (edges) are initialized

  const handleNodeMouseDown = (nodeId: string, e: React.MouseEvent<SVGGElement>) => {
    e.stopPropagation();
    draggingNodeRef.current = nodeId;
    const clickedNode = nodes.find(n => n.id === nodeId);
    if (clickedNode) {
      setSelectedNode(clickedNode);
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        // Mouse in SVG coordinate space taking zoom and pan into account
        const mouseX = (e.clientX - rect.left - pan.x) / zoom;
        const mouseY = (e.clientY - rect.top - pan.y) / zoom;
        dragOffsetRef.current = {
          x: mouseX - (clickedNode.x || 0),
          y: mouseY - (clickedNode.y || 0)
        };
      }
    }
  };

  const handleContainerMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    isPanningRef.current = true;
    panStartRef.current = {
      x: e.clientX - pan.x,
      y: e.clientY - pan.y
    };
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (draggingNodeRef.current && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const mouseX = (e.clientX - rect.left - pan.x) / zoom;
      const mouseY = (e.clientY - rect.top - pan.y) / zoom;

      setNodes(prev => prev.map(node => {
        if (node.id === draggingNodeRef.current) {
          return {
            ...node,
            x: mouseX - dragOffsetRef.current.x,
            y: mouseY - dragOffsetRef.current.y,
            vx: 0,
            vy: 0
          };
        }
        return node;
      }));
    } else if (isPanningRef.current) {
      setPan({
        x: e.clientX - panStartRef.current.x,
        y: e.clientY - panStartRef.current.y
      });
    }
  };

  const handleMouseUpOrLeave = () => {
    draggingNodeRef.current = null;
    isPanningRef.current = false;
  };

  const handleZoom = (factor: number) => {
    setZoom(prev => Math.max(0.3, Math.min(3, prev * factor)));
  };

  const resetPanZoom = () => {
    setPan({ x: 0, y: 0 });
    setZoom(1);
  };

  // Node Color Helper
  const getNodeColor = (type: string) => {
    switch (type) {
      case "Project": return { border: "#eab308", fill: "#eab30815" }; // Gold
      case "Component": return { border: "#3b82f6", fill: "#3b82f615" }; // Blue
      case "Microcontroller": return { border: "#6366f1", fill: "#6366f115" }; // Indigo
      case "Sensor": return { border: "#10b981", fill: "#10b98115" }; // Emerald
      case "Actuator":
      case "Motor": return { border: "#d946ef", fill: "#d946ef15" }; // Fuchsia
      case "Battery": return { border: "#f97316", fill: "#f9731615" }; // Orange
      case "Protocol": return { border: "#06b6d4", fill: "#06b6d415" }; // Cyan
      case "Pin": return { border: "#14b8a6", fill: "#14b8a615" }; // Teal
      case "Datasheet": return { border: "#84cc16", fill: "#84cc1615" }; // Lime
      case "ResearchPaper": return { border: "#ec4899", fill: "#ec489915" }; // Pink
      case "FailureMode": return { border: "#ef4444", fill: "#ef444415" }; // Red
      case "Vendor": return { border: "#a855f7", fill: "#a855f715" }; // Purple
      default: return { border: "#64748b", fill: "#64748b15" }; // Slate
    }
  };

  // Filter & Search Logic
  const filteredNodes = nodes.filter(node => {
    const matchesSearch = node.label.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          node.type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === "all" || node.type === filterType;
    return matchesSearch && matchesType;
  });

  const nodeTypesList = Array.from(new Set(nodes.map(n => n.type)));

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-400 font-mono">
        <Network className="w-12 h-12 mb-3 stroke-1 text-cyan-500 animate-spin" />
        <span className="text-xs">Querying AuraDB Engineering Knowledge Graph...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-400 font-mono border border-red-500/20 rounded bg-red-950/5">
        <Shield className="w-12 h-12 mb-3 stroke-1 text-red-500 animate-pulse" />
        <span className="text-xs text-red-400">Failed to load Knowledge Graph Layer: {error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search & Filtering Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search graph..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded pl-8 pr-3 py-1 text-xs text-slate-300 placeholder-slate-500 outline-none w-48 font-mono focus:border-cyan-800"
            />
          </div>
          <div className="flex items-center gap-1.5 bg-slate-900/50 border border-slate-800 p-1 rounded">
            <button
              onClick={() => setFilterType("all")}
              className={`text-[9px] font-mono uppercase tracking-wider px-2.5 py-0.5 rounded cursor-pointer ${
                filterType === "all" ? "bg-cyan-950 text-cyan-400 font-bold border border-cyan-800/40" : "text-slate-400"
              }`}
            >
              All Labels
            </button>
            {nodeTypesList.map(type => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`text-[9px] font-mono uppercase tracking-wider px-2.5 py-0.5 rounded cursor-pointer ${
                  filterType === type ? "bg-cyan-950 text-cyan-400 font-bold border border-cyan-800/40" : "text-slate-400"
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-0.5 rounded">
            <button onClick={() => handleZoom(1.2)} className="text-[10px] font-mono px-2 py-0.5 hover:text-white cursor-pointer">+</button>
            <button onClick={() => handleZoom(0.8)} className="text-[10px] font-mono px-2 py-0.5 hover:text-white cursor-pointer">-</button>
            <button onClick={resetPanZoom} className="text-[9px] font-mono px-2 py-0.5 border-l border-slate-800 hover:text-white cursor-pointer">Reset</button>
          </div>
          <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Info className="w-3.5 h-3.5 text-cyan-400" />
            <span>Interactive Graph: click node to inspect properties.</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SVG Graph Drawing Board */}
        <div className="lg:col-span-3 border border-slate-800/80 bg-zinc-950/60 rounded-xl relative overflow-hidden h-[500px]">
          <svg
            ref={containerRef}
            className="w-full h-full cursor-grab active:cursor-grabbing select-none"
            onMouseDown={handleContainerMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUpOrLeave}
            onMouseLeave={handleMouseUpOrLeave}
          >
            {/* Background Grid Pattern */}
            <defs>
              <pattern id="graph-grid" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#ffffff03" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#graph-grid)" />

            <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
              {/* Draw Edges */}
              {edges.map((edge, idx) => {
                const source = nodes.find(n => n.id === edge.source);
                const target = nodes.find(n => n.id === edge.target);
                if (!source || !target || !source.x || !source.y || !target.x || !target.y) return null;

                const color = getNodeColor(source.type).border;

                return (
                  <g key={`edge-${idx}`} className="group">
                    <line
                      x1={source.x}
                      y1={source.y}
                      x2={target.x}
                      y2={target.y}
                      stroke={color}
                      strokeWidth="1.2"
                      strokeOpacity="0.4"
                      className="transition-all duration-300 group-hover:stroke-opacity-90 group-hover:stroke-[1.8px]"
                    />
                    {/* Tiny Direction Arrow */}
                    <circle
                      cx={(source.x + target.x) / 2}
                      cy={(source.y + target.y) / 2}
                      r="2"
                      fill={color}
                      opacity="0.6"
                    />
                  </g>
                );
              })}

              {/* Draw Nodes */}
              {filteredNodes.map((node) => {
                if (!node.x || !node.y) return null;

                const isSelected = selectedNode?.id === node.id;
                const colors = getNodeColor(node.type);

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    onMouseDown={(e) => handleNodeMouseDown(node.id, e)}
                    className="cursor-pointer group"
                  >
                    {/* Glowing effect around node */}
                    <rect
                      x="-65"
                      y="-16"
                      width="130"
                      height="32"
                      rx="4"
                      fill="none"
                      stroke={colors.border}
                      strokeWidth={isSelected ? 3 : 1.2}
                      className="transition-all group-hover:stroke-cyan-400"
                      style={{
                        filter: isSelected ? `drop-shadow(0 0 5px ${colors.border})` : 'none'
                      }}
                    />
                    <rect
                      x="-65"
                      y="-16"
                      width="130"
                      height="32"
                      rx="4"
                      fill="#09090b"
                      fillOpacity="0.9"
                    />
                    <rect
                      x="-65"
                      y="-16"
                      width="130"
                      height="32"
                      rx="4"
                      fill={colors.fill}
                    />

                    {/* Node text */}
                    <text
                      x="0"
                      y="3"
                      textAnchor="middle"
                      fill="#f1f5f9"
                      fontSize="8.5"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      {node.label.length > 20 ? `${node.label.substring(0, 17)}...` : node.label}
                    </text>

                    {/* Small circle indicator of Type */}
                    <circle
                      cx="-55"
                      cy="0"
                      r="3.5"
                      fill={colors.border}
                    />
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Selected Node Details Panel */}
        <div className="lg:col-span-1 space-y-4">
          <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/40 font-mono h-full flex flex-col justify-between">
            <div>
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-cyan-400" />
                AuraDB Metadata
              </h4>
              {selectedNode ? (
                <div className="space-y-4">
                  <div>
                    <span className="text-[9px] text-slate-500 block">Label Name</span>
                    <span className="text-xs text-slate-200 font-bold block">{selectedNode.label}</span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-500 block">Node Label</span>
                    <span className="text-xs uppercase tracking-wider block font-bold text-cyan-400">
                      {selectedNode.type}
                    </span>
                  </div>
                  <div className="border-t border-slate-800/80 pt-3">
                    <span className="text-[9px] text-slate-500 block mb-1">Properties (JSON)</span>
                    <div className="bg-zinc-900/60 p-2.5 rounded border border-slate-850 overflow-y-auto max-h-[160px] text-[10px] text-slate-300 scrollbar-none">
                      {Object.keys(selectedNode.properties || {}).length > 0 ? (
                        Object.entries(selectedNode.properties).map(([k, v]) => (
                          <div key={k} className="mb-1 leading-normal">
                            <span className="text-cyan-500 font-semibold">{k}:</span> <span className="text-slate-100">{String(v)}</span>
                          </div>
                        ))
                      ) : (
                        <span className="text-slate-500 italic">No attributes.</span>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-500 italic p-3 border border-slate-900 border-dashed rounded text-center">
                  Click on any node to traverse and retrieve properties from AuraDB.
                </div>
              )}
            </div>

            {/* Colors Legend */}
            <div className="border-t border-slate-800 pt-4 mt-4 space-y-2">
              <h5 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Graph Legends</h5>
              <div className="grid grid-cols-2 gap-1.5 text-[9px]">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#eab308]"></span>
                  <span className="text-slate-400">Project</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#3b82f6]"></span>
                  <span className="text-slate-400">Component</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#06b6d4]"></span>
                  <span className="text-slate-400">Protocol</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#14b8a6]"></span>
                  <span className="text-slate-400">Pin</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#84cc16]"></span>
                  <span className="text-slate-400">Datasheet</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#ec4899]"></span>
                  <span className="text-slate-400">Research</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#ef4444]"></span>
                  <span className="text-slate-400">Failure Mode</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#a855f7]"></span>
                  <span className="text-slate-400">Vendor</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
