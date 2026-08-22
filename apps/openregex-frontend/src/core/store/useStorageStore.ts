import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface PersonalItem {
  id: string;
  name?: string;
  tags?: string[];
  engineId: string;
  engineLabel: string;
  regex: string;
  text: string;
  flags: string[];
  matchCount: number;
  timestamp: number;
}

export interface HistoryItem {
  id: string;
  engineId: string;
  regex: string;
  text: string;
  flags: string[];
  timestamp: number;
}

interface StorageState {
  personal: PersonalItem[];
  history: HistoryItem[];
  historyIndex: number;
  addPersonal: (item: Omit<PersonalItem, 'id' | 'timestamp'>) => void;
  removePersonal: (id: string) => void;
  clearPersonal: () => void;
  importPersonal: (items: PersonalItem[]) => number;
  updatePersonalItem: (id: string, updates: Partial<PersonalItem>) => void;
  pushHistory: (item: Omit<HistoryItem, 'id' | 'timestamp'>) => void;
  setHistoryIndex: (index: number) => void;
  clearHistory: () => void;
}

export const useStorageStore = create<StorageState>()(
  persist(
    (set) => ({
      personal: [],
      history: [],
      historyIndex: -1,

      addPersonal: (item) => set((state) => ({
        personal: [{ ...item, tags: item.tags || [], id: crypto.randomUUID(), timestamp: Date.now() }, ...state.personal]
      })),

      removePersonal: (id) => set((state) => ({
        personal: state.personal.filter((i) => i.id !== id)
      })),

      clearPersonal: () => set({ personal: [] }),

      // Single state update regardless of dump size; imported items win on id collision.
      importPersonal: (items) => {
        let imported = 0;
        set((state) => {
          const merged = new Map<string, PersonalItem>();
          state.personal.forEach((i) => merged.set(i.id, i));
          items.forEach((i) => {
            if (!merged.has(i.id)) imported++;
            merged.set(i.id, i);
          });
          return { personal: Array.from(merged.values()).sort((a, b) => b.timestamp - a.timestamp) };
        });
        return imported;
      },

      updatePersonalItem: (id, updates) => set((state) => ({
        personal: state.personal.map((i) => i.id === id ? { ...i, ...updates } : i)
      })),

      pushHistory: (item) => set((state) => {
        const currentIndex = state.historyIndex === -1 ? 0 : state.historyIndex;
        const currentItem = state.history[currentIndex];

        if (
          currentItem &&
          currentItem.engineId === item.engineId &&
          currentItem.regex === item.regex &&
          currentItem.text === item.text &&
          JSON.stringify(currentItem.flags) === JSON.stringify(item.flags)
        ) {
          return state;
        }

        let newHistory = state.history;
        if (state.historyIndex > 0) {
          newHistory = state.history.slice(state.historyIndex);
        }

        if (
          newHistory[0] &&
          newHistory[0].engineId === item.engineId &&
          newHistory[0].regex === item.regex &&
          newHistory[0].text === item.text &&
          JSON.stringify(newHistory[0].flags) === JSON.stringify(item.flags)
        ) {
          return { history: newHistory, historyIndex: 0 };
        }

        const updatedHistory = [{ ...item, id: crypto.randomUUID(), timestamp: Date.now() }, ...newHistory].slice(0, 100);
        return { history: updatedHistory, historyIndex: 0 };
      }),

      setHistoryIndex: (index) => set({ historyIndex: index }),

      clearHistory: () => set({ history: [], historyIndex: -1 })
    }),
    {
      name: 'openregex-storage-store'
    }
  )
);