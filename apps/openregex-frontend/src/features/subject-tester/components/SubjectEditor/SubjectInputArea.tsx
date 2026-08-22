import React, { useRef, useEffect } from 'react';
import { Chunk } from '../Chunk';
import { SHARED_SUBJECT_CLASSES, SHARED_GUTTER_CLASSES } from './constants';
import { Segment } from '../../utils/segment.utils';

interface SubjectInputAreaProps {
  text: string;
  setText: (val: string) => void;
  matchesCount: number;
  chunks: Segment[][];
  selectionState: any;
  overlayRef: React.RefObject<HTMLDivElement>;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  onMouseMove: (e: React.MouseEvent<HTMLDivElement>) => void;
  onMouseLeave: () => void;
  onClick: (e: React.MouseEvent<HTMLTextAreaElement | HTMLDivElement>) => void;
}

export const SubjectInputArea: React.FC<SubjectInputAreaProps> = ({
  text, setText, matchesCount, chunks, selectionState, overlayRef, textareaRef, onMouseMove, onMouseLeave, onClick
}) => {
  const gutterRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const overlay = overlayRef.current;
    const gutter = gutterRef.current;
    if (!overlay || !gutter) return;

    const syncGutter = () => { gutter.scrollTop = overlay.scrollTop; };
    overlay.addEventListener('scroll', syncGutter, { passive: true });
    return () => overlay.removeEventListener('scroll', syncGutter);
  }, [overlayRef]);

  const handleScroll = (e: React.UIEvent<HTMLTextAreaElement>) => {
    if (overlayRef.current) {
      overlayRef.current.scrollTop = e.currentTarget.scrollTop;
      overlayRef.current.scrollLeft = e.currentTarget.scrollLeft;
    }
    if (gutterRef.current) {
      gutterRef.current.scrollTop = e.currentTarget.scrollTop;
    }
  };

  const lineCount = text.split('\n').length;
  const linesStr = Array.from({ length: Math.max(1, lineCount) }, (_, i) => i + 1).join('\n');

  return (
    <div className="relative flex-1 flex min-h-[80px]" onMouseMove={onMouseMove} onMouseLeave={onMouseLeave}>
      <div
        ref={gutterRef}
        className={`w-12 shrink-0 bg-black/5 dark:bg-white/5 border-r border-ide-border text-theme-muted/50 text-right overflow-hidden ${SHARED_GUTTER_CLASSES}`}
      >
        {linesStr}
        {text.endsWith('\n') && <br/>}
      </div>

      <div className="relative flex-1 min-w-0">
        <div ref={overlayRef} className={`absolute inset-0 overflow-auto z-0 isolate pointer-events-auto text-ide-text [scrollbar-width:none] [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] ${SHARED_SUBJECT_CLASSES}`}>
          {chunks.map((chunkSegments, idx) => (
            <Chunk key={idx} segments={chunkSegments} selectionState={selectionState} rootRef={overlayRef} />
          ))}
          {text.endsWith('\n') && <br />}
        </div>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value.replace(/\r/g, ''))}
          onScroll={handleScroll}
          onClick={onClick}
          placeholder="Enter text to match against..."
          spellCheck={false}
          className={`absolute inset-0 w-full h-full bg-transparent text-ide-text resize-none placeholder-ide-dim overflow-auto custom-scrollbar z-10 pointer-events-auto ${SHARED_SUBJECT_CLASSES} ${matchesCount > 0 ? 'text-transparent caret-theme-text' : ''}`}
        />
      </div>
    </div>
  );
};