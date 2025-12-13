import React, { useState, useCallback } from 'react';
import { Header } from '@/components/Header';
import { ChatPanel } from '@/components/ChatPanel';
import { DavosMap } from '@/components/DavosMap';
import { LoadingOverlay } from '@/components/LoadingOverlay';
import { useEvents } from '@/hooks/useEvents';
import { useRecommendations } from '@/hooks/useRecommendations';
import { Recommendation } from '@/types/events';

export default function Index() {
  const { events, venueCount, uniqueTracks } = useEvents();
  const { 
    recommendations, 
    message, 
    loading, 
    getRecommendations, 
    clearRecommendations 
  } = useRecommendations();
  
  const [activeFilter, setActiveFilter] = useState('all');

  const handleFilterChange = useCallback((track: string) => {
    setActiveFilter(track);
    if (track !== 'all') {
      clearRecommendations();
    }
  }, [clearRecommendations]);

  const handleRecommendationClick = useCallback((recommendation: Recommendation) => {
    // Fly to event on map
    const flyToEvent = (window as any).flyToEvent;
    if (flyToEvent) {
      flyToEvent(recommendation.id);
    }
  }, []);

  return (
    <div className="h-screen bg-[#0a1628] text-slate-100 font-mono overflow-hidden">
      <Header 
        eventCount={events.length} 
        venueCount={venueCount} 
      />
      
      <div className="flex h-screen pt-[70px] max-md:flex-col">
        <ChatPanel
          message={message}
          recommendations={recommendations}
          tracks={uniqueTracks}
          activeFilter={activeFilter}
          isLoading={loading}
          onSubmit={getRecommendations}
          onFilterChange={handleFilterChange}
          onRecommendationClick={handleRecommendationClick}
        />
        
        <DavosMap
          events={events}
          recommendations={recommendations}
          activeFilter={activeFilter}
        />
      </div>
      
      <LoadingOverlay 
        isVisible={loading} 
        message="Analyzing your profile..." 
      />
    </div>
  );
}
