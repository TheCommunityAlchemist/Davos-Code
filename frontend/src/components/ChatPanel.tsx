import React, { useState, KeyboardEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { RecommendationCard } from './RecommendationCard';
import { FilterChips } from './FilterChips';
import { Recommendation } from '@/types/events';

interface ChatPanelProps {
  message: string;
  recommendations: Recommendation[];
  tracks: string[];
  activeFilter: string;
  isLoading: boolean;
  onSubmit: (input: string) => void;
  onFilterChange: (track: string) => void;
  onRecommendationClick: (recommendation: Recommendation) => void;
}

export function ChatPanel({
  message,
  recommendations,
  tracks,
  activeFilter,
  isLoading,
  onSubmit,
  onFilterChange,
  onRecommendationClick,
}: ChatPanelProps) {
  const [linkedinInput, setLinkedinInput] = useState('');
  const [profileInput, setProfileInput] = useState('');

  const handleSubmit = () => {
    const input = linkedinInput.trim() || profileInput.trim();
    if (input) {
      onSubmit(input);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <aside className="w-[400px] bg-gradient-to-b from-[#0a1628]/[0.98] to-[#1a4a6e]/20 border-r border-white/5 flex flex-col overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-[#1a4a6e] max-md:fixed max-md:bottom-0 max-md:left-0 max-md:right-0 max-md:w-full max-md:h-[50vh] max-md:border-r-0 max-md:border-t max-md:border-white/10 max-md:rounded-t-[20px] max-md:z-[500]">
      {/* Input Section */}
      <div className="mb-6">
        <label className="block text-[0.7rem] text-cyan-400 uppercase tracking-wider mb-3">
          🔗 Your LinkedIn or Profile
        </label>
        
        <div className="relative mb-3">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 bg-[#0A66C2] text-white font-bold text-[0.65rem] px-1.5 py-0.5 rounded-sm">
            in
          </span>
          <Input
            type="text"
            value={linkedinInput}
            onChange={(e) => setLinkedinInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="linkedin.com/in/yourname"
            className="pl-11 bg-white/5 border-white/10 text-white placeholder:text-white/30 focus:border-[#0A66C2] focus:ring-[#0A66C2]/30"
          />
        </div>

        <div className="flex items-center my-4 text-slate-400 text-[0.7rem]">
          <div className="flex-1 h-px bg-white/10" />
          <span className="px-3 uppercase tracking-wider">or describe yourself</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        <Textarea
          value={profileInput}
          onChange={(e) => setProfileInput(e.target.value)}
          placeholder="I'm a climate scientist interested in blockchain, sustainable finance, and international policy..."
          className="min-h-[100px] bg-white/5 border-white/10 text-white placeholder:text-white/30 focus:border-emerald-500 focus:ring-emerald-500/20 resize-y"
        />

        <Button
          onClick={handleSubmit}
          disabled={isLoading}
          className="w-full mt-4 bg-gradient-to-br from-cyan-400 to-emerald-500 text-[#0a1628] font-syne font-semibold uppercase tracking-wider hover:shadow-lg hover:shadow-cyan-400/40 hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:translate-y-0"
        >
          ✨ Get AI Recommendations
        </Button>
      </div>

      {/* AI Response */}
      <div className="mb-6">
        <div className="bg-cyan-400/10 border border-cyan-400/20 rounded-xl p-4 text-sm leading-relaxed">
          <p dangerouslySetInnerHTML={{ __html: message.replace(/\n/g, '<br/>') }} />
        </div>
      </div>

      {/* Recommendations List */}
      {recommendations.length > 0 && (
        <div className="flex-1 flex flex-col gap-3 mb-6">
          {recommendations.map((rec, index) => (
            <RecommendationCard
              key={rec.id}
              recommendation={rec}
              index={index}
              onClick={() => onRecommendationClick(rec)}
            />
          ))}
        </div>
      )}

      {/* Quick Filters */}
      <FilterChips
        tracks={tracks}
        activeFilter={activeFilter}
        onFilterChange={onFilterChange}
      />
    </aside>
  );
}
