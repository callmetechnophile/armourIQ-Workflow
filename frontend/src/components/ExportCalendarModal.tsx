'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, X, Check, Loader2, Download, RefreshCw, Clock, Globe } from 'lucide-react';

interface ExportCalendarModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
  projectName: string;
}

export default function ExportCalendarModal({
  isOpen,
  onClose,
  projectId,
  projectName
}: ExportCalendarModalProps) {
  const [calendarType, setCalendarType] = useState<'Google' | 'Outlook' | 'Apple' | 'ICS'>('Google');
  const [timezone, setTimezone] = useState('UTC');
  const [reminders, setReminders] = useState<string[]>([
    '1 Day Before',
    '1 Hour Before',
    '15 Minutes Before'
  ]);
  const [loading, setLoading] = useState(false);
  const [updateExisting, setUpdateExisting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const detectedTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        if (detectedTz) {
          setTimezone(detectedTz);
        }
      } catch (e) {
        console.error('Failed to detect timezone:', e);
      }
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleReminderToggle = (reminder: string) => {
    if (reminders.includes(reminder)) {
      setReminders(reminders.filter((r) => r !== reminder));
    } else {
      setReminders([...reminders, reminder]);
    }
  };

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg('');

    // If download ICS file option is selected, trigger file download directly
    if (calendarType === 'ICS') {
      try {
        window.open(`/api/calendar/download-ics/${projectId}`, '_blank');
        setSuccessMsg('Download initiated successfully!');
        setLoading(false);
        setTimeout(() => {
          setSuccessMsg('');
          onClose();
        }, 3000);
      } catch (err) {
        alert('Failed to download calendar file.');
        setLoading(false);
      }
      return;
    }

    try {
      const res = await fetch('/api/calendar/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          calendar_type: calendarType,
          reminders,
          timezone,
          update_existing: updateExisting
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Export failed.');
      }

      const result = await res.json();
      
      if (calendarType === 'Apple' && result.download_url) {
        // Trigger download for apple .ics
        window.open(result.download_url, '_blank');
        setSuccessMsg('Apple Calendar event package generated and downloaded!');
      } else {
        setSuccessMsg(result.message || 'Export completed successfully!');
      }

      setLoading(false);
      setTimeout(() => {
        setSuccessMsg('');
        onClose();
      }, 4000);
    } catch (err: any) {
      alert(err.message || 'An error occurred during calendar export.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
      <div className="glass-panel border border-cyan-500/20 bg-zinc-950/95 max-w-md w-full rounded-xl relative p-6 space-y-5 shadow-2xl animate-fade-in font-mono">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
          <div className="flex items-center gap-2 text-cyan-400">
            <Calendar className="w-5 h-5" />
            <h3 className="text-xs font-bold uppercase tracking-widest">
              Export Project Timeline
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Project Context Summary */}
        <div className="bg-zinc-900/50 border border-zinc-850 p-3 rounded-lg text-[10px] text-slate-400 space-y-1">
          <div><span className="font-bold text-slate-300">Project:</span> {projectName}</div>
          <div><span className="font-bold text-slate-300">Location:</span> WorkflowGuide AI</div>
          <div><span className="font-bold text-slate-300">Default Scope:</span> calendar.export</div>
        </div>

        {successMsg ? (
          <div className="py-6 flex flex-col items-center justify-center text-center space-y-3">
            <div className="w-10 h-10 rounded-full bg-cyan-950/50 border border-cyan-500/30 flex items-center justify-center text-cyan-400 animate-pulse">
              <Check className="w-5 h-5" />
            </div>
            <p className="text-xs font-bold text-slate-200 uppercase tracking-wide">
              {successMsg}
            </p>
            <p className="text-[10px] text-slate-500">
              Closing export modal shortly...
            </p>
          </div>
        ) : (
          <form onSubmit={handleExport} className="space-y-4 text-xs">
            {/* Calendar Selection */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 uppercase font-semibold">Select Destination</label>
              <div className="grid grid-cols-2 gap-2 text-[10px] font-bold">
                {[
                  { id: 'Google', label: 'Google Calendar' },
                  { id: 'Outlook', label: 'Outlook Calendar' },
                  { id: 'Apple', label: 'Apple Calendar (.ics)' },
                  { id: 'ICS', label: 'Download ICS File' }
                ].map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setCalendarType(type.id as any)}
                    className={`p-2.5 rounded border transition-all text-left cursor-pointer flex items-center justify-between ${
                      calendarType === type.id
                        ? 'border-cyan-500 bg-cyan-950/20 text-cyan-400'
                        : 'border-zinc-850 bg-zinc-900/40 text-slate-400 hover:border-zinc-800'
                    }`}
                  >
                    {type.label}
                    {calendarType === type.id && <Check className="w-3.5 h-3.5" />}
                  </button>
                ))}
              </div>
            </div>

            {/* Timezone */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1">
                <Globe className="w-3.5 h-3.5 text-cyan-500" /> Detected Timezone
              </label>
              <input
                type="text"
                required
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="e.g. Asia/Kolkata"
                className="w-full bg-zinc-900 border border-zinc-850 rounded px-3 py-2 text-white outline-none focus:border-cyan-500 font-mono text-[11px]"
              />
            </div>

            {/* Reminders selection */}
            <div className="space-y-1.5">
              <label className="text-[10px] text-slate-400 uppercase font-semibold flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-cyan-500" /> Choose Reminders
              </label>
              <div className="bg-zinc-900/40 border border-zinc-850 rounded p-2.5 space-y-2">
                {[
                  '1 Day Before',
                  '1 Hour Before',
                  '15 Minutes Before'
                ].map((reminder) => (
                  <label key={reminder} className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={reminders.includes(reminder)}
                      onChange={() => handleReminderToggle(reminder)}
                      className="rounded bg-zinc-950 border-zinc-800 text-cyan-600 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5"
                    />
                    <span className="text-[10px] text-slate-300 font-medium">{reminder}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Project Updates Options Toggle */}
            <div className="bg-zinc-900/30 border border-zinc-850 p-2.5 rounded-lg">
              <label className="flex items-start gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={updateExisting}
                  onChange={(e) => setUpdateExisting(e.target.checked)}
                  className="rounded bg-zinc-950 border-zinc-800 text-cyan-600 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5 mt-0.5"
                />
                <div>
                  <span className="text-[10px] text-slate-200 font-bold block">Update Existing Events</span>
                  <span className="text-[8px] text-slate-500 leading-normal block mt-0.5">
                    Enable this option to synchronize/modify previously exported schedule items instead of creating duplicates.
                  </span>
                </div>
              </label>
            </div>

            {/* Actions */}
            <div className="flex gap-2 justify-end pt-2 border-t border-zinc-900">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-slate-400 px-4 py-2 rounded cursor-pointer font-bold disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-cyan-600 hover:bg-cyan-500 text-white px-5 py-2 rounded cursor-pointer font-bold flex items-center gap-1.5 disabled:opacity-50 shadow-lg shadow-cyan-900/20"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Exporting...
                  </>
                ) : updateExisting ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5" />
                    Update Events
                  </>
                ) : (
                  <>
                    <Download className="w-3.5 h-3.5" />
                    Export Calendar
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
