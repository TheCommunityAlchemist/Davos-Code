import React from 'react';
import { Recommendation } from '@/types/events';

interface RecommendationCardProps {
  recommendation: Recommendation;
  index: number;
  onClick: () => void;
}

export function RecommendationCard({ recommendation, index, onClick }: RecommendationCardProps) {
  return (
    <div
      onClick={onClick}
      className="bg-white/[0.03] border border-white/[0.08] rounded-xl p-4 cursor-pointer transition-all duration-300 hover:bg-white/[0.06] hover:border-cyan-400 hover:translate-x-1"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="font-syne text-sm font-semibold flex-1 leading-tight text-white">
          {recommendation.title}
        </span>
        <span className="bg-gradient-to-br from-cyan-400 to-emerald-500 px-2 py-1 rounded-md text-[0.7rem] font-semibold text-[#0a1628] ml-2 whitespace-nowrap">
          {recommendation.match_percentage}%
        </span>
      </div>
      <div className="text-xs text-slate-400 mb-1">
        📍 {recommendation.venue}
      </div>
      <div className="text-[0.7rem] text-cyan-400 italic">
        💡 {recommendation.explanation}
      </div>
    </div>
  );
}
