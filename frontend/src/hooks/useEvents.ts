import { useState, useEffect, useCallback } from 'react';
import { DavosEvent, ApiResponse } from '@/types/events';
import { CONFIG } from '@/lib/constants';

export function useEvents() {
  const [events, setEvents] = useState<DavosEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${CONFIG.API_URL}/api/events`);
      const data: ApiResponse<DavosEvent> = await response.json();
      
      if (data.success && data.events) {
        setEvents(data.events);
      } else {
        setError(data.error || 'Failed to load events');
      }
    } catch (err) {
      console.error('Error loading events:', err);
      setError('Could not connect to API. Make sure your Railway backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const uniqueTracks = [...new Set(events.map(e => e.track))].sort();
  const uniqueVenues = [...new Set(events.map(e => e.venue))];

  return {
    events,
    loading,
    error,
    refetch: fetchEvents,
    uniqueTracks,
    venueCount: uniqueVenues.length,
  };
}
