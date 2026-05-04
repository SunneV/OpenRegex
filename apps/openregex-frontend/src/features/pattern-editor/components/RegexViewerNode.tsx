import React, { useRef } from 'react';
import { ASTNode } from '../../../core/types';
import { getGroupColorClasses } from '../../../shared/utils/colors';
import { isCheatSheetItemHovered } from '../../../shared/utils/hoverMatcher';
import { useRegexStore } from '../../../core/store/useRegexStore';
import { RegexTooltip } from './RegexTooltip';

interface RegexViewerNodeProps {
  node: ASTNode;
  activeGroupIds: number[];
  hoveredGroupId: number | null;
  hoveredToken: string | null;
  hoveredTokenIndex: number | null;
  activeToken: string | null;
  activeTokenIndex: number | null;
  isBoundary?: boolean;
  forceBoundaryHighlight?: boolean;
  forceBoundaryActive?: boolean;
  boundaryClasses?: string;
  parentGroupId?: number;
  nonCapturingPrefix?: string;
  openingToken?: string;
  cheatSheetItems?: string[];
}

interface RegexTextTokenProps {
  node: ASTNode;
  t: string;
  tokenStr: string;
  isToken: boolean;
  isBoundary?: boolean;
  parentGroupId?: number;
  finalClassName: string;
  tooltipToken: string;
  tooltipDescription: string;
  isDirectlyHovered: boolean;
}

const RegexTextToken: React.FC<RegexTextTokenProps> = ({
  node, t, tokenStr, isToken, isBoundary, parentGroupId, finalClassName, tooltipToken, tooltipDescription, isDirectlyHovered
}) => {
  const spanRef = useRef<HTMLSpanElement>(null);

  return (
    <>
      <span
        ref={spanRef}
        data-token={isToken ? tokenStr : undefined}
        data-token-index={isToken ? node.startIndex : undefined}
        data-group-id={isBoundary && parentGroupId !== undefined ? parentGroupId : undefined}
        className={finalClassName.trim().replace(/\s+/g, ' ')}
      >
        {t}
      </span>
      <RegexTooltip
        targetRef={spanRef}
        token={tooltipToken}
        description={tooltipDescription}
        isVisible={isDirectlyHovered}
      />
    </>
  );
};

const getSymbolClass = (t: string): string => {
  if (t.startsWith('\\')) {
    if (/^\\[bBAZzGMmK]/.test(t) || t.startsWith('\\b{')) return "text-sky-600/70 dark:text-sky-200/40";
    if (/^\\[wWdDsShHvVXpP]/.test(t)) return "text-orange-600/70 dark:text-orange-200/40";
    if (/^\\[xUu0-9]/.test(t) || /^\\[afnrt]/.test(t)) return "text-emerald-600/70 dark:text-emerald-200/40";
    if (/^\\[1-9]/.test(t) || /^\\[kg]/.test(t)) return "text-indigo-600/70 dark:text-indigo-200/40";
    return "text-orange-600/70 dark:text-orange-200/40";
  }
  if (t.startsWith('(*')) return "text-rose-600/70 dark:text-rose-200/40";
  if (t.startsWith('[') || t.startsWith('[^')) return "text-amber-600/70 dark:text-amber-200/40";
  if (/^[*+?][?+]?$/.test(t) || t.startsWith('{')) return "text-purple-600/70 dark:text-purple-200/40";
  if (t === '^' || t === '$' || t === '|') return "text-sky-600/70 dark:text-sky-200/40";
  if (t === '.') return "text-rose-600/70 dark:text-rose-200/40";
  return "";
};

export const RegexViewerNode: React.FC<RegexViewerNodeProps> = ({
  node, activeGroupIds, hoveredGroupId, hoveredToken, hoveredTokenIndex, activeToken, activeTokenIndex, isBoundary, forceBoundaryHighlight, forceBoundaryActive, boundaryClasses, parentGroupId, nonCapturingPrefix, openingToken, cheatSheetItems
}) => {
  if (node.type === 'text') {
    const t = node.text || "";

    const isSupported = (tokenToTest: string) => {
      if (!cheatSheetItems || cheatSheetItems.length === 0) return true;
      return cheatSheetItems.some(item => isCheatSheetItemHovered(tokenToTest, item));
    };

    let symbolClass = "";
    let tokenStr = t;

    if (isBoundary) {
      if (t.startsWith('(?') || t === '(') {
        if (parentGroupId === undefined) symbolClass = "text-sky-600/70 dark:text-sky-200/40 cursor-help";
        tokenStr = nonCapturingPrefix || openingToken || '(';
      } else if (t === ')') {
        if (parentGroupId === undefined) symbolClass = "text-sky-600/70 dark:text-sky-200/40 cursor-help";
        tokenStr = nonCapturingPrefix || openingToken || '(';
      }
    } else {
      symbolClass = getSymbolClass(t);
    }

    const supported = isSupported(tokenStr) || isSupported(t);

    if (!supported) {
      symbolClass = "";
    }

    const isToken = Boolean((symbolClass !== "" || isBoundary) && supported);

    let tooltipDescription = "";
    let tooltipToken = "";

    if (isToken) {
      const { engines, selectedEngineId } = useRegexStore.getState();
      const activeEngine = engines.find(e => e.engine_id === selectedEngineId);
      const allItems = activeEngine?.engine_cheat_sheet?.flatMap(cat => cat.items) || [];
      const match = allItems.find(item => isCheatSheetItemHovered(tokenStr, item.character) || isCheatSheetItemHovered(t, item.character));

      if (match) {
        tooltipToken = match.character;
        tooltipDescription = match.description;
      }
    }

    const isHovered = !!forceBoundaryHighlight || (isToken && (
      hoveredTokenIndex !== null
        ? hoveredTokenIndex === node.startIndex
        : (hoveredToken === tokenStr || hoveredToken === t ||
          (!!hoveredToken && isCheatSheetItemHovered(tokenStr, hoveredToken)) ||
          (!!hoveredToken && isCheatSheetItemHovered(t, hoveredToken)))
    ));

    const isActive = !!forceBoundaryActive || (isToken && (
      activeTokenIndex !== null
        ? activeTokenIndex === node.startIndex
        : (activeToken === tokenStr || activeToken === t ||
          (!!activeToken && isCheatSheetItemHovered(tokenStr, activeToken)) ||
          (!!activeToken && isCheatSheetItemHovered(t, activeToken)))
    ));

    const isHighlighted = isHovered || isActive;

    const isDirectlyHovered = Boolean(isToken && hoveredTokenIndex !== null && hoveredTokenIndex === node.startIndex);

    const activeTokenClass = isHighlighted
      ? "rounded-sm z-20 bg-theme-primary/20 !text-theme-primary ring-1 ring-theme-primary/40 drop-shadow-sm dark:bg-theme-primary/15 dark:!text-theme-primary dark:ring-1 dark:ring-theme-primary/40 dark:drop-shadow-none"
      : (!isBoundary && isToken ? "cursor-pointer" : "");

    const finalClassName = (isBoundary && parentGroupId !== undefined)
      ? `relative z-10 transition-all duration-150 rounded-sm ${isToken ? 'cursor-pointer' : ''} ${boundaryClasses || ''} ${activeTokenClass}`
      : `${symbolClass || "text-theme-text/60 dark:text-white/50"} ${activeTokenClass} transition-all duration-150 relative ${isToken ? 'cursor-pointer' : ''}`;

    return (
      <RegexTextToken
        node={node}
        t={t}
        tokenStr={tokenStr}
        isToken={isToken}
        isBoundary={isBoundary}
        parentGroupId={parentGroupId}
        finalClassName={finalClassName}
        tooltipToken={tooltipToken}
        tooltipDescription={tooltipDescription}
        isDirectlyHovered={isDirectlyHovered}
      />
    );
  }

  if (node.type === 'group') {
    const isGroupActive = node.id !== undefined && activeGroupIds.includes(node.id);
    const isPatternHovered = node.id !== undefined && hoveredGroupId === node.id;
    const isEffectivelyActive = isGroupActive || isPatternHovered;
    const isDimmed = activeGroupIds.length > 0 && !isGroupActive;

    const classes = node.isCapturing ? getGroupColorClasses(node.id!, isEffectivelyActive, isDimmed) : '';
    let zIndex = isEffectivelyActive ? 'z-40' : (node.isCapturing ? 'z-0 hover:z-20' : 'z-0');

    const combinedBoundaryClasses = node.isCapturing ? `${classes} ${zIndex}`.trim() : '';

    let opToken = "(";
    let nonCapPrefix = undefined;

    if (node.children && node.children.length > 0) {
        let prefix = "";
        for (const child of node.children) {
            if (child.type === 'text') {
                prefix += child.text;
                if (prefix.length >= 10 || prefix.includes('>') || prefix.includes("'")) break;
            } else {
                break;
            }
        }

        if (node.isCapturing) {
            const match = prefix.match(/^\(\?(?:P?<[^>]+>|<[^>]+>|'[^']+')/);
            if (match) opToken = match[0];
            else opToken = "(";
        } else {
            const match = prefix.match(/^\(\?(?:<=|<!|[=!:>|~]|[a-zA-Z-]+:?|\([^\)]+\))/);
            if (match) nonCapPrefix = match[0];
            else nonCapPrefix = node.children[0]?.text;
        }
    }

    let isGroupBoundaryHovered = false;
    let isGroupBoundaryActive = false;

    if (node.children && node.children.length > 0) {
        const firstChild = node.children[0];
        const lastChild = node.children[node.children.length - 1];

        if (hoveredTokenIndex !== null && (hoveredTokenIndex === firstChild.startIndex || hoveredTokenIndex === lastChild.startIndex)) {
            isGroupBoundaryHovered = true;
        }
        if (activeTokenIndex !== null && (activeTokenIndex === firstChild.startIndex || activeTokenIndex === lastChild.startIndex)) {
            isGroupBoundaryActive = true;
        }
    }

    return (
      <span className={`relative ${zIndex}`}>
        {node.children?.map((c, i) => {
          const isChildBoundary = i === 0 || i === (node.children!.length - 1);
          return (
            <RegexViewerNode
              key={i}
              node={c}
              activeGroupIds={activeGroupIds}
              hoveredGroupId={hoveredGroupId}
              hoveredToken={hoveredToken}
              hoveredTokenIndex={hoveredTokenIndex}
              activeToken={activeToken}
              activeTokenIndex={activeTokenIndex}
              isBoundary={isChildBoundary}
              forceBoundaryHighlight={isChildBoundary && isGroupBoundaryHovered}
              forceBoundaryActive={isChildBoundary && isGroupBoundaryActive}
              boundaryClasses={combinedBoundaryClasses}
              parentGroupId={node.isCapturing ? node.id : undefined}
              nonCapturingPrefix={nonCapPrefix}
              openingToken={node.isCapturing ? opToken : undefined}
              cheatSheetItems={cheatSheetItems}
            />
          );
        })}
      </span>
    );
  }

  if (node.type === 'root') {
    return (
      <>
        {node.children?.map((c, i) => (
          <RegexViewerNode
             key={i}
             node={c}
             activeGroupIds={activeGroupIds}
             hoveredGroupId={hoveredGroupId}
             hoveredToken={hoveredToken}
             hoveredTokenIndex={hoveredTokenIndex}
             activeToken={activeToken}
             activeTokenIndex={activeTokenIndex}
             cheatSheetItems={cheatSheetItems}
          />
        ))}
      </>
    );
  }

  return null;
};