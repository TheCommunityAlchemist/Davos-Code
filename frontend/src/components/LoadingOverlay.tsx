import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
}

export function LoadingOverlay({ isVisible, message = 'Analyzing your profile...' }: LoadingOverlayProps) {
  return (
    <div
      className={cn(
        'fixed inset-0 bg-[#050d18]/90 z-[2000] flex-col gap-4 justify-center items-center',
        isVisible ? 'flex' : 'hidden'
      )}
    >
      <div className="w-10 h-10 border-[3px] border-white/10 border-t-cyan-400 rounded-full animate-spin" />
      <p className="text-slate-400 text-sm">{message}</p>
    </div>
  );
}
