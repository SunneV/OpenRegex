import React, { useMemo } from 'react';
import { useRegexStore } from '../../../../core/store/useRegexStore';
import { PatternEditorHeader } from './PatternEditorHeader';
import { PatternInputArea } from './PatternInputArea';
import { OptimizedPatternSplitView } from './OptimizedPatternSplitView';
import { FloatingAIActions } from './FloatingAIActions';
import { RegexTooltip } from '../RegexTooltip';

export const PatternEditor: React.FC = () => {
  const engines = useRegexStore(state => state.engines);
  const selectedEngineId = useRegexStore(state => state.selectedEngineId);

  const activeEngine = engines.find(e => e.engine_id === selectedEngineId);

  const cheatSheetItems = useMemo(() => {
    if (!activeEngine?.engine_cheat_sheet) return [];
    return activeEngine.engine_cheat_sheet.flatMap(cat => cat.items);
  }, [activeEngine]);

  const cheatSheetMap = useMemo(() => {
    const map = new Map<string, string>();
    cheatSheetItems.forEach(item => {
      map.set(item.character, item.description);
    });
    return map;
  }, [cheatSheetItems]);

  return (
    <div className="flex flex-col h-full bg-ide-panel border border-ide-border shadow-sm rounded-sm focus-within:ring-1 focus-within:ring-theme-primary transition-all overflow-hidden relative">
      <PatternEditorHeader />

      <div className="flex-1 flex flex-col min-h-0 bg-transparent">
        <PatternInputArea cheatSheetMap={cheatSheetMap} cheatSheetItems={cheatSheetItems} />
        <OptimizedPatternSplitView cheatSheetMap={cheatSheetMap} cheatSheetItems={cheatSheetItems} />
      </div>

      <FloatingAIActions />
      <RegexTooltip cheatSheetMap={cheatSheetMap} cheatSheetItems={cheatSheetItems} />
    </div>
  );
};