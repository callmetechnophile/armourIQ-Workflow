'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Network, Info, Sliders, Shield, Zap, Search, Eye, RefreshCw, Users, BookOpen, Layers, Clock, AlertTriangle, Cpu, Terminal, GitFork, UserCheck } from 'lucide-react';

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

interface GraphExplorerProps {
  projectName: string;
  apiBase: string;
}

export default function GraphExplorer({ projectName, apiBase }: GraphExplorerProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [explorerQuery, setExplorerQuery] = useState<string>("");

  const containerRef = useRef<SVGSVGElement | null>(null);
  const simulationRef = useRef<number | null>(null);
  const draggingNodeRef = useRef<string | null>(null);
  const dragOffsetRef = useRef({ x: 0, y: 0 });

  // Pan and Zoom
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const isPanningRef = useRef(false);
  const panStartRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    async function loadEKG() {
      if (!projectName) return;
      setLoading(true);
      setError(null);
      try {
        const cleanName = projectName.replace(/ /g, "_");
        const res = await fetch(`${apiBase}/api/graph/explorer/project/${cleanName}`);
        if (!res.ok) throw new Error("AuraDB connection error. Verify database status.");
        const data = await res.json();
        
        // Map nodes into positions — normalise both flat and React-Flow-nested shapes
        const initializedNodes = (data.nodes || []).map((node: any, idx: number) => {
          const col = idx % 4;
          const row = Math.floor(idx / 4); // ← was `idx // 4` (JS comment, always 0!)
          // Backend may return ReactFlow shape: { id, data: { label, type, properties } }
          // or flat shape: { id, label, type, properties }
          const label      = node.label      ?? node.data?.label      ?? node.id;
          const type       = node.type       ?? node.data?.type       ?? "Component";
          const properties = node.properties ?? node.data?.properties ?? {};
          return {
            id: node.id,
            label,
            type,
            properties,
            x: 80 + col * 200 + (Math.random() - 0.5) * 40,
            y: 85 + row * 110 + (Math.random() - 0.5) * 30,
            vx: 0,
            vy: 0
          };
        });

        // Resolve edge mappings — handle both flat and ReactFlow edge shapes
        const formattedEdges = (data.edges || []).map((e: any) => ({
          source: e.source,
          target: e.target,
          type: e.label || e.type || e.data?.label || "CONNECTED_TO"
        }));

        setNodes(initializedNodes);
        setEdges(formattedEdges);
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setLoading(false);
      }
    }

    loadEKG();
  }, [projectName, apiBase]);

  // Force-directed simulation step loop
  useEffect(() => {
    if (nodes.length === 0) return;

    const width = 850;
    const height = 500;
    const strengthRepulsion = 600;
    const strengthAttraction = 0.08;
    const centerAttraction = 0.015;
    const damping = 0.8;

    function step() {
      // Repulsion between nodes
      for (let i = 0; i < nodes.length; i++) {
        const nodeA = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const nodeB = nodes[j];
          if (!nodeA.x || !nodeA.y || !nodeB.x || !nodeB.y) continue;

          const dx = nodeB.x - nodeA.x;
          const dy = nodeB.y - nodeA.y;
          const distSq = dx * dx + dy * dy + 0.1;
          const dist = Math.sqrt(distSq);

          if (dist < 180) {
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

      // Spring attraction along edges
      edges.forEach(edge => {
        const sourceNode = nodes.find(n => n.id === edge.source);
        const targetNode = nodes.find(n => n.id === edge.target);

        if (sourceNode && targetNode && sourceNode.x && sourceNode.y && targetNode.x && targetNode.y) {
          const dx = targetNode.x - sourceNode.x;
          const dy = targetNode.y - sourceNode.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 0.1;
          
          const force = (dist - 110) * strengthAttraction;
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

      // Gravity pull to center
      nodes.forEach(node => {
        if (node.id === draggingNodeRef.current) return;

        if (node.x && node.y) {
          const dx = width / 2 - node.x;
          const dy = height / 2 - node.y;

          node.vx = ((node.vx || 0) + dx * centerAttraction) * damping;
          node.vy = ((node.vy || 0) + dy * centerAttraction) * damping;

          node.x += node.vx;
          node.y += node.vy;

          // Boundaries
          node.x = Math.max(50, Math.min(width - 50, node.x));
          node.y = Math.max(50, Math.min(height - 50, node.y));
        }
      });

      setNodes([...nodes]);
      simulationRef.current = requestAnimationFrame(step);
    }

    simulationRef.current = requestAnimationFrame(step);

    return () => {
      if (simulationRef.current) cancelAnimationFrame(simulationRef.current);
    };
  }, [edges]);

  const handleNodeMouseDown = (nodeId: string, e: React.MouseEvent<SVGGElement>) => {
    e.stopPropagation();
    draggingNodeRef.current = nodeId;
    const clickedNode = nodes.find(n => n.id === nodeId);
    if (clickedNode) {
      setSelectedNode(clickedNode);
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
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
    setZoom(prev => Math.max(0.3, Math.min(2.5, prev * factor)));
  };

  const resetPanZoom = () => {
    setPan({ x: 0, y: 0 });
    setZoom(1);
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case "Project": return { border: "#eab308", fill: "#eab30815" }; // Gold
      case "User": return { border: "#3b82f6", fill: "#3b82f615" }; // Blue
      case "Team": return { border: "#a855f7", fill: "#a855f715" }; // Purple
      case "Component": return { border: "#6366f1", fill: "#6366f115" }; // Indigo
      case "Vendor": return { border: "#d946ef", fill: "#d946ef15" }; // Fuchsia
      case "ResearchPaper": return { border: "#ec4899", fill: "#ec489915" }; // Pink
      case "Datasheet": return { border: "#14b8a6", fill: "#14b8a615" }; // Teal
      case "Battery": return { border: "#f97316", fill: "#f9731615" }; // Orange
      case "Sensor": return { border: "#10b981", fill: "#10b98115" }; // Emerald
      case "Protocol": return { border: "#06b6d4", fill: "#06b6d415" }; // Cyan
      case "Code": return { border: "#0284c7", fill: "#0284c715" }; // Sky
      case "Agent": return { border: "#0891b2", fill: "#0891b215" }; // Cyan/Teal
      case "FailureMode": return { border: "#ef4444", fill: "#ef444415" }; // Red
      default: return { border: "#64748b", fill: "#64748b15" };
    }
  };

  const getEdgeColor = (type: string) => {
    switch (type) {
      case "POWERED_BY": return "#f97316";
      case "CONNECTED_TO": return "#06b6d4";
      case "COMMUNICATES_VIA": return "#10b981";
      case "DELEGATES_TO": return "#a855f7";
      case "CONTRADICTS": return "#ef4444";
      default: return "#475569";
    }
  };

  // Traversal Expansion click
  const handleNodeDoubleClick = async (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    // Dynamically retrieve node details / expansions
    try {
      const cleanName = node.label.replace(/ /g, "_");
      let endpoint = `/api/graph/explorer/component/${cleanName}`;
      if (node.type === "Team") endpoint = `/api/graph/explorer/team/${cleanName}`;
      else if (node.type === "User") endpoint = `/api/graph/explorer/user/${cleanName}`;
      else if (node.type === "Project") endpoint = `/api/graph/explorer/project/${cleanName}`;
      
      const res = await fetch(endpoint);
      if (res.ok) {
        const data = await res.json();
        
        // Merge nodes
        const currentIds = new Set(nodes.map(n => n.id));
        const newNodes: GraphNode[] = [];
        
        (data.nodes || []).forEach((n: any) => {
          if (!currentIds.has(n.id)) {
            newNodes.push({
              ...n,
              x: (node.x || 400) + (Math.random() - 0.5) * 150,
              y: (node.y || 250) + (Math.random() - 0.5) * 150,
              vx: 0,
              vy: 0
            });
          }
        });
        
        // Merge edges
        const currentEdgeKeys = new Set(edges.map(e => `${e.source}_${e.target}`));
        const newEdges: GraphEdge[] = [];
        (data.edges || []).forEach((e: any) => {
          const key = `${e.source}_${e.target}`;
          if (!currentEdgeKeys.has(key)) {
            newEdges.push({
              source: e.source,
              target: e.target,
              type: e.label || e.type
            });
          }
        });

        setNodes([...nodes, ...newNodes]);
        setEdges([...edges, ...newEdges]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Filters & Search Highlight
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
        <span className="text-xs">Querying AuraDB EKG Reasoner...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-400 font-mono border border-red-500/20 rounded bg-red-950/5">
        <Shield className="w-12 h-12 mb-3 stroke-1 text-red-500" />
        <span className="text-xs text-red-400">EKG Offline: {error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Graph Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search EKG..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-350 placeholder-slate-500 outline-none w-48 font-mono focus:border-cyan-800"
            />
          </div>
          
          <div className="flex items-center gap-1 bg-slate-900/50 border border-slate-800 p-0.5 rounded overflow-x-auto max-w-[350px] scrollbar-none">
            <button
              onClick={() => setFilterType("all")}
              className={`text-[9px] font-mono uppercase tracking-wider px-2.5 py-0.5 rounded cursor-pointer whitespace-nowrap ${
                filterType === "all" ? "bg-cyan-950 text-cyan-400 font-bold border border-cyan-800/40" : "text-slate-400"
              }`}
            >
              All
            </button>
            {nodeTypesList.map(type => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`text-[9px] font-mono uppercase tracking-wider px-2.5 py-0.5 rounded cursor-pointer whitespace-nowrap ${
                  filterType === type ? "bg-cyan-950 text-cyan-400 font-bold border border-cyan-800/40" : "text-slate-400"
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-0.5 rounded">
            <button onClick={() => handleZoom(1.15)} className="text-[10px] font-mono px-2 py-0.5 hover:text-white cursor-pointer">+</button>
            <button onClick={() => handleZoom(0.85)} className="text-[10px] font-mono px-2 py-0.5 hover:text-white cursor-pointer">-</button>
            <button onClick={resetPanZoom} className="text-[9px] font-mono px-2 py-0.5 border-l border-slate-800 hover:text-white cursor-pointer">Reset</button>
          </div>
          <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Info className="w-3.5 h-3.5 text-cyan-400" />
            <span>Double click node to traverse expand.</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas Board */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 border border-slate-800/80 bg-zinc-950/60 rounded-xl relative overflow-hidden h-[520px]">
          <svg
            ref={containerRef}
            className="w-full h-full cursor-grab active:cursor-grabbing select-none"
            onMouseDown={handleContainerMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUpOrLeave}
            onMouseLeave={handleMouseUpOrLeave}
          >
            {/* Background Grid */}
            <defs>
              <pattern id="ekg-grid" width="25" height="25" patternUnits="userSpaceOnUse">
                <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#ffffff03" strokeWidth="0.8" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#ekg-grid)" />

            <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
              {/* Draw Edges */}
              {edges.map((edge, idx) => {
                const source = nodes.find(n => n.id === edge.source);
                const target = nodes.find(n => n.id === edge.target);
                if (!source || !target || !source.x || !source.y || !target.x || !target.y) return null;

                const color = getEdgeColor(edge.type);

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
                      className="transition-all duration-300 group-hover:stroke-opacity-95 group-hover:stroke-[1.8px]"
                    />
                    {/* Edge Label text along paths */}
                    <text
                      x={(source.x + target.x) / 2}
                      y={(source.y + target.y) / 2 - 4}
                      textAnchor="middle"
                      fill={color}
                      fontSize="7"
                      fontFamily="monospace"
                      opacity="0.8"
                      className="pointer-events-none fill-slate-400"
                    >
                      {edge.type}
                    </text>
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
                    onDoubleClick={(e) => handleNodeDoubleClick(node.id, e)}
                    className="cursor-pointer group"
                  >
                    {/* Glowing outer box */}
                    <rect
                      x="-65"
                      y="-16"
                      width="130"
                      height="32"
                      rx="5"
                      fill="none"
                      stroke={colors.border}
                      strokeWidth={isSelected ? 3 : 1.2}
                      style={{
                        filter: isSelected ? `drop-shadow(0 0 4px ${colors.border})` : 'none'
                      }}
                    />
                    <rect
                      x="-65"
                      y="-16"
                      width="130"
                      height="32"
                      rx="5"
                      fill="#09090b"
                      fillOpacity="0.9"
                    />
                    <rect
                      x="-65"
                      y="-16"
                      width="130"
                      height="32"
                      rx="5"
                      fill={colors.fill}
                    />

                    {/* Text Label */}
                    <text
                      x="0"
                      y="3"
                      textAnchor="middle"
                      fill="#f8fafc"
                      fontSize="8"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      {node.label.length > 20 ? `${node.label.substring(0, 17)}...` : node.label}
                    </text>

                    {/* Node indicator */}
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

        {/* Selected Node Details side panel */}
        <div className="lg:col-span-1 space-y-4">
          <div className="glass-panel p-4 border border-blue-500/20 bg-zinc-950/40 font-mono h-full flex flex-col justify-between">
            <div>
              <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-4 flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-cyan-400" />
                EKG Entity Details
              </h4>
              {selectedNode ? (
                <div className="space-y-4 text-xs">
                  <div>
                    <span className="text-[9px] text-slate-500 block">Name</span>
                    <span className="text-xs text-slate-200 font-bold block">{selectedNode.label}</span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-500 block">Label Label</span>
                    <span className="text-xs uppercase tracking-wider block font-bold text-cyan-400">
                      {selectedNode.type}
                    </span>
                  </div>
                  
                  {/* Entity Specific Custom Fields */}
                  {selectedNode.type === "Component" && (
                    <div className="border-t border-slate-850 pt-3.5 space-y-2">
                      <div>
                        <span className="text-[9px] text-slate-500 block">Category</span>
                        <span className="text-slate-350">{selectedNode.properties?.category || "Core Module"}</span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 block">Est. Cost</span>
                        <span className="text-slate-350 font-bold">${selectedNode.properties?.cost || 0.0} USD</span>
                      </div>
                    </div>
                  )}

                  {selectedNode.type === "Team" && (
                    <div className="border-t border-slate-850 pt-3.5 space-y-2">
                      <div>
                        <span className="text-[9px] text-slate-500 block">Members count</span>
                        <span className="text-slate-350">{selectedNode.properties?.members || 1} Collaborators</span>
                      </div>
                      <div>
                        <span className="text-[9px] text-slate-500 block">Workspace uuid</span>
                        <span className="text-slate-350 font-bold text-[10px] break-all">{selectedNode.properties?.uuid || "N/A"}</span>
                      </div>
                    </div>
                  )}

                  {selectedNode.type === "Project" && (
                    <div className="border-t border-slate-850 pt-3.5 space-y-2">
                      <div>
                        <span className="text-[9px] text-slate-500 block">Evolution Version</span>
                        <span className="text-slate-350 font-bold flex items-center gap-1">
                          <GitFork className="w-3.5 h-3.5 text-cyan-400" />
                          v1 &rarr; v2 &rarr; v3
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="border-t border-slate-850 pt-3.5">
                    <span className="text-[9px] text-slate-500 block mb-1">Properties (JSON)</span>
                    <div className="bg-zinc-900/60 p-2.5 border border-slate-850 rounded overflow-y-auto max-h-[160px] text-[10px] text-slate-300 scrollbar-none leading-normal">
                      {Object.keys(selectedNode.properties || {}).length > 0 ? (
                        Object.entries(selectedNode.properties).map(([k, v]) => (
                          <div key={k} className="mb-1.5">
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
                  Click on any node to query properties from AuraDB. Double-click to traverse expand.
                </div>
              )}
            </div>

            {/* Colors Legend */}
            <div className="border-t border-slate-800 pt-4 mt-4 space-y-2">
              <h5 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">EKG Legends</h5>
              <div className="grid grid-cols-2 gap-1.5 text-[9px]">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#eab308]"></span>
                  <span className="text-slate-400">Project</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#3b82f6]"></span>
                  <span className="text-slate-400">User</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#a855f7]"></span>
                  <span className="text-slate-400">Team</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#6366f1]"></span>
                  <span className="text-slate-400">Component</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#ec4899]"></span>
                  <span className="text-slate-400">Paper</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#ef4444]"></span>
                  <span className="text-slate-400">Failure Mode</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
