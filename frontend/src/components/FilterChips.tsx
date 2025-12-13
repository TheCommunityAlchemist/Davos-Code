import React from 'react';
import { cn } from '@/lib/utils';

interface FilterChipsProps {
  tracks: string[];
  activeFilter: string;
  onFilterChange: (track: string) => void;
}

export function FilterChips({ tracks, activeFilter, onFilterChange }: FilterChipsProps) {
  return (
    <div className="mt-auto pt-4 border-t border-white/5">
      <label className="block text-[0.7rem] text-cyan-400 uppercase tracking-wider mb-3">
        🏷️ Quick Filters
      </label>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onFilterChange('all')}
          className={cn(
            'px-3 py-2 rounded-full text-[0.7rem] transition-all duration-300',
            activeFilter === 'all'
              ? 'bg-gradient-to-br from-cyan-400 to-emerald-500 text-[#0a1628] font-medium border-transparent'
              : 'bg-white/5 border border-white/10 text-slate-400 hover:bg-white/10'
          )}
        >
          All Events
        </button>
        {tracks.map((track) => (
          <button
            key={track}
            onClick={() => onFilterChange(track)}
            className={cn(
              'px-3 py-2 rounded-full text-[0.7rem] transition-all duration-300',
              activeFilter === track
                ? 'bg-gradient-to-br from-cyan-400 to-emerald-500 text-[#0a1628] font-medium border-transparent'
                : 'bg-white/5 border border-white/10 text-slate-400 hover:bg-white/10'
            )}
          >
            {track.split(' ')[0]}
          </button>
        ))}
      </div>
    </div>
  );
}
