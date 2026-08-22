import React, { useState, useMemo, useRef } from 'react';
import { Bookmark, X, Search, Download, Upload } from 'lucide-react';
import { useStorageStore, PersonalItem } from '../../../core/store/useStorageStore';
import { useUIStore } from '../../../core/store/useUIStore';
import { useRegexStore } from '../../../core/store/useRegexStore';
import { getShareUrl } from '../../../shared/utils/link';
import { downloadPersonalDump, parsePersonalDump } from '../utils/dump';
import { PersonalToolbar } from './PersonalToolbar';
import { PersonalTableRow } from './PersonalTableRow';

export const PersonalPanel: React.FC = () => {
  const { personal, removePersonal, clearPersonal, updatePersonalItem, importPersonal } = useStorageStore();
  const { isPersonalOpen, setPersonalOpen } = useUIStore();
  const { setSelectedEngineId, setRegex, setText, setActiveFlags } = useRegexStore();

  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [groupBy, setGroupBy] = useState<'none' | 'engine' | 'tags'>('none');
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    try {
      const items = parsePersonalDump(await file.text());
      const added = importPersonal(items);
      setImportStatus(`Imported ${added} new item${added === 1 ? '' : 's'} (${items.length} in file).`);
    } catch (err) {
      setImportStatus(err instanceof Error ? err.message : 'Import failed.');
    }
    setTimeout(() => setImportStatus(null), 4000);
  };

  const filteredItems = personal.filter(item => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (item.name && item.name.toLowerCase().includes(q)) ||
      (item.regex && item.regex.toLowerCase().includes(q)) ||
      (item.text && item.text.toLowerCase().includes(q)) ||
      (item.engineLabel && item.engineLabel.toLowerCase().includes(q)) ||
      (item.tags && item.tags.some(t => t.toLowerCase().includes(q)))
    );
  });

  const grouped = useMemo(() => {
    if (groupBy === 'none') return { 'All Regex': filteredItems };
    if (groupBy === 'engine') {
      return filteredItems.reduce((acc, item) => {
        (acc[item.engineLabel] = acc[item.engineLabel] || []).push(item);
        return acc;
      }, {} as Record<string, PersonalItem[]>);
    }
    if (groupBy === 'tags') {
      const groups: Record<string, PersonalItem[]> = { 'Untagged': [] };
      filteredItems.forEach(item => {
        if (!item.tags || item.tags.length === 0) {
          groups['Untagged'].push(item);
        } else {
          item.tags.forEach(tag => {
            (groups[tag] = groups[tag] || []).push(item);
          });
        }
      });
      if (groups['Untagged'].length === 0) delete groups['Untagged'];
      return groups;
    }
    return { 'All Regex': filteredItems };
  }, [filteredItems, groupBy]);

  if (!isPersonalOpen) return null;

  const handleLoad = (item: PersonalItem) => {
    setSelectedEngineId(item.engineId);
    setRegex(item.regex);
    setText(item.text);
    setActiveFlags(item.flags);
    setPersonalOpen(false);
  };

  const handleCopyLink = (item: PersonalItem) => {
    const url = getShareUrl({
      engine_id: item.engineId,
      regex: item.regex,
      text: item.text,
      flags: item.flags
    });
    navigator.clipboard.writeText(url);
    setCopiedId(item.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 dark:bg-black/60 backdrop-blur-sm">
      <div className="bg-theme-base dark:bg-[#121216] border border-theme-border shadow-2xl rounded-[20px] w-full max-w-6xl flex flex-col max-h-[85vh] overflow-hidden">

        <div className="flex items-center justify-between px-6 py-4 bg-black/5 dark:bg-white/5 shrink-0">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-indigo-500/10 text-indigo-500`}>
              <Bookmark size={18} strokeWidth={2.5} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-theme-text uppercase tracking-widest">Personal Regex</h2>
              <p className="text-[10px] text-theme-muted font-mono mt-0.5">
                {personal.length} saved regex patterns
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {importStatus && (
              <span className="text-[10px] font-mono text-theme-muted">{importStatus}</span>
            )}
            {personal.length > 0 && (
              <button
                onClick={() => downloadPersonalDump(personal)}
                title="Export all saved patterns to a JSON file"
                aria-label="Export saved patterns to JSON"
                className="flex items-center gap-1.5 text-[10px] uppercase font-bold text-theme-muted hover:text-theme-text transition-colors"
              >
                <Download size={13} /> Export
              </button>
            )}
            <button
              onClick={() => fileInputRef.current?.click()}
              title="Import patterns from a JSON dump (merged with existing items)"
              aria-label="Import saved patterns from JSON"
              className="flex items-center gap-1.5 text-[10px] uppercase font-bold text-theme-muted hover:text-theme-text transition-colors"
            >
              <Upload size={13} /> Import
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/json,.json"
              onChange={handleImportFile}
              className="hidden"
            />
            {personal.length > 0 && (
              <button
                onClick={() => {
                  if (window.confirm('Are you sure you want to clear all personal items?')) clearPersonal();
                }}
                className="text-[10px] uppercase font-bold text-rose-500 hover:text-rose-600 transition-colors"
              >
                Clear All
              </button>
            )}
            <button
              onClick={() => setPersonalOpen(false)}
              className="p-2 text-theme-muted hover:text-theme-text hover:bg-black/5 dark:hover:bg-white/10 rounded-full transition-colors"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {personal.length > 0 && (
          <PersonalToolbar
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            groupBy={groupBy}
            setGroupBy={setGroupBy}
          />
        )}

        <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
          {personal.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-theme-muted opacity-60">
              <Bookmark size={48} className="mb-4" />
              <p className="text-sm font-mono">No saved items yet.</p>
              <p className="text-[10px]">Use the Save button in the Pattern Editor to store regexes here.</p>
            </div>
          ) : Object.keys(grouped).length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-theme-muted opacity-60">
              <Search size={48} className="mb-4" />
              <p className="text-sm font-mono">No matches found.</p>
              <p className="text-[10px]">Try adjusting your search query.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[900px]">
                <thead>
                  <tr className="border-b border-theme-border text-[10px] font-black text-theme-muted uppercase tracking-widest">
                    <th className="px-4 py-3 w-[150px]">Name</th>
                    <th className="px-4 py-3 w-[150px]">Tags</th>
                    <th className="px-4 py-3">Engine</th>
                    <th className="px-4 py-3">Pattern</th>
                    <th className="px-4 py-3">Subject</th>
                    <th className="px-4 py-3 text-center">Matches</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(grouped).map(([groupName, groupItems]) => (
                    <React.Fragment key={groupName}>
                      {groupBy !== 'none' && (
                        <tr className="bg-black/5 dark:bg-white/5 border-b border-theme-border">
                          <td colSpan={7} className="px-4 py-2 text-[10px] font-black uppercase tracking-widest text-theme-muted">
                            {groupName} <span className="opacity-50 ml-1">({groupItems.length})</span>
                          </td>
                        </tr>
                      )}
                      {groupItems.map((item) => (
                        <PersonalTableRow
                          key={item.id}
                          item={item}
                          handleLoad={handleLoad}
                          handleCopyLink={handleCopyLink}
                          removePersonal={removePersonal}
                          updatePersonalItem={updatePersonalItem}
                          copiedId={copiedId}
                        />
                      ))}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};