import React, { useState, useEffect } from "react";
import { Users, UserPlus, MessageSquare, Send, Activity, Shield } from "lucide-react";

interface Member {
  id: number;
  user_id: string;
  email: string;
  role: string;
  joined_at: string;
}

interface Comment {
  id: number;
  section: string;
  author: string;
  content: string;
  timestamp: string;
}

interface ActivityLog {
  id: number;
  user_id: string;
  action: string;
  details: string;
  timestamp: string;
}

interface TeamWorkspaceProps {
  teamData?: {
    team_id: number;
    team_name: string;
    members: Member[];
    comments: Comment[];
    activities: ActivityLog[];
  };
  projectId?: string;
  apiBase: string;
}

export default function TeamWorkspace({ teamData, projectId, apiBase }: TeamWorkspaceProps) {
  const [members, setMembers] = useState<Member[]>(teamData?.members || []);
  const [comments, setComments] = useState<Comment[]>(teamData?.comments || []);
  const [activities, setActivities] = useState<ActivityLog[]>(teamData?.activities || []);
  
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("Engineer");
  const [inviteTeamName, setInviteTeamName] = useState("");
  const [inviteResult, setInviteResult] = useState<any>(null);
  
  const [newComment, setNewComment] = useState("");
  const [commentSection, setCommentSection] = useState("General");
  
  const teamId = teamData?.team_id || 1;

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail || !inviteTeamName) return;
    try {
      const res = await fetch(`${apiBase}/api/collaboration/teams/invite-collaborator`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          team_name: inviteTeamName,
          email: inviteEmail,
          role: inviteRole
        })
      });
      if (res.ok) {
        const result = await res.json();
        setInviteResult(result);
        
        // Add invitee placeholder to local members view
        const placeholderMember = {
          id: result.team_id,
          user_id: `invited_user`,
          email: inviteEmail,
          role: inviteRole,
          joined_at: new Date().toISOString()
        };
        setMembers([...members, placeholderMember]);
        
        // Refresh logs
        fetchLogs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment) return;
    try {
      const res = await fetch(`${apiBase}/api/collaboration/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId || "BionicHand_System",
          section: commentSection,
          author: "current_user",
          content: newComment
        })
      });
      if (res.ok) {
        const added = await res.json();
        setComments([...comments, added]);
        setNewComment("");
        fetchLogs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${apiBase}/api/collaboration/activity/${teamId}`);
      if (res.ok) {
        const data = await res.json();
        setActivities(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 p-4">
      {/* Team Members List & Invite */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-6">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Team Members</h3>
          </div>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2 py-0.5 rounded">
            ID: {teamId}
          </span>
        </div>

        {/* Invite Form */}
        {!inviteResult ? (
          <form onSubmit={handleInvite} className="bg-zinc-900/60 p-4 border border-zinc-850 rounded-lg space-y-3">
            <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
              <UserPlus className="w-3.5 h-3.5 text-cyan-400" /> Invite Collaborator
            </div>
            <div className="space-y-2">
              <input
                type="text"
                required
                placeholder="New Team Name"
                value={inviteTeamName}
                onChange={(e) => setInviteTeamName(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
              />
              <input
                type="email"
                required
                placeholder="collaborator@company.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
              />
              <div className="flex gap-2">
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="flex-1 bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
                >
                  <option value="Engineer">Engineer</option>
                  <option value="Reviewer">Reviewer</option>
                  <option value="Viewer">Viewer</option>
                </select>
                <button
                  type="submit"
                  className="bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold px-4 py-2 rounded transition-all cursor-pointer"
                >
                  Invite
                </button>
              </div>
            </div>
          </form>
        ) : (
          <div className="bg-zinc-900/60 p-4 border border-cyan-800/20 rounded-lg space-y-3.5 text-xs font-mono">
            <h4 className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest border-b border-zinc-850 pb-1.5">
              Secure Team Invite Generated
            </h4>
            <div>
              <span className="text-[9px] text-slate-500 uppercase block font-semibold">Generated Numeric Team ID</span>
              <span className="text-xs text-white font-bold tracking-wider block bg-zinc-950 px-2 py-1 rounded border border-zinc-800 mt-1 select-all">{inviteResult.team_id_numeric}</span>
            </div>
            <div>
              <span className="text-[9px] text-slate-500 uppercase block font-semibold">Secure Joining Link</span>
              <span className="text-[10px] text-cyan-400 block bg-zinc-950 px-2 py-1 rounded border border-zinc-800 mt-1 select-all truncate">{inviteResult.invite_url}</span>
            </div>
            <div className="space-y-1">
              <span className="text-[9px] text-slate-500 uppercase block font-semibold">Email Subject</span>
              <div className="bg-zinc-950 border border-zinc-800 p-1.5 rounded text-slate-200 font-bold select-all text-[10px]">{inviteResult.email_subject}</div>
            </div>
            <div className="space-y-1">
              <span className="text-[9px] text-slate-500 uppercase block font-semibold">Email Body</span>
              <pre className="bg-zinc-950 border border-zinc-800 p-2.5 rounded text-slate-300 whitespace-pre-wrap select-all text-[9px] overflow-y-auto max-h-[140px] leading-normal">{inviteResult.email_body}</pre>
            </div>
            <button
              onClick={() => {
                setInviteResult(null);
                setInviteEmail("");
                setInviteTeamName("");
              }}
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs py-2 rounded transition-all cursor-pointer"
            >
              Done & Close
            </button>
          </div>
        )}

        {/* Members Cards */}
        <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
          {members.map((m) => (
            <div key={m.id} className="flex items-center justify-between p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
              <div className="min-w-0">
                <div className="text-xs font-mono font-bold text-slate-200 truncate">{m.email}</div>
                <div className="text-[10px] font-mono text-slate-500">Joined {new Date(m.joined_at).toLocaleDateString()}</div>
              </div>
              <span className={`text-[10px] font-mono font-bold uppercase tracking-widest px-2 py-0.5 border rounded ${
                m.role === "Owner" ? "text-red-400 bg-red-950/20 border-red-800/40" :
                m.role === "Engineer" ? "text-cyan-400 bg-cyan-950/20 border-cyan-800/40" :
                m.role === "Reviewer" ? "text-amber-400 bg-amber-950/20 border-amber-800/40" :
                "text-slate-400 bg-slate-900/20 border-slate-800/40"
              }`}>
                {m.role}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Discussion & Comments */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-6">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Comments Panel</h3>
          </div>
        </div>

        {/* Add Comment */}
        <form onSubmit={handleAddComment} className="bg-zinc-900/60 p-4 border border-zinc-850 rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">Section Focus</div>
            <select
              value={commentSection}
              onChange={(e) => setCommentSection(e.target.value)}
              className="bg-zinc-950 border border-zinc-800 rounded px-2 py-1 text-[10px] font-mono text-slate-300 focus:outline-none focus:border-purple-500"
            >
              <option value="General">General</option>
              <option value="BOM">BOM</option>
              <option value="Wiring">Wiring</option>
              <option value="Power">Power</option>
              <option value="Research">Research</option>
              <option value="Code">Code</option>
            </select>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ask a question or request a review..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-purple-500"
            />
            <button
              type="submit"
              className="bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs font-bold p-2.5 rounded transition-all"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>

        {/* Comments Feed */}
        <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
          {comments.map((c) => (
            <div key={c.id} className="p-3 bg-zinc-900/20 border border-zinc-850 rounded-lg space-y-1.5">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-1">
                <span className="text-[10px] font-mono font-extrabold text-slate-400">{c.author}</span>
                <span className="text-[9px] font-mono text-purple-400 uppercase tracking-wider bg-purple-950/20 px-1.5 border border-purple-900/30 rounded">
                  {c.section}
                </span>
              </div>
              <p className="text-xs font-mono text-slate-300">{c.content}</p>
              <div className="text-[8px] font-mono text-slate-500 text-right">
                {new Date(c.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Activity Feed */}
      <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-6">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Activity Feed</h3>
          </div>
        </div>

        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
          {activities.map((a) => (
            <div key={a.id} className="flex gap-2.5 items-start p-3 bg-zinc-900/30 border border-zinc-850 rounded-lg">
              <div className="p-1.5 bg-emerald-950/30 border border-emerald-800/40 rounded mt-0.5 text-emerald-400">
                <Shield className="w-3.5 h-3.5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-mono text-slate-300">
                  <span className="font-extrabold text-slate-400">{a.user_id}</span> {a.details}
                </div>
                <div className="text-[8px] font-mono text-slate-500 mt-1">
                  {new Date(a.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
