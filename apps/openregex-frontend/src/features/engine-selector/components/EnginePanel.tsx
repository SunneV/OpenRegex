import React, { useMemo, useState, useRef, useEffect } from 'react';
import { ChevronDown, Terminal, Book, Check, Info } from 'lucide-react';
import { EngineInfo } from '../../../core/types';
import { useRegexStore } from '../../../core/store/useRegexStore';
import { getWorkerSchemaVersion, isWorkerSchemaSupported, SUPPORTED_WORKER_SCHEMA_VERSION } from '../../../core/schema';

const PythonIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path fill="#387EB8" d="M12.012 1.933c-4.805 0-4.57 2.083-4.57 2.083v2.213h4.63v.654H5.21S2 6.55 2 11.53c0 4.978 2.768 4.793 2.768 4.793h2.174v-3.11c0-1.892 1.57-3.461 3.46-3.461h3.415s1.616-.073 1.616-1.637V4.08s.163-2.147-3.42-2.147zm-1.874 1.517a.91.91 0 0 1 .91.91.91.91 0 0 1-.91.91.91.91 0 0 1-.91-.91.91.91 0 0 1 .91-.91z"/>
    <path fill="#FFE052" d="M11.988 22.067c4.805 0 4.57-2.083 4.57-2.083v-2.213h-4.63v-.654h6.862s3.21.332 3.21-4.648c0-4.978-2.768-4.793-2.768-4.793h-2.174v3.11c0 1.892-1.57 3.461-3.46 3.461h-3.415s-1.616.073-1.616 1.637v4.032s-.163 2.147 3.42 2.147zm1.874-1.517a.91.91 0 0 1-.91-.91.91.91 0 0 1 .91-.91.91.91 0 0 1 .91.91.91.91 0 0 1-.91.91z"/>
  </svg>
);

const JSIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <rect width="24" height="24" rx="2" fill="#F7DF1E"/>
    <path fill="#000" d="M12.42 16.94c0 1.45-1.07 2.5-3.05 2.5-1.74 0-2.82-.9-3.02-2.19l1.77-.52c.11.75.64 1.25 1.34 1.25.7 0 1.15-.35 1.15-.84 0-.61-.57-.86-1.56-1.22-1.42-.51-2.43-1.12-2.43-2.61 0-1.42 1.11-2.48 2.86-2.48 1.6 0 2.53.86 2.76 2.05l-1.72.5c-.14-.58-.58-.99-1.15-.99-.6 0-.96.34-.96.79 0 .54.51.78 1.48 1.14 1.46.54 2.53 1.14 2.53 2.62zm7.69 2.37c-.7 0-1.17-.42-1.17-1.1v-6.95h-1.9v7.1c0 1.7 1.07 2.62 2.8 2.62.24 0 .47-.02.68-.06l-.41-1.61z"/>
  </svg>
);

const PHPIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <ellipse cx="12" cy="12" rx="11" ry="7" fill="#777BB4"/>
    <text x="12" y="15.5" fill="#000" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="9" textAnchor="middle">php</text>
  </svg>
);

const GoIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <text x="12" y="16.5" fill="#00ADD8" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="14" fontStyle="italic" textAnchor="middle" letterSpacing="-1">GO</text>
  </svg>
);

const CppIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <polygon points="12,1 22,6 22,18 12,23 2,18 2,6" fill="#00599C"/>
    <text x="12" y="16" fill="#fff" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="10" textAnchor="middle">C++</text>
  </svg>
);

const CSharpIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <polygon points="12,1 22,6 22,18 12,23 2,18 2,6" fill="#239120"/>
    <text x="12" y="16" fill="#fff" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="11" textAnchor="middle">C#</text>
  </svg>
);

const CIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <polygon points="12,1 22,6 22,18 12,23 2,18 2,6" fill="#A8B9CC"/>
    <text x="12" y="16.5" fill="#fff" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="13" textAnchor="middle">C</text>
  </svg>
);

const JavaIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path fill="#5382A1" d="M16 13h-8v-2h8v2zm-8 2h6v-2h-6v2zm9-7v-2c0-1.1-.9-2-2-2h-7c-1.1 0-2 .9-2 2v9c0 1.66 1.34 3 3 3h5c1.66 0 3-1.34 3-3v-2h2c1.1 0 2-.9 2-2v-1c0-1.1-.9-2-2-2h-2zm-9-2h7v2h-7v-2zm9 5h-2v-2h2v2zm-2 3h-5c-.55 0-1-.45-1-1v-2h7v2c0 .55-.45 1-1 1z"/>
    <path fill="#F8981D" d="M11 2c-.55 0-1 .45-1 1v3c0 .55.45 1 1 1s1-.45 1-1v-3c0-.55-.45-1-1-1zm3 1c-.55 0-1 .45-1 1v3c0 .55.45 1 1 1s1-.45 1-1v-3c0-.55-.45-1-1-1zm-6 2c-.55 0-1 .45-1 1v3c0 .55.45 1 1 1s1-.45 1-1v-3c0-.55-.45-1-1-1z"/>
  </svg>
);

const RustIcon = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path fill="currentColor" opacity="0.9" d="M22.5 12c0 5.8-4.7 10.5-10.5 10.5S1.5 17.8 1.5 12 6.2 1.5 12 1.5 22.5 6.2 22.5 12zm-3 0c0-4.14-3.36-7.5-7.5-7.5S4.5 7.86 4.5 12s3.36 7.5 7.5 7.5 7.5-3.36 7.5-7.5z"/>
    <text x="12" y="16.5" fill="var(--theme-base, #fff)" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="12" textAnchor="middle">R</text>
  </svg>
);

const getLanguageIcon = (family: string, size = 14) => {
  const f = family.toLowerCase();
  if (f.includes('python')) return <PythonIcon size={size} />;
  if (f.includes('java') && !f.includes('script')) return <JavaIcon size={size} />;
  if (f.includes('javascript') || f.includes('node') || f.includes('v8')) return <JSIcon size={size} />;
  if (f.includes('c++') || f.includes('cpp')) return <CppIcon size={size} />;
  if (f.includes('c#') || f.includes('csharp') || f.includes('.net')) return <CSharpIcon size={size} />;
  if (f.includes('c') && !f.includes('++') && !f.includes('#')) return <CIcon size={size} />;
  if (f.includes('php')) return <PHPIcon size={size} />;
  if (f.includes('rust')) return <RustIcon size={size} />;
  if (f.includes('go')) return <GoIcon size={size} />;
  return <Terminal size={size} className="text-theme-muted" />;
};

export const EnginePanel: React.FC = () => {
  const { engines, workers, selectedEngineId, setSelectedEngineId, loading } = useRegexStore();
  const [isOpen, setIsOpen] = useState(false);
  const [isTriviaOpen, setIsTriviaOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triviaRef = useRef<HTMLDivElement>(null);

  const groupedEngines = useMemo(() => {
    const groups: Record<string, EngineInfo[]> = {};
    engines.forEach(engine => {
      const family = engine.engine_label.split(' ')[0];
      if (!groups[family]) groups[family] = [];
      groups[family].push(engine);
    });

    // Sort engines alphabetically within each family
    Object.values(groups).forEach(group => {
      group.sort((a, b) => a.engine_label.localeCompare(b.engine_label));
    });

    return groups;
  }, [engines]);

  const longestLabel = useMemo(() => {
    let longest = 'Select Engine...';
    engines.forEach(e => {
      if (e.engine_label.length > longest.length) longest = e.engine_label;
    });
    return longest;
  }, [engines]);

  const activeEngine = engines.find(e => e.engine_id === selectedEngineId);
  const activeWorker = workers.find(w => w.engines.some(e => e.engine_id === selectedEngineId));
  const activeFamily = activeEngine ? activeEngine.engine_label.split(' ')[0] : '';

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
      if (triviaRef.current && !triviaRef.current.contains(event.target as Node)) {
        setIsTriviaOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="flex flex-col justify-center gap-1.5 h-full shrink-0">
      <div className="flex items-center gap-2">
        <div className="relative" ref={dropdownRef}>
          <div
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center justify-between bg-black/10 dark:bg-black/40 border border-theme-border rounded-lg px-3 py-1.5 cursor-pointer hover:bg-black/20 dark:hover:bg-white/5 transition-all group shadow-inner"
          >
            <div className="flex items-center gap-2">
              <div className="opacity-90">{getLanguageIcon(activeFamily, 14)}</div>
              <div className="grid items-center">
                <span className="invisible col-start-1 row-start-1 text-[11px] font-mono font-bold select-none pointer-events-none whitespace-nowrap">
                  {longestLabel}
                </span>
                <span className="col-start-1 row-start-1 text-theme-text text-[11px] font-mono font-bold select-none">
                  {activeEngine?.engine_label || 'Select Engine...'}
                </span>
              </div>
            </div>
            <ChevronDown size={14} className={`text-theme-muted transition-transform duration-200 ml-2 shrink-0 ${isOpen ? 'rotate-180' : ''}`} />
          </div>

          {isOpen && (
            <div className="absolute top-full left-0 mt-1 w-[280px] sm:w-[480px] lg:w-[650px] bg-white/95 dark:bg-[#1a1a20]/95 backdrop-blur-md rounded-lg z-50 shadow-xl border border-black/10 dark:border-white/10 overflow-hidden p-2">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 max-h-[60vh] overflow-y-auto custom-scrollbar">
                {Object.entries(groupedEngines)
                  .sort(([familyA], [familyB]) => familyA.localeCompare(familyB))
                  .map(([family, familyEngines]) => (
                  <div key={family} className="flex flex-col gap-1 border border-black/5 dark:border-white/5 rounded-md p-1.5 bg-black/[0.02] dark:bg-white/[0.02]">
                    <div className="px-1 text-[10px] font-black text-theme-muted/80 uppercase tracking-widest select-none pb-1 mb-1 border-b border-black/5 dark:border-white/5 flex items-center gap-1.5">
                      {getLanguageIcon(family, 14)} {family}
                    </div>
                    <div className="flex flex-col gap-0.5">
                      {familyEngines.map((e) => (
                        <button
                          key={e.engine_id}
                          onClick={() => {
                            setSelectedEngineId(e.engine_id);
                            setIsOpen(false);
                          }}
                          className={`flex items-center justify-between w-full px-2 py-1.5 rounded-sm text-left text-[11px] font-mono transition-colors ${
                            selectedEngineId === e.engine_id
                              ? 'bg-theme-primary/10 text-theme-primary font-bold'
                              : 'text-theme-text/80 hover:text-theme-text hover:bg-black/5 dark:hover:bg-white/10'
                          }`}
                        >
                          <span className="truncate pr-2">{e.engine_label.replace(family + ' ', '')}</span>
                          {selectedEngineId === e.engine_id && <Check size={12} className="text-theme-primary opacity-80 shrink-0" />}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {activeEngine?.engine_docs?.cheat_sheet_url && (
          <a
            href={activeEngine.engine_docs.cheat_sheet_url}
            target="_blank"
            rel="noopener noreferrer"
            title="Documentation"
            className="flex items-center gap-1 text-[9px] font-bold transition-all px-2.5 py-1 rounded-md border uppercase tracking-wider bg-blue-500/5 border-blue-500/10 hover:border-blue-500/30 text-blue-600/80 dark:text-blue-400/80 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-500/10"
          >
            <Book size={12} /> DOCS
          </a>
        )}

        {activeEngine?.engine_docs?.trivia && activeEngine.engine_docs.trivia.length > 0 && (
          <div className="relative" ref={triviaRef}>
            <button
              onClick={() => setIsTriviaOpen(!isTriviaOpen)}
              title="Engine Trivia"
              className={`flex items-center justify-center transition-all p-1.5 rounded-md border ${
                isTriviaOpen
                  ? 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/30'
                  : 'bg-orange-500/5 border-orange-500/10 hover:border-orange-500/30 text-orange-600/80 dark:text-orange-400/80 hover:text-orange-600 dark:hover:text-orange-400 hover:bg-orange-500/10'
              }`}
            >
              <Info size={14} />
            </button>

            {isTriviaOpen && (
              <div className="absolute top-full left-0 md:left-auto md:right-0 mt-2 w-64 md:w-72 bg-white/95 dark:bg-[#1a1a20]/95 backdrop-blur-md rounded-lg p-3 z-50 shadow-xl border border-black/10 dark:border-white/10 overflow-hidden cursor-default">
                <h4 className="text-sm font-black text-theme-muted uppercase tracking-widest mb-2 border-b border-black/10 dark:border-white/10 pb-1">
                  Did you know?
                </h4>
                <ul className="flex flex-col gap-2 max-h-[40vh] overflow-y-auto custom-scrollbar pr-1">
                  {activeEngine.engine_docs.trivia.map((item, idx) => (
                    <li key={idx} className="text-[10.5px] font-mono text-theme-text/90 leading-tight flex items-start gap-1.5">
                      <span className="text-theme-primary mt-0.5 opacity-80 shrink-0 select-none">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center gap-3 text-[10px] font-mono text-theme-muted/80 tracking-tight pl-1">
        {loading && <div className="w-1.5 h-1.5 rounded-full bg-theme-primary animate-pulse shrink-0" />}
        <span
          className="flex items-center gap-1 cursor-help"
          title={activeWorker?.worker_release_date ? `Release: ${activeWorker.worker_release_date}` : 'Release: Unknown'}
        >
          <span className="font-sans font-black opacity-50 uppercase text-[8px]">Worker</span>
          <span className="text-theme-text font-bold">{activeWorker?.worker_version || '---'}</span>
        </span>
        <span className="flex items-center gap-1">
          <span className="font-sans font-black opacity-50 uppercase text-[8px]">Lib</span>
          <span className="text-theme-text font-bold">{activeEngine?.engine_regex_lib_version || '---'}</span>
        </span>
        {activeWorker && (
          <span
            className="flex items-center gap-1 cursor-help"
            title={
              isWorkerSchemaSupported(activeWorker.worker_schema_version)
                ? `Communication schema v${getWorkerSchemaVersion(activeWorker.worker_schema_version)}`
                : `Worker reports schema v${getWorkerSchemaVersion(activeWorker.worker_schema_version)}, frontend expects v${SUPPORTED_WORKER_SCHEMA_VERSION}. Results may be inconsistent — update this worker.`
            }
          >
            <span className="font-sans font-black opacity-50 uppercase text-[8px]">Schema</span>
            <span className={`font-bold ${isWorkerSchemaSupported(activeWorker.worker_schema_version) ? 'text-theme-text' : 'text-amber-500'}`}>
              {getWorkerSchemaVersion(activeWorker.worker_schema_version)}
              {!isWorkerSchemaSupported(activeWorker.worker_schema_version) && ' !'}
            </span>
          </span>
        )}
      </div>
    </div>
  );
};