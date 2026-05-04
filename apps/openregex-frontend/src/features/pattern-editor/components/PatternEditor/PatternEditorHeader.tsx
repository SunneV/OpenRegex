import React, { useState, useMemo, useRef, useEffect } from 'react';
import { Activity, Share2, Check, Lightbulb, Trash2, BookmarkPlus, Save, ChevronDown, Clock, Undo2, Redo2, Bookmark, ChevronLeft, ChevronRight } from 'lucide-react';
import { useRegexStore } from '../../../../core/store/useRegexStore';
import { useSelectionStore } from '../../../../core/store/useSelectionStore';
import { useOptimizedSelectionStore } from '../../../../core/store/useOptimizedSelectionStore';
import { useUIStore } from '../../../../core/store/useUIStore';
import { useLLMStore } from '../../../../core/store/useLLMStore';
import { useStorageStore } from '../../../../core/store/useStorageStore';
import type { EngineFlag } from '../../../../core/types';
import { getShareUrl } from '../../../../shared/utils/link';

type FlagGroup = 'Basic' | 'Advance' | 'Unique';

const normalizeFlagGroup = (group?: string): FlagGroup => {
  const normalized = (group || '').trim().toLowerCase();
  if (normalized === 'advance') return 'Advance';
  if (normalized === 'unique') return 'Unique';
  return 'Basic';
};

const getFlagColors = (group: FlagGroup, isActive: boolean) => {
  switch (group) {
    case 'Advance':
      return isActive
        ? 'bg-indigo-500/20 border-indigo-500/30 text-indigo-700 dark:text-indigo-300'
        : 'bg-indigo-500/5 border-indigo-500/10 text-indigo-600/70 dark:text-indigo-400/70 hover:bg-indigo-500/10 hover:text-indigo-600 dark:hover:text-indigo-400';
    case 'Unique':
      return isActive
        ? 'bg-amber-500/20 border-amber-500/30 text-amber-700 dark:text-amber-300'
        : 'bg-amber-500/5 border-amber-500/10 text-amber-600/70 dark:text-amber-400/70 hover:bg-amber-500/10 hover:text-amber-600 dark:hover:text-amber-400';
    case 'Basic':
    default:
      return isActive
        ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-700 dark:text-emerald-300'
        : 'bg-emerald-500/5 border-emerald-500/10 text-emerald-600/70 dark:text-emerald-400/70 hover:bg-emerald-500/10 hover:text-emerald-600 dark:hover:text-emerald-400';
  }
};

export const PatternEditorHeader: React.FC = () => {
  const regex = useRegexStore(state => state.regex);
  const text = useRegexStore(state => state.text);
  const activeFlags = useRegexStore(state => state.activeFlags);
  const toggleFlag = useRegexStore(state => state.toggleFlag);
  const engines = useRegexStore(state => state.engines);
  const selectedEngineId = useRegexStore(state => state.selectedEngineId);
  const setSelectedEngineId = useRegexStore(state => state.setSelectedEngineId);
  const setRegex = useRegexStore(state => state.setRegex);
  const setText = useRegexStore(state => state.setText);
  const setActiveFlags = useRegexStore(state => state.setActiveFlags);
  const handleClear = useRegexStore(state => state.handleClear);
  const handleLoadExample = useRegexStore(state => state.handleLoadExample);
  const matches = useRegexStore(state => state.matches);

  const originalSelection = useSelectionStore();
  const optimizedSelection = useOptimizedSelectionStore();
  const setCompatibilityReportOpen = useUIStore(state => state.setCompatibilityReportOpen);
  const optimizationProposal = useLLMStore(state => state.optimizationProposal);

  const { addPersonal, history, historyIndex, setHistoryIndex, personal } = useStorageStore();

  const [copied, setCopied] = useState(false);
  const [historySaved, setHistorySaved] = useState(false);
  const [isSaveMenuOpen, setIsSaveMenuOpen] = useState(false);
  const [isHistoryMenuOpen, setIsHistoryMenuOpen] = useState(false);

  const [isNamingSave, setIsNamingSave] = useState(false);
  const [customSaveName, setCustomSaveName] = useState('');

  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const saveMenuRef = useRef<HTMLDivElement>(null);
  const historyMenuRef = useRef<HTMLDivElement>(null);
  const flagsContainerRef = useRef<HTMLDivElement>(null);

  const checkScroll = () => {
    if (flagsContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = flagsContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  useEffect(() => {
    checkScroll();
    window.addEventListener('resize', checkScroll);
    return () => window.removeEventListener('resize', checkScroll);
  }, []);

  const handleScroll = (direction: 'left' | 'right') => {
    if (flagsContainerRef.current) {
      const scrollAmount = 150;
      flagsContainerRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (saveMenuRef.current && !saveMenuRef.current.contains(e.target as Node)) {
        setIsSaveMenuOpen(false);
        setIsNamingSave(false);
      }
      if (historyMenuRef.current && !historyMenuRef.current.contains(e.target as Node)) {
        setIsHistoryMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const activeEngine = engines.find(e => e.engine_id === selectedEngineId);
  const availableFlags = activeEngine?.engine_capabilities.flags || [];
  const isOptimizationMode = optimizationProposal !== null;

  const handleShareClick = () => {
    const shareUrl = getShareUrl({ engine_id: selectedEngineId, regex, text, flags: activeFlags });
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const executeSave = (name?: string) => {
    addPersonal({
      name,
      engineId: selectedEngineId,
      engineLabel: activeEngine?.engine_label || selectedEngineId,
      regex,
      text,
      flags: activeFlags,
      matchCount: matches.length
    });
    setHistorySaved(true);
    setTimeout(() => setHistorySaved(false), 2000);
    setIsSaveMenuOpen(false);
    setIsNamingSave(false);
    setCustomSaveName('');
  };

  const handleSaveQuick = () => executeSave();

  const canUndo = historyIndex < history.length - 1 && history.length > 0;
  const canRedo = historyIndex > 0;

  const loadHistoryItem = (index: number) => {
    if (index >= 0 && index < history.length) {
      const item = history[index];
      setSelectedEngineId(item.engineId);
      setRegex(item.regex);
      setText(item.text);
      setActiveFlags(item.flags);
      setHistoryIndex(index);
    }
    setIsHistoryMenuOpen(false);
  };

  const handleUndo = () => {
    const nextIndex = historyIndex === -1 ? 1 : historyIndex + 1;
    loadHistoryItem(nextIndex);
  };

  const handleRedo = () => {
    if (historyIndex > 0) loadHistoryItem(historyIndex - 1);
  };

  const groupedFlags = useMemo(() => {
    const basic: EngineFlag[] = [];
    const advance: EngineFlag[] = [];
    const unique: EngineFlag[] = [];

    availableFlags.forEach(flag => {
      const normalizedGroup = normalizeFlagGroup(flag.group);
      if (normalizedGroup === 'Basic') basic.push(flag);
      else if (normalizedGroup === 'Advance') advance.push(flag);
      else unique.push(flag);
    });

    const sortAlphabetically = (a: EngineFlag, b: EngineFlag) => a.name.localeCompare(b.name);
    basic.sort(sortAlphabetically);
    advance.sort(sortAlphabetically);
    unique.sort(sortAlphabetically);

    return { basic, advance, unique };
  }, [availableFlags]);

  const renderFlagGroup = (flags: EngineFlag[]) => {
    return flags.map(flag => {
      const group = normalizeFlagGroup(flag.group);
      const colorClass = getFlagColors(group, activeFlags.includes(flag.name));

      return (
        <button
          key={flag.name}
          onClick={() => toggleFlag(flag.name)}
          title={flag.description}
          className={`font-mono text-[10px] px-1.5 py-0.5 rounded-sm border transition-colors shrink-0 ${colorClass}`}
        >
          /{flag.name}
        </button>
      );
    });
  };

  return (
    <div className="component-header flex flex-wrap md:flex-nowrap items-center justify-between gap-2 w-full relative">
      {/* Left - Label & Main Actions */}
      <div className="flex items-center gap-3 justify-start z-20 shrink-0">
        <div className="flex items-center gap-2">
           <label className="component-label m-0">Pattern</label>
           {isOptimizationMode && <span className="text-[9px] font-black uppercase text-theme-muted/50 tracking-wider bg-black/5 dark:bg-white/5 px-2 py-0.5 rounded-full border border-theme-border shadow-sm">Split View</span>}
        </div>

        <div className="flex items-center gap-1 bg-black/5 dark:bg-white/5 p-0.5 rounded-lg border border-black/5 dark:border-white/5">
          <button onClick={handleUndo} disabled={!canUndo} className="p-1 text-theme-muted hover:text-theme-text hover:bg-black/5 dark:hover:bg-white/10 rounded disabled:opacity-30 disabled:hover:bg-transparent transition-colors" title="Undo">
            <Undo2 size={12} strokeWidth={2.5} />
          </button>
          <button onClick={handleRedo} disabled={!canRedo} className="p-1 text-theme-muted hover:text-theme-text hover:bg-black/5 dark:hover:bg-white/10 rounded disabled:opacity-30 disabled:hover:bg-transparent transition-colors" title="Redo">
            <Redo2 size={12} strokeWidth={2.5} />
          </button>
          <div className="relative" ref={historyMenuRef}>
            <button onClick={() => setIsHistoryMenuOpen(!isHistoryMenuOpen)} className="p-1 text-theme-muted hover:text-theme-text hover:bg-black/5 dark:hover:bg-white/10 rounded transition-colors" title="Execution History">
              <Clock size={12} strokeWidth={2.5} />
            </button>
            {isHistoryMenuOpen && (
              <div className="absolute top-full left-0 mt-1 w-72 max-h-64 bg-theme-base dark:bg-[#121216] backdrop-blur-md rounded-md border border-theme-border shadow-xl z-50 overflow-y-auto custom-scrollbar flex flex-col p-1">
                {history.length === 0 ? (
                  <div className="p-3 text-[10px] text-theme-muted text-center font-mono italic">No history yet. Executions auto-save here.</div>
                ) : (
                  history.map((h, i) => {
                    const isPersonal = personal.some(p => p.regex === h.regex && p.text === h.text && p.engineId === h.engineId && JSON.stringify(p.flags) === JSON.stringify(h.flags));
                    const isCurrent = historyIndex === -1 ? i === 0 : historyIndex === i;
                    return (
                      <div key={h.id} className="relative group/item">
                        <button onClick={() => loadHistoryItem(i)} className={`w-full flex items-center justify-between px-2 py-1.5 text-left text-[10px] font-mono rounded transition-colors ${isCurrent ? 'bg-theme-primary/10 text-theme-primary font-bold' : 'text-theme-text hover:bg-black/5 dark:hover:bg-white/5'}`}>
                          <div className="truncate flex-1 pr-2 flex flex-col">
                            <span className="truncate">{h.regex || '<Empty Regex>'}</span>
                          </div>
                          {isPersonal && <Bookmark size={10} className="text-emerald-500 shrink-0" />}
                        </button>
                        <div className="absolute hidden group-hover/item:block top-0 right-full mr-2 w-64 bg-theme-base border border-theme-border p-2 rounded-md shadow-2xl z-[100] text-[10px] font-mono break-all text-theme-text whitespace-pre-wrap pointer-events-none">
                          {h.regex || '<Empty Regex>'}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 border-l border-ide-border pl-2 shrink-0">
          <div className="relative flex items-stretch border border-transparent hover:border-ide-border rounded-md group" ref={saveMenuRef}>
            <button onClick={handleSaveQuick} className="p-1.5 text-indigo-500 hover:bg-black/5 dark:hover:bg-white/5 rounded-l-md transition-colors" title="Quick Save to Personal">
              {historySaved ? <Check size={14} strokeWidth={2.5} className="text-emerald-500" /> : <Save size={14} strokeWidth={2.5} />}
            </button>
            <button onClick={() => setIsSaveMenuOpen(!isSaveMenuOpen)} className="p-1 text-indigo-500 hover:bg-black/5 dark:hover:bg-white/5 rounded-r-md transition-colors border-l border-transparent group-hover:border-ide-border" title="Save Options">
              <ChevronDown size={12} strokeWidth={2.5} />
            </button>
            {isSaveMenuOpen && (
              <div className="absolute top-full left-0 mt-1 w-48 bg-theme-base dark:bg-[#121216] backdrop-blur-md rounded-md border border-theme-border shadow-xl z-[60] flex flex-col p-1">
                {isNamingSave ? (
                  <div className="p-2 flex flex-col gap-2">
                    <input
                      autoFocus
                      type="text"
                      placeholder="Regex name..."
                      value={customSaveName}
                      onChange={(e) => setCustomSaveName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          executeSave(customSaveName.trim());
                        } else if (e.key === 'Escape') {
                          setIsNamingSave(false);
                          setCustomSaveName('');
                        }
                      }}
                      className="bg-black/5 dark:bg-white/5 border border-theme-border rounded px-2 py-1 text-[10px] text-theme-text outline-none focus:ring-1 focus:ring-indigo-500 w-full"
                    />
                    <div className="flex gap-1">
                      <button onClick={() => executeSave(customSaveName.trim())} className="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white text-[9px] font-bold py-1 rounded transition-colors">Save</button>
                      <button onClick={() => { setIsNamingSave(false); setCustomSaveName(''); }} className="flex-1 bg-black/10 dark:bg-white/10 hover:bg-black/20 dark:hover:bg-white/20 text-theme-text text-[9px] font-bold py-1 rounded transition-colors">Cancel</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <button onClick={handleSaveQuick} className="text-left px-3 py-1.5 text-[10px] font-bold text-theme-text hover:bg-black/5 dark:hover:bg-white/5 rounded transition-colors flex items-center gap-2">
                      <Save size={12} /> Quick Save
                    </button>
                    <button onClick={() => setIsNamingSave(true)} className="text-left px-3 py-1.5 text-[10px] font-bold text-theme-text hover:bg-black/5 dark:hover:bg-white/5 rounded transition-colors flex items-center gap-2">
                      <BookmarkPlus size={12} /> Save with Name...
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Center - Flags */}
      <div className="flex items-center justify-center w-full order-last mt-2 md:mt-0 md:w-auto md:order-none md:flex-1 md:min-w-0 z-0 relative px-0 md:px-2">
        {availableFlags.length > 0 && (
          <div className="relative flex items-center bg-black/5 dark:bg-white/5 p-1 rounded-lg border border-black/5 dark:border-white/5 w-full md:w-auto max-w-full overflow-hidden pointer-events-auto">
            {canScrollLeft && (
              <button
                onClick={() => handleScroll('left')}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-0.5 bg-gradient-to-r from-theme-base via-theme-base to-transparent text-theme-muted hover:text-theme-text transition-colors h-full flex items-center"
              >
                <ChevronLeft size={14} className="mr-2" />
              </button>
            )}

            <div
              ref={flagsContainerRef}
              onScroll={checkScroll}
              className="flex items-center gap-1.5 overflow-x-auto w-full [scrollbar-width:none] [&::-webkit-scrollbar]:hidden scroll-smooth"
            >
              {groupedFlags.basic.length > 0 && (
                <div className="flex items-center gap-1 shrink-0">
                  {renderFlagGroup(groupedFlags.basic)}
                </div>
              )}
              {groupedFlags.advance.length > 0 && (
                <>
                  {groupedFlags.basic.length > 0 && <div className="w-px h-3.5 bg-theme-border opacity-50 mx-0.5 shrink-0" />}
                  <div className="flex items-center gap-1 shrink-0">
                    {renderFlagGroup(groupedFlags.advance)}
                  </div>
                </>
              )}
              {groupedFlags.unique.length > 0 && (
                <>
                  {(groupedFlags.basic.length > 0 || groupedFlags.advance.length > 0) && <div className="w-px h-3.5 bg-theme-border opacity-50 mx-0.5 shrink-0" />}
                  <div className="flex items-center gap-1 shrink-0">
                    {renderFlagGroup(groupedFlags.unique)}
                  </div>
                </>
              )}
            </div>

            {canScrollRight && (
              <button
                onClick={() => handleScroll('right')}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 p-0.5 bg-gradient-to-l from-theme-base via-theme-base to-transparent text-theme-muted hover:text-theme-text transition-colors h-full flex items-center"
              >
                <ChevronRight size={14} className="ml-2" />
              </button>
            )}
          </div>
        )}
      </div>

      {/* Right - Rest of Actions */}
      <div className="flex items-center gap-2 justify-end ml-auto z-10 overflow-x-auto custom-scrollbar pb-0.5 md:pb-0 shrink-0">
        {(originalSelection.activeGroupIds.length > 0 || originalSelection.activeToken !== null || optimizedSelection.activeGroupIds.length > 0) && (
          <button className="shrink-0 text-xs font-mono bg-cyan-100 dark:bg-[#2A3130] text-cyan-700 dark:text-[#A7B5B3] px-2 py-1 rounded-sm border border-cyan-300 dark:border-[#3D4745] hover:bg-cyan-200 dark:hover:bg-[#343C3A] transition-colors" onClick={() => { originalSelection.handleClearSelection(); optimizedSelection.handleClearSelection(); }}>
             Clear Selections ✕
          </button>
        )}

        <div className="flex items-center gap-1.5 shrink-0">
          <button onClick={() => setCompatibilityReportOpen(true)} className="p-1.5 text-indigo-500 hover:bg-black/5 dark:hover:bg-white/5 rounded-md transition-colors border border-transparent hover:border-ide-border" title="Check Cross-Engine Compatibility">
            <Activity size={14} strokeWidth={2.5} />
          </button>

          <div className="w-px h-3.5 bg-ide-border mx-0.5" />

          <button onClick={handleShareClick} className="p-1.5 text-indigo-500 hover:bg-black/5 dark:hover:bg-white/5 rounded-md transition-colors border border-transparent hover:border-ide-border" title="Share">
            {copied ? <Check size={14} strokeWidth={2.5} /> : <Share2 size={14} strokeWidth={2.5} />}
          </button>

          {(activeEngine?.engine_examples?.length ?? 0) > 0 && <button onClick={handleLoadExample} className="p-1.5 text-amber-500 hover:bg-black/5 dark:hover:bg-white/5 rounded-md transition-colors border border-transparent hover:border-ide-border" title="Load Random Example"><Lightbulb size={14} strokeWidth={2.5} /></button>}
          <button onClick={handleClear} className="p-1.5 text-rose-600 hover:bg-rose-500/10 rounded-md transition-colors border border-transparent hover:border-rose-500/20" title="Clear Inputs"><Trash2 size={14} strokeWidth={2.5} /></button>
        </div>
      </div>
    </div>
  );
};
