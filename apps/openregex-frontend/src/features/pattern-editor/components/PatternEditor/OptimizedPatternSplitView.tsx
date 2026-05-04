import React, { useRef, useMemo } from 'react';
import { Check, X } from 'lucide-react';
import { useRegexStore } from '../../../../core/store/useRegexStore';
import { useOptimizedSelectionStore } from '../../../../core/store/useOptimizedSelectionStore';
import { useLLMStore } from '../../../../core/store/useLLMStore';
import { buildRegexTree } from '../../utils/pattern.utils';
import { RegexViewerNode } from '../RegexViewerNode';
import { SHARED_TEXT_CLASSES } from './constants';

interface OptimizedPatternSplitViewProps {
  cheatSheetMap: Map<string, string>;
  cheatSheetItems: any[];
}

export const OptimizedPatternSplitView: React.FC<OptimizedPatternSplitViewProps> = ({ cheatSheetMap, cheatSheetItems }) => {
  const setRegex = useRegexStore(state => state.setRegex);
  const setActiveFlags = useRegexStore(state => state.setActiveFlags);
  const optimizedSelection = useOptimizedSelectionStore();
  const optimizationProposal = useLLMStore(state => state.optimizationProposal);
  const setOptimizationProposal = useLLMStore(state => state.setOptimizationProposal);

  const optPatternDivRef = useRef<HTMLDivElement>(null);
  const optimizedRegex = optimizationProposal?.optimizedRegex || '';
  const optAstTree = useMemo(() => optimizedRegex ? buildRegexTree(optimizedRegex) : null, [optimizedRegex]);

  if (!optimizationProposal) return null;

  const handleOptClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!optPatternDivRef.current) return;
    const el = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement;
    let token = null, tokenIndex = null, groupId = null;
    if (el) {
      const groupEl = el.closest('[data-group-id]');
      if (groupEl) groupId = Number(groupEl.getAttribute('data-group-id'));
      const tokenEl = el.closest('[data-token]');
      if (tokenEl) {
        token = tokenEl.getAttribute('data-token');
        const idxAttr = tokenEl.getAttribute('data-token-index');
        if (idxAttr) tokenIndex = Number(idxAttr);
      }
      if (groupId !== null || token !== null) {
        optimizedSelection.handleSelection(null, groupId, null, e.ctrlKey || e.metaKey, token, tokenIndex, 'pattern');
        return;
      }
    }
    optimizedSelection.handleSelection(null, null, null, false, null, null, 'pattern');
  };

  const handleOptMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!optPatternDivRef.current) return;
    const el = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement;
    let token = null, tokenIndex = null, groupId = null;
    if (el) {
      const tokenEl = el.closest('[data-token]');
      if (tokenEl) {
        token = tokenEl.getAttribute('data-token');
        const idxAttr = tokenEl.getAttribute('data-token-index');
        if (idxAttr) tokenIndex = Number(idxAttr);
      }
      const groupEl = el.closest('[data-group-id]');
      if (groupEl) groupId = Number(groupEl.getAttribute('data-group-id'));
    }
    optimizedSelection.handleHover(null, groupId, null, token, tokenIndex);
  };

  const handleAcceptOptimization = () => {
    if (optimizationProposal) {
      setRegex(optimizationProposal.optimizedRegex);
      if (optimizationProposal.flags) {
          setActiveFlags(optimizationProposal.flags);
      }
      setOptimizationProposal(null);
    }
  };

  const handleDiscardOptimization = () => {
    setOptimizationProposal(null);
  };

  return (
    <div className="flex flex-col flex-1 min-h-[80px] border-t border-purple-500/20 bg-purple-500/5 z-10 shadow-[0_-4px_15px_rgba(0,0,0,0.05)]">
      <div className="flex items-center justify-between px-3 py-1 bg-purple-500/10 border-b border-purple-500/10 shrink-0">
          <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider">Optimized Pattern</span>
              {optimizationProposal.flags && optimizationProposal.flags.length > 0 && (
                  <div className="flex gap-1">
                      {optimizationProposal.flags.map(f => (
                          <span key={f} className="text-[9px] font-mono font-bold bg-purple-500/20 text-purple-400 px-1 py-0.5 rounded shadow-sm border border-purple-500/30">/{f}</span>
                      ))}
                  </div>
              )}
          </div>
          <div className="flex gap-2">
              <button onClick={handleAcceptOptimization} className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/30 rounded transition-colors flex items-center gap-1"><Check size={10}/> Accept</button>
              <button onClick={handleDiscardOptimization} className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-600 dark:text-rose-400 hover:bg-rose-500/30 rounded transition-colors flex items-center gap-1"><X size={10}/> Discard</button>
          </div>
      </div>
      <div className="relative flex-1" onMouseMove={handleOptMouseMove} onClick={handleOptClick} onMouseLeave={() => optimizedSelection.handleHover(null, null, null, null)}>
        <div ref={optPatternDivRef} className={`absolute inset-0 overflow-y-auto z-0 pointer-events-auto text-purple-600 dark:text-purple-300 ${SHARED_TEXT_CLASSES}`}>
          {optAstTree ? <RegexViewerNode node={optAstTree} activeGroupIds={optimizedSelection.activeGroupIds} hoveredGroupId={optimizedSelection.hoveredGroupId} hoveredToken={optimizedSelection.hoveredToken} hoveredTokenIndex={optimizedSelection.hoveredTokenIndex} activeToken={optimizedSelection.activeToken} activeTokenIndex={optimizedSelection.activeTokenIndex} cheatSheetMap={cheatSheetMap} cheatSheetItems={cheatSheetItems} /> : null}
        </div>
      </div>
    </div>
  );
};