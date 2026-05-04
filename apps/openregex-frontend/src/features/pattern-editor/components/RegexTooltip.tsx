import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { useSelectionStore } from '../../../core/store/useSelectionStore';
import { useOptimizedSelectionStore } from '../../../core/store/useOptimizedSelectionStore';
import { isCheatSheetItemHovered } from '../../../shared/utils/hoverMatcher';

interface RegexTooltipProps {
  cheatSheetMap: Map<string, string>;
  cheatSheetItems: any[];
}

export const RegexTooltip: React.FC<RegexTooltipProps> = ({ cheatSheetMap, cheatSheetItems }) => {
  const hoveredTokenOrig = useSelectionStore(state => state.hoveredToken);
  const hoveredTokenIndexOrig = useSelectionStore(state => state.hoveredTokenIndex);
  const hoveredTokenOpt = useOptimizedSelectionStore(state => state.hoveredToken);
  const hoveredTokenIndexOpt = useOptimizedSelectionStore(state => state.hoveredTokenIndex);

  const [tooltipStyle, setTooltipStyle] = useState<React.CSSProperties>({
    opacity: 0,
    pointerEvents: 'none',
    position: 'fixed',
    top: 0,
    left: 0,
    zIndex: -1
  });

  const token = hoveredTokenOrig || hoveredTokenOpt;
  const index = hoveredTokenIndexOrig !== null ? hoveredTokenIndexOrig : hoveredTokenIndexOpt;
  const isOpt = hoveredTokenIndexOpt !== null;

  let description: string | undefined = undefined;
  let displayToken = token;

  if (token) {
    if (token === '|') {
      description = "x|y Alternation (x or y, prefer x)";
      displayToken = "|";
    } else if (cheatSheetMap.has(token)) {
      description = cheatSheetMap.get(token);
    } else if (cheatSheetItems) {
      const match = cheatSheetItems.find(item => isCheatSheetItemHovered(token, item.character));
      if (match) {
        description = match.description;
        displayToken = match.character;
      }
    }
  }

  const isVisible = !!(token && description && index !== null);

  useEffect(() => {
    if (!isVisible || typeof window === 'undefined') {
      setTooltipStyle(prev => ({ ...prev, opacity: 0, zIndex: -1 }));
      return;
    }

    const updatePos = () => {
      const elements = document.querySelectorAll(`[data-token-index="${index}"]`);
      let targetEl: Element | null = null;

      if (elements.length === 1) {
          targetEl = elements[0];
      } else if (elements.length > 1) {
          targetEl = Array.from(elements).find(el => {
              const isOptEl = !!el.closest('.border-purple-500\\/20') || !!el.closest('.bg-purple-500\\/5');
              return isOpt ? isOptEl : !isOptEl;
          }) || elements[0];
      }

      if (!targetEl) return;

      const targetRect = targetEl.getBoundingClientRect();
      const tooltipEl = document.getElementById('regex-tooltip-singleton');
      if (!tooltipEl) return;
      const tooltipRect = tooltipEl.getBoundingClientRect();

      let top = targetRect.top - tooltipRect.height - 8;
      let left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);

      if (top < 8) {
        top = targetRect.bottom + 8;
      }

      if (left < 8) {
        left = 8;
      } else if (left + tooltipRect.width > window.innerWidth - 8) {
        left = window.innerWidth - tooltipRect.width - 8;
      }

      setTooltipStyle({
        top: `${top}px`,
        left: `${left}px`,
        opacity: 1,
        transition: 'opacity 150ms ease-in-out',
        position: 'fixed',
        zIndex: 99999,
        pointerEvents: 'none'
      });
    };

    const timer = requestAnimationFrame(() => {
      updatePos();
    });

    window.addEventListener('resize', updatePos);
    document.addEventListener('scroll', updatePos, true);

    return () => {
      cancelAnimationFrame(timer);
      window.removeEventListener('resize', updatePos);
      document.removeEventListener('scroll', updatePos, true);
    };
  }, [isVisible, index, isOpt]);

  if (!isVisible || !description || typeof document === 'undefined') return null;

  return createPortal(
    <div
      id="regex-tooltip-singleton"
      style={tooltipStyle}
      className="flex items-stretch bg-white/30 dark:bg-[#121216]/40 backdrop-blur-xl border border-white/50 dark:border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.15)] rounded-lg overflow-hidden w-max max-w-[320px]"
    >
      <span className="flex items-center justify-center bg-white/40 dark:bg-black/30 text-theme-primary font-mono font-black px-3 py-2 border-r border-white/40 dark:border-white/5 text-[12px] shrink-0 whitespace-nowrap drop-shadow-sm">
        {displayToken}
      </span>
      <span className="flex items-center text-theme-text px-3 py-2 text-[11.5px] font-medium leading-relaxed whitespace-normal text-left drop-shadow-sm">
        {description}
      </span>
    </div>,
    document.body
  );
};