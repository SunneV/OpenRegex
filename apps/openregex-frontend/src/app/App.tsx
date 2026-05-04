import { useState, useEffect, useRef } from 'react';
import { Header } from './layout/Header';
import { Footer } from './layout/Footer';
import { PatternEditor } from '../features/pattern-editor';
import { SubjectEditor } from '../features/subject-tester';
import { Inspector } from '../features/match-inspector';
import { CheatSheet } from '../features/cheat-sheet';
import { CompatibilityReport } from '../features/engine-selector';
import { PersonalPanel } from '../features/personal';
import { TermsModal } from '../features/terms';
import { AISidebar } from '../features/ai-assistant';
import { useRegexStore } from '../core/store/useRegexStore';
import { useSelectionStore } from '../core/store/useSelectionStore';
import { useUIStore } from '../core/store/useUIStore';
import { useLLMStore } from '../core/store/useLLMStore';
import { useStorageStore } from '../core/store/useStorageStore';
import { getUrlState, updateUrlState } from '../shared/utils/link';
import { mapPythonIndicesToJs } from '../shared/utils/subject.utils';
import pkg from '../../package.json';

const LEGACY_ENGINE_MAP: Record<string, string> = {
  'Python - re': 'python_re',
  'Python - regex': 'python_regex',
  'C++': 'cpp_std',
  'Java': 'jvm_standard',
  'JavaScript': 'v8_standard'
};

export default function App() {
  const [systemInfo, setSystemInfo] = useState({
    backendVersion: 'Unknown',
    frontendVersion: pkg.version,
    releaseDate: 'Unknown'
  });

  const [patternRatio, setPatternRatio] = useState(0.42); // 42% default split
  const [cheatSheetHeight, setCheatSheetHeight] = useState(30);
  const [isDraggingCS, setIsDraggingCS] = useState(false);

  const leftColumnRef = useRef<HTMLDivElement>(null);

  const isCheatSheetOpen = useUIStore(state => state.isCheatSheetOpen);

  const isAiSidebarOpen = useLLMStore(state => state.isAiSidebarOpen);
  const setAiSidebarOpen = useLLMStore(state => state.setAiSidebarOpen);
  const isAvailable = useLLMStore(state => state.isAvailable);

  const setWorkers = useRegexStore(state => state.setWorkers);
  const setLoading = useRegexStore(state => state.setLoading);
  const setSelectedEngineId = useRegexStore(state => state.setSelectedEngineId);
  const setRegex = useRegexStore(state => state.setRegex);
  const setText = useRegexStore(state => state.setText);
  const loading = useRegexStore(state => state.loading);
  const selectedEngineId = useRegexStore(state => state.selectedEngineId);
  const regex = useRegexStore(state => state.regex);
  const text = useRegexStore(state => state.text);
  const activeFlags = useRegexStore(state => state.activeFlags);
  const setMatches = useRegexStore(state => state.setMatches);
  const setError = useRegexStore(state => state.setError);
  const setExecTime = useRegexStore(state => state.setExecTime);

  useEffect(() => {
    fetch('/api/info', {
      headers: { 'X-Frontend-Version': pkg.version }
    })
      .then(res => res.json())
      .then(data => {
        setSystemInfo({
          backendVersion: data.backend_version || data.version || 'Unknown',
          frontendVersion: pkg.version,
          releaseDate: data.release_date || 'Unknown'
        });

      })
      .catch(() => {
        setSystemInfo({ backendVersion: 'Unknown', frontendVersion: pkg.version, releaseDate: 'Unknown' });
      });

    fetch('/api/engines')
      .then(res => res.json())
      .then(async (workerData) => {
        setWorkers(workerData);
        const flatEngines = workerData.flatMap((w: any) => w.engines);

        const urlState = await getUrlState();
        if (urlState) {

          let resolvedEngineId = '';

          if (urlState.engine_id) {
            resolvedEngineId = urlState.engine_id;
          } else if (urlState.e) {
            const exactMatch = flatEngines.find((e: any) => e.engine_id === urlState.e || e.engine_label === urlState.e);
            if (exactMatch) {
              resolvedEngineId = exactMatch.engine_id;
            } else {
              const normalizedLegacy = LEGACY_ENGINE_MAP[urlState.e] || urlState.e.toLowerCase();
              const prefixMatch = flatEngines.find((e: any) =>
                e.engine_id.startsWith(`${normalizedLegacy}_`) ||
                e.engine_id.startsWith(normalizedLegacy) ||
                e.engine_label.toLowerCase().includes(normalizedLegacy)
              );
              resolvedEngineId = prefixMatch ? prefixMatch.engine_id : (flatEngines.length > 0 ? flatEngines[0].engine_id : '');
            }
          } else {
            resolvedEngineId = flatEngines.length > 0 ? flatEngines[0].engine_id : '';
          }

          setSelectedEngineId(resolvedEngineId);
          setRegex((urlState.regex || urlState.r || '').replace(/\r/g, ''));
          setText((urlState.text || urlState.t || '').replace(/\r/g, ''));
          useRegexStore.setState({ activeFlags: urlState.flags || [] });
        } else if (flatEngines.length > 0) {
          const currentId = useRegexStore.getState().selectedEngineId;
          const isValid = flatEngines.some((e: any) => e.engine_id === currentId);
          if (!isValid) {
            setSelectedEngineId(flatEngines[0].engine_id);
          } else {
            setSelectedEngineId(currentId);
          }
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch engines", err);
        setLoading(false);
      });
  }, [setWorkers, setLoading, setSelectedEngineId, setRegex, setText]);

  useEffect(() => {
    if (!loading) {
      updateUrlState({ engine_id: selectedEngineId, regex, text, flags: activeFlags });
    }

    if (!regex || !text || !selectedEngineId) {
      setMatches([]);
      setError(null);
      setExecTime(null);
      return;
    }

    const timer = setTimeout(() => {
      fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine_id: selectedEngineId, regex, text, flags: activeFlags })
      })
      .then(async res => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Server error');
        return data;
      })
      .then(data => {
        if (data.success) {

          const normalizedMatches = mapPythonIndicesToJs(text, data.matches);
          setMatches(normalizedMatches);
          setError(null);

          useStorageStore.getState().pushHistory({
            engineId: selectedEngineId,
            regex,
            text,
            flags: activeFlags
          });

        } else {
          setMatches([]);
          setError(data.error || 'Unknown execution error');
        }
        setExecTime(data.execution_time_ms);

        const { activeGroupIds, handleClearSelection } = useSelectionStore.getState();
        if (activeGroupIds.length > 0 && data.success) {
           const maxGroup = data.matches.reduce((max: number, m: any) =>
             Math.max(max, ...m.groups.map((g: any) => g.group_id)), 0);
           if (activeGroupIds.some(id => id > maxGroup)) handleClearSelection();
        }
      })
      .catch(err => {
        setError(err.message);
        setMatches([]);
        setExecTime(null);
      });
    }, 300);

    return () => clearTimeout(timer);
  }, [regex, text, selectedEngineId, activeFlags, loading, setMatches, setError, setExecTime]);

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'l') {
        e.preventDefault();
        if (isAvailable) {
          setAiSidebarOpen(!isAiSidebarOpen);
        }
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, [isAvailable, isAiSidebarOpen, setAiSidebarOpen]);

  const startDrag = (e: React.PointerEvent) => {
    e.preventDefault();
    const startY = e.clientY;
    const startRatio = patternRatio;
    const containerHeight = leftColumnRef.current?.getBoundingClientRect().height || 1;

    const onMove = (moveEvent: PointerEvent) => {
      const deltaY = moveEvent.clientY - startY;
      const deltaRatio = deltaY / containerHeight;
      let newRatio = startRatio + deltaRatio;
      newRatio = Math.max(0.15, Math.min(newRatio, 0.85)); // Constraint limits
      setPatternRatio(newRatio);
    };

    const onUp = () => {
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', onUp);
    };

    document.addEventListener('pointermove', onMove);
    document.addEventListener('pointerup', onUp);
  };

  const startCheatSheetDrag = (e: React.PointerEvent) => {
    e.preventDefault();
    setIsDraggingCS(true);
    const startY = e.clientY;
    const startHeight = cheatSheetHeight;
    const windowHeight = window.innerHeight || 1;

    const onMove = (moveEvent: PointerEvent) => {
      const deltaY = moveEvent.clientY - startY;
      const deltaVh = (deltaY / windowHeight) * 100;
      let newHeight = startHeight + deltaVh;
      newHeight = Math.max(10, Math.min(newHeight, 85)); // Constraint limits
      setCheatSheetHeight(newHeight);
    };

    const onUp = () => {
      setIsDraggingCS(false);
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', onUp);
    };

    document.addEventListener('pointermove', onMove);
    document.addEventListener('pointerup', onUp);
  };

  return (
    <div className="flex flex-col min-h-screen lg:h-screen w-full relative text-theme-text bg-theme-base lg:overflow-hidden">
      <div className="bg-orbs fixed inset-0 pointer-events-none">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="relative z-10 flex flex-col h-full w-full flex-1">
        {/* Header - Fixed Top */}
        <div className="px-2 md:px-3 pt-2 md:pt-3 shrink-0 w-full relative z-30">
          <Header />
        </div>

        {/* Workspace Area: Cheat Sheet + Main Workspaces */}
        <div className="flex-1 flex flex-col px-2 md:px-3 py-2 md:py-3 overflow-visible lg:overflow-hidden relative min-h-0">

          {/* Cheat Sheet & Resizer */}
          <div
            className={`${isDraggingCS ? '' : 'transition-all duration-300'} ease-in-out overflow-hidden z-20 shrink-0 flex flex-col`}
            style={{
              height: isCheatSheetOpen ? `${cheatSheetHeight}vh` : '0px',
              opacity: isCheatSheetOpen ? 1 : 0
            }}
          >
            <div className="flex-1 min-h-0 w-full">
              <CheatSheet />
            </div>
            {isCheatSheetOpen && (
              <div
                className="h-3 w-full cursor-row-resize flex items-center justify-center group shrink-0"
                onPointerDown={startCheatSheetDrag}
                title="Drag to resize Cheat Sheet"
              >
                <div className="w-12 h-1 rounded-full bg-theme-border group-hover:bg-theme-primary/50 transition-colors" />
              </div>
            )}
          </div>

          {/* Main Workspace - Native scroll on mobile, flex on desktop */}
          <main className="flex-1 flex flex-col lg:flex-row gap-3 relative min-h-0">

            <div ref={leftColumnRef} className="flex flex-col w-full lg:w-7/12 h-[65vh] min-h-[500px] lg:h-full lg:min-h-0 shrink-0 lg:shrink relative">
              {/* Pattern Editor */}
              <div
                className="flex flex-col rounded-[16px] md:rounded-[20px] overflow-hidden glass-panel relative border border-ide-border focus-within:ring-1 focus-within:ring-theme-primary transition-shadow lg:min-h-0 shrink-0"
                style={{ flexBasis: `calc(${patternRatio * 100}% - 6px)`, minHeight: '150px' }}
              >
                <PatternEditor />
              </div>

              {/* Draggable Resizer (Tight spacing) */}
              <div
                className="h-3 w-full cursor-row-resize flex items-center justify-center group shrink-0"
                onPointerDown={startDrag}
                title="Drag to resize"
              >
                <div className="w-12 h-1 rounded-full bg-theme-border group-hover:bg-theme-primary/50 transition-colors" />
              </div>

              {/* Subject Editor */}
              <div
                className="flex flex-col rounded-[16px] md:rounded-[20px] overflow-hidden glass-panel relative border border-ide-border focus-within:ring-1 focus-within:ring-theme-primary transition-shadow lg:min-h-0 shrink-0"
                style={{ flexBasis: `calc(${(1 - patternRatio) * 100}% - 6px)`, minHeight: '200px' }}
              >
                <SubjectEditor />
              </div>
            </div>

            {/* Inspector Panel */}
            <div className="w-full min-h-[450px] lg:min-h-0 lg:h-full glass-panel rounded-[16px] md:rounded-[20px] overflow-hidden flex flex-col relative shadow-lg shrink-0 lg:shrink lg:w-5/12">
              <Inspector />
            </div>

            {/* AI Sidebar */}
            {isAiSidebarOpen && isAvailable && (
               <div className="fixed z-50 bottom-0 right-0 md:bottom-[80px] md:right-[40px] w-full h-[85dvh] md:w-[420px] md:h-[calc(100vh-120px)] md:max-h-[750px] glass-panel rounded-t-[20px] md:rounded-[20px] overflow-hidden flex flex-col shadow-2xl shadow-purple-500/20 border-t border-x md:border border-purple-500/40 animate-in slide-in-from-bottom-8 fade-in bg-theme-base/95 backdrop-blur-xl">
                 <AISidebar onClose={() => setAiSidebarOpen(false)} />
               </div>
            )}
          </main>
        </div>

        {/* Footer - Sits naturally at the bottom of the document on mobile */}
        <div className="px-2 md:px-3 pb-2 md:pb-3 shrink-0 flex items-center w-full z-40 mt-auto">
          <div className="w-full">
            <Footer
              frontendVersion={systemInfo.frontendVersion}
              backendVersion={systemInfo.backendVersion}
              backendReleaseDate={systemInfo.releaseDate}
            />
          </div>
        </div>
      </div>

      <CompatibilityReport />
      <PersonalPanel />
      <TermsModal />
    </div>
  );
}