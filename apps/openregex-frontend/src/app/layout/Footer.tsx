/// <reference types="vite/client" />
import React from 'react';
import { Github, Heart, Linkedin, FileCode, ExternalLink, ShieldCheck } from 'lucide-react';
import { useTermsStore } from '../../core/store/useTermsStore';

interface FooterProps {
  frontendVersion: string;
  backendVersion: string;
  backendReleaseDate: string;
}

export const Footer: React.FC<FooterProps> = ({ frontendVersion, backendVersion, backendReleaseDate }) => {
  const frontendReleaseDate = import.meta.env.VITE_APP_RELEASE_DATE || 'Unknown';
  const { openTermsModal } = useTermsStore();

  return (
    <footer className="flex flex-col md:flex-row justify-between items-center md:items-stretch gap-2 md:gap-4 z-20 h-auto md:h-[40px] w-full">

      <div className="w-full md:w-auto md:flex-1 flex justify-center md:justify-start h-[36px] md:h-full">
        <div className="glass-panel rounded-full px-5 flex items-center justify-center gap-4 shadow-sm h-full w-full md:w-auto">
          <a
            href="/api"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-[10px] font-bold text-theme-primary hover:opacity-80 hover:scale-105 transition-all duration-300 uppercase tracking-wider"
          >
            <FileCode size={13} /> API Docs <ExternalLink size={10} className="ml-0.5" />
          </a>
        </div>
      </div>

      <div className="w-full md:w-auto flex-initial flex items-center justify-center h-[36px] md:h-full">
        <div className="glass-panel rounded-full px-6 flex items-center justify-center gap-4 md:gap-6 shadow-sm h-full w-full md:w-auto">
          <a
            href="https://github.com/sunnev/openregex"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-[10px] font-semibold text-theme-muted hover:text-black dark:hover:text-white hover:scale-110 hover:-translate-y-0.5 transition-all duration-300 ease-[cubic-bezier(0.175,0.885,0.32,1.275)]"
          >
            <Github size={13} /> SOURCE
          </a>
          <a
            href="https://www.linkedin.com/in/wojciech-cicho%C5%84-421127141/"
            target="_blank"
            rel="noopener noreferrer"
            title="SunneV (Wojciech Mariusz Cichoń)"
            className="flex items-center gap-1.5 text-[10px] font-semibold text-theme-muted hover:text-[#0A66C2] hover:scale-110 hover:-translate-y-0.5 transition-all duration-300 ease-[cubic-bezier(0.175,0.885,0.32,1.275)]"
          >
            <Linkedin size={13} /> AUTHOR
          </a>
          <a
            href="https://github.com/sponsors/sunnev"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-[10px] font-semibold text-theme-muted hover:text-pink-500 hover:scale-110 hover:-translate-y-0.5 transition-all duration-300 ease-[cubic-bezier(0.175,0.885,0.32,1.275)] group"
          >
            <Heart size={13} className="transition-all duration-300 group-hover:fill-pink-500 group-hover:text-pink-500" />
            SPONSOR
          </a>
        </div>
      </div>

      <div className="w-full md:w-auto md:flex-1 flex justify-center md:justify-end h-[36px] md:h-full">
        <div className="glass-panel rounded-full px-5 flex items-center justify-center shadow-sm h-full w-full md:w-auto gap-3">
          <button
            onClick={openTermsModal}
            className="flex flex-col items-center md:items-start justify-center leading-none gap-0.5 text-theme-text hover:text-purple-500 transition-colors"
            title="Terms & Cookies"
          >
            <span className="text-[9px] font-mono font-bold flex items-center gap-1"><ShieldCheck size={10} /> TERMS</span>
          </button>

          <div className="w-px h-4 bg-theme-border opacity-40"></div>

          <div className="flex flex-col items-center md:items-end justify-center leading-none gap-0.5 cursor-help" title={`Frontend Release: ${frontendReleaseDate}`}>
            <span className="text-[9px] font-mono text-theme-text font-bold">GUI: {frontendVersion}</span>
          </div>
          <div className="w-px h-4 bg-theme-border opacity-40"></div>
          <div className="flex flex-col items-center md:items-start justify-center leading-none gap-0.5 cursor-help" title={`Backend Release: ${backendReleaseDate}`}>
            <span className="text-[9px] font-mono text-theme-text font-bold">API: {backendVersion}</span>
          </div>
        </div>
      </div>

    </footer>
  );
};