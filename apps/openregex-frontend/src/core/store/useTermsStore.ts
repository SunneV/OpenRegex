import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface TermsState {
  hasAcceptedTerms: boolean;
  hasRejectedTerms: boolean;
  isTermsModalOpen: boolean;
  acceptTerms: () => void;
  rejectTerms: () => void;
  openTermsModal: () => void;
  closeTermsModal: () => void;
}

export const useTermsStore = create<TermsState>()(
  persist(
    (set) => ({
      hasAcceptedTerms: false,
      hasRejectedTerms: false,
      isTermsModalOpen: false,
      acceptTerms: () => set({ hasAcceptedTerms: true, hasRejectedTerms: false, isTermsModalOpen: false }),
      rejectTerms: () => set({ hasRejectedTerms: true }),
      openTermsModal: () => set({ isTermsModalOpen: true }),
      closeTermsModal: () => set({ isTermsModalOpen: false }),
    }),
    {
      name: 'openregex-terms-store',
      partialize: (state) => ({ hasAcceptedTerms: state.hasAcceptedTerms }),
    }
  )
);