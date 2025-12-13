export interface DavosEvent {
  id: string;
  title: string;
  venue: string;
  address?: string;
  location?: string;
  track: string;
  lat: number;
  lon: number;
  website?: string;
  date?: string;
  time?: string;
  description?: string;
}

export interface Recommendation extends DavosEvent {
  match_percentage: number;
  explanation: string;
}

export interface ApiResponse<T> {
  success: boolean;
  error?: string;
  message?: string;
  events?: T[];
  recommendations?: Recommendation[];
}
