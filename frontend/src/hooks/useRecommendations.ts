import { useState, useCallback } from 'react';
import { Recommendation, ApiResponse } from '@/types/events';
import { CONFIG } from '@/lib/constants';

export function useRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [message, setMessage] = useState<string>(
    '👋 Welcome to Davos 2026! Enter your LinkedIn URL or describe your interests to get personalized event recommendations.'
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getRecommendations = useCallback(async (input: string) => {
    if (!input.trim()) {
      setMessage('⚠️ Please enter your LinkedIn URL or describe your interests.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${CONFIG.API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      const data: ApiResponse<Recommendation> = await response.json();

      if (data.success) {
        setMessage(data.message || 'Here are your recommendations!');
        setRecommendations(data.recommendations || []);
      } else {
        setMessage('❌ ' + (data.error || 'Something went wrong'));
        setError(data.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Error getting recommendations:', err);
      const errorMessage = 'Could not connect to the AI agent. Please check if your API is running.';
      setMessage('⚠️ ' + errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearRecommendations = useCallback(() => {
    setRecommendations([]);
    setMessage('👋 Welcome to Davos 2026! Enter your LinkedIn URL or describe your interests to get personalized event recommendations.');
  }, []);

  return {
    recommendations,
    message,
    loading,
    error,
    getRecommendations,
    clearRecommendations,
  };
}
