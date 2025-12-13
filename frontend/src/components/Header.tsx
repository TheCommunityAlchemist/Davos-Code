import React from 'react';

interface HeaderProps {
  eventCount: number;
  venueCount: number;
}

export function Header({ eventCount, venueCount }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-[70px] bg-gradient-to-b from-[#050d18] to-[#050d18]/90 backdrop-blur-lg border-b border-white/5 flex justify-between items-center px-8">
      <div className="flex items-center gap-4">
        <div className="w-[45px] h-[45px] bg-gradient-to-br from-cyan-400 to-emerald-500 rounded-xl flex items-center justify-center text-2xl">
          🏔️
        </div>
        <div>
          <h1 className="font-syne text-xl font-bold bg-gradient-to-br from-slate-100 to-slate-400 bg-clip-text text-transparent">
            DAVOS 2026
          </h1>
          <span className="text-[0.65rem] text-cyan-400 tracking-widest uppercase">
            AI Event Navigator
          </span>
        </div>
      </div>
      
      <div className="flex gap-8">
        <div className="text-center">
          <span className="font-syne text-2xl font-extrabold bg-gradient-to-br from-cyan-400 to-emerald-500 bg-clip-text text-transparent block">
            {eventCount}
          </span>
          <span className="text-[0.6rem] text-slate-400 uppercase tracking-wider">
            Events
          </span>
        </div>
        <div className="text-center">
          <span className="font-syne text-2xl font-extrabold bg-gradient-to-br from-cyan-400 to-emerald-500 bg-clip-text text-transparent block">
            {venueCount || '--'}
          </span>
          <span className="text-[0.6rem] text-slate-400 uppercase tracking-wider">
            Venues
          </span>
        </div>
      </div>
    </header>
  );
}
