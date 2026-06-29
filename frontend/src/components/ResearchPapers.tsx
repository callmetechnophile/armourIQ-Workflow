'use client';

import React from 'react';
import { BookOpen, ExternalLink, FileText } from 'lucide-react';

interface PaperItem {
  id: string;
  title: string;
  authors: string;
  source: string;
  url: string;
  publish_year: number;
  citation_count: number;
}

interface PaperSummary {
  paper_id: string;
  title: string;
  summary: string;
  conclusions: string[];
  recommendations: string;
}

interface ResearchPapersProps {
  papers: PaperItem[];
  summary: PaperSummary;
}

export default function ResearchPapers({ papers, summary }: ResearchPapersProps) {
  if (!papers || papers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <BookOpen className="w-12 h-12 mb-2 stroke-1 text-slate-600" />
        <p>No research papers found.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Paper List */}
      <div className="lg:col-span-1 space-y-4">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2 mb-1">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          Retrieved References
        </h3>
        {papers.map((paper) => (
          <a 
            key={paper.id} 
            href={paper.url} 
            target="_blank" 
            rel="noreferrer"
            className="glass-panel p-4 border border-blue-500/10 hover:border-blue-500/30 hover:bg-slate-900/5 transition-all duration-200 block cursor-pointer"
          >
            <div className="flex justify-between items-start gap-2 mb-1">
              <h4 className="text-xs font-semibold text-slate-200 line-clamp-2 leading-tight">
                {paper.title}
              </h4>
              <span className="text-cyan-400 hover:text-cyan-300 transition-colors flex-shrink-0 mt-0.5">
                <ExternalLink className="w-3.5 h-3.5" />
              </span>
            </div>
            
            <p className="text-[10px] text-slate-400 mb-2">
              {paper.authors} • <span className="font-semibold">{paper.source}</span>
            </p>
            
            <div className="flex justify-between items-center text-[9px] text-slate-500 font-mono mt-1 border-t border-slate-800/40 pt-2">
              <span>Published: {paper.publish_year}</span>
              <span>Citations: {paper.citation_count}</span>
            </div>
          </a>
        ))}
      </div>

      {/* Primary Paper Analysis/Summary */}
      <div className="lg:col-span-2 space-y-4">
        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2 mb-1">
          <FileText className="w-4 h-4 text-cyan-400" />
          Deep Synthesis & Summary
        </h3>
        
        {summary && summary.summary ? (
          <div className="glass-panel p-6 border border-blue-500/20 bg-blue-950/5 space-y-4">
            <div>
              <h4 className="text-sm font-bold text-slate-100 mb-1 border-b border-slate-800 pb-2">
                {summary.title}
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed mt-2">
                {summary.summary}
              </p>
            </div>

            <div className="space-y-2">
              <h5 className="text-[11px] font-bold text-amber-400 uppercase tracking-wider font-mono">
                Key Technical Findings:
              </h5>
              <ul className="list-disc pl-4 space-y-1.5 text-xs text-slate-300">
                {summary.conclusions?.map((concl, i) => (
                  <li key={`concl-${i}`} className="leading-relaxed">
                    {concl}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-4">
              <h5 className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider font-mono mb-1">
                Architecture Integration Recommendation:
              </h5>
              <p className="text-xs text-slate-300 italic leading-relaxed">
                "{summary.recommendations}"
              </p>
            </div>
          </div>
        ) : (
          <div className="glass-panel p-6 border border-blue-500/10 text-center text-slate-400 text-xs">
            Select a paper to view its engineering synthesis.
          </div>
        )}
      </div>
    </div>
  );
}
