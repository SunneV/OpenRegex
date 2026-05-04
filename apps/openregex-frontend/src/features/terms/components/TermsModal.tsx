import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ShieldCheck, X, FileText, Cookie, AlertTriangle } from 'lucide-react';
import { useTermsStore } from '../../../core/store/useTermsStore';

export const TermsModal: React.FC = () => {
  const { hasAcceptedTerms, hasRejectedTerms, isTermsModalOpen, acceptTerms, rejectTerms, closeTermsModal } = useTermsStore();
  const [termsContent, setTermsContent] = useState<string>('Loading terms...');
  const [view, setView] = useState<'main' | 'terms' | 'cookies'>('main');

  // Yes, this checks the VITE_APP_TERMS variable. If it's "accepted", the modal will not be forced open.
  const isForced = import.meta.env.VITE_APP_TERMS !== 'accept' && !hasAcceptedTerms;
  const isOpen = isForced || isTermsModalOpen;

  useEffect(() => {
    if (isOpen && view === 'terms') {
      fetch('/TERMS.md')
        .then((res) => {
          if (!res.ok) throw new Error('Terms file not found');
          return res.text();
        })
        .then((text) => setTermsContent(text))
        .catch(() => setTermsContent('Terms of Service document could not be loaded.'));
    }
  }, [isOpen, view]);

  const handleClose = () => {
    setView('main');
    closeTermsModal();
  };

  if (!isOpen) return null;

  if (hasRejectedTerms && isForced) {
    return (
      <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div className="bg-theme-base dark:bg-[#121216] border border-rose-500/30 shadow-2xl rounded-[20px] w-full max-w-md p-6 flex flex-col items-center text-center">
          <AlertTriangle size={48} className="text-rose-500 mb-4" />
          <h2 className="text-lg font-bold text-theme-text mb-2 uppercase tracking-widest">Access Denied</h2>
          <p className="text-xs text-theme-muted mb-6">
            You must accept the Terms of Service and Cookie Policy to use OpenRegex.
          </p>
          <button
            onClick={() => useTermsStore.setState({ hasRejectedTerms: false })}
            className="w-full py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-xl text-xs font-bold uppercase tracking-wider transition-colors"
          >
            Review Terms Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
      <div className="bg-theme-base dark:bg-[#121216] border border-theme-border shadow-2xl rounded-[20px] w-full max-w-2xl flex flex-col max-h-[85vh] overflow-hidden animate-in fade-in zoom-in-95 duration-200">

        <div className="flex items-center justify-between px-6 py-4 border-b border-theme-border bg-black/5 dark:bg-white/5 shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-500">
              <ShieldCheck size={20} strokeWidth={2.5} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-theme-text uppercase tracking-widest">
                {view === 'main' ? 'Legal & Privacy' : view === 'terms' ? 'Terms of Service' : 'Cookie Policy'}
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {view !== 'main' && (
              <button
                onClick={() => setView('main')}
                className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 rounded transition-colors"
              >
                Back
              </button>
            )}
            {!isForced && (
              <button
                onClick={handleClose}
                className="p-2 text-theme-muted hover:text-theme-text hover:bg-rose-500/10 hover:text-rose-500 rounded-full transition-colors"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
          {view === 'main' && (
            <div className="flex flex-col gap-6">
              <p className="text-sm text-theme-text/80 leading-relaxed text-center px-4">
                Before you continue to <strong className="text-theme-primary">OpenRegex</strong>, please review and accept our <strong>Terms of Service</strong> and <strong>Cookie Policy</strong>.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() => setView('terms')}
                  className="flex flex-col items-center justify-center gap-4 p-8 rounded-2xl border border-theme-border bg-gradient-to-b from-black/5 to-black/10 dark:from-white/5 dark:to-white/10 hover:from-purple-500/10 hover:to-purple-500/20 hover:border-purple-500/50 shadow-sm hover:shadow-purple-500/20 transition-all duration-300 group"
                >
                  <div className="p-4 bg-black/5 dark:bg-white/5 rounded-full group-hover:bg-purple-500/20 transition-colors">
                    <FileText size={36} className="text-theme-muted group-hover:text-purple-500 transition-colors" />
                  </div>
                  <span className="text-sm font-black uppercase tracking-widest text-theme-text group-hover:text-purple-500 transition-colors">Terms of Service</span>
                </button>

                <button
                  onClick={() => setView('cookies')}
                  className="flex flex-col items-center justify-center gap-4 p-8 rounded-2xl border border-theme-border bg-gradient-to-b from-black/5 to-black/10 dark:from-white/5 dark:to-white/10 hover:from-purple-500/10 hover:to-purple-500/20 hover:border-purple-500/50 shadow-sm hover:shadow-purple-500/20 transition-all duration-300 group"
                >
                  <div className="p-4 bg-black/5 dark:bg-white/5 rounded-full group-hover:bg-purple-500/20 transition-colors">
                    <Cookie size={36} className="text-theme-muted group-hover:text-purple-500 transition-colors" />
                  </div>
                  <span className="text-sm font-black uppercase tracking-widest text-theme-text group-hover:text-purple-500 transition-colors">Cookie Policy</span>
                </button>
              </div>
            </div>
          )}

          {view === 'terms' && (
            <div className="text-xs text-theme-text leading-relaxed prose prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{termsContent}</ReactMarkdown>
            </div>
          )}

          {view === 'cookies' && (
            <div className="text-xs text-theme-text leading-relaxed flex flex-col gap-4">
              <h3 className="text-sm font-bold uppercase tracking-widest">How we use Cookies</h3>
              <p>
                OpenRegex uses essential cookies and local storage to ensure the proper functioning of the application.
                These are required to save your preferences, theme settings, and application state locally on your device.
              </p>
              <p>
                <strong>Essential Local Storage:</strong> We store your accepted terms, regex history, and personal regex saves directly in your browser using `localStorage`. This data does not leave your device unless you explicitly share a link.
              </p>
              <p>
                By accepting, you consent to the use of these essential local storage mechanisms. We do not use third-party tracking or advertising cookies.
              </p>
            </div>
          )}
        </div>

        {view === 'main' && isForced && (
          <div className="flex items-center gap-3 px-6 py-4 border-t border-theme-border bg-ide-bg shrink-0">
            <button
              onClick={rejectTerms}
              className="flex-1 py-3 px-4 rounded-xl text-xs font-bold uppercase tracking-wider text-rose-500 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition-all"
            >
              Reject
            </button>
            <button
              onClick={acceptTerms}
              className="flex-1 py-3 px-4 rounded-xl text-xs font-bold uppercase tracking-wider bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/20 transition-all"
            >
              Accept All
            </button>
          </div>
        )}
      </div>
    </div>
  );
};