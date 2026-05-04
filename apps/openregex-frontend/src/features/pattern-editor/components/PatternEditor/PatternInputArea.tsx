import React, { useRef, useMemo } from 'react';
import { useRegexStore } from '../../../../core/store/useRegexStore';
import { useSelectionStore } from '../../../../core/store/useSelectionStore';
import { buildRegexTree } from '../../utils/pattern.utils';
import { RegexViewerNode } from '../RegexViewerNode';
import { SHARED_TEXT_CLASSES } from './constants';

interface PatternInputAreaProps {
  cheatSheetMap: Map<string, string>;
  cheatSheetItems: any[];
}

export const PatternInputArea: React.FC<PatternInputAreaProps> = ({ cheatSheetMap, cheatSheetItems }) => {
  const regex = useRegexStore(state => state.regex);
  const setRegex = useRegexStore(state => state.setRegex);
  const originalSelection = useSelectionStore();

  const patternBackdropRef = useRef<HTMLTextAreaElement>(null);
  const patternBackdropDivRef = useRef<HTMLDivElement>(null);
  const astTree = useMemo(() => regex ? buildRegexTree(regex) : null, [regex]);

  const handleEditorClick = (e: React.MouseEvent<HTMLTextAreaElement>) => {
    const cursorStart = e.currentTarget.selectionStart;
    const cursorEnd = e.currentTarget.selectionEnd;
    if (cursorStart !== cursorEnd) { originalSelection.handleSelection(null, null, null, false, null, null, 'pattern'); return; }

    if (!patternBackdropRef.current || !patternBackdropDivRef.current) return;
    try {
      patternBackdropRef.current.style.pointerEvents = 'none';
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
          originalSelection.handleSelection(null, groupId, null, e.ctrlKey || e.metaKey, token, tokenIndex, 'pattern');
          return;
        }
      }
      originalSelection.handleSelection(null, null, null, false, null, null, 'pattern');
    } finally {
      patternBackdropRef.current.style.pointerEvents = 'auto';
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!patternBackdropDivRef.current || !patternBackdropRef.current) return;
    try {
      patternBackdropRef.current.style.pointerEvents = 'none';
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
      originalSelection.handleHover(null, groupId, null, token, tokenIndex);
    } finally {
      patternBackdropRef.current.style.pointerEvents = 'auto';
    }
  };

  const handleScroll = (e: React.UIEvent<HTMLTextAreaElement>) => {
    if (patternBackdropDivRef.current) {
      patternBackdropDivRef.current.scrollTop = e.currentTarget.scrollTop;
      patternBackdropDivRef.current.scrollLeft = e.currentTarget.scrollLeft;
    }
  };

  return (
    <div className="relative flex-1 min-h-[80px]" onMouseLeave={() => originalSelection.handleHover(null, null, null, null)} onMouseMove={handleMouseMove}>
      <div ref={patternBackdropDivRef} className={`absolute inset-0 overflow-y-auto z-0 pointer-events-auto text-ide-dim ${SHARED_TEXT_CLASSES}`}>
        {astTree ? <RegexViewerNode node={astTree} activeGroupIds={originalSelection.activeGroupIds} hoveredGroupId={originalSelection.hoveredGroupId} hoveredToken={originalSelection.hoveredToken} hoveredTokenIndex={originalSelection.hoveredTokenIndex} activeToken={originalSelection.activeToken} activeTokenIndex={originalSelection.activeTokenIndex} cheatSheetMap={cheatSheetMap} cheatSheetItems={cheatSheetItems} /> : <span className="text-transparent">Placeholder text</span>}
        {regex.endsWith('\n') && <br />}
      </div>
      <textarea ref={patternBackdropRef} value={regex} onChange={e => setRegex(e.target.value.replace(/\r/g, ''))} onClick={handleEditorClick} onScroll={handleScroll} placeholder="e.g. (?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})" spellCheck={false} className={`absolute inset-0 w-full h-full bg-transparent text-transparent caret-theme-text resize-none placeholder-ide-dim overflow-y-auto z-10 pointer-events-auto pb-16 ${SHARED_TEXT_CLASSES}`} />
    </div>
  );
};