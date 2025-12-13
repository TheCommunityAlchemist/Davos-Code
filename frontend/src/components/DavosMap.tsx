import React, { useEffect, useRef, useCallback, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Button } from '@/components/ui/button';
import { DavosEvent, Recommendation } from '@/types/events';
import { CONFIG, getTrackColor } from '@/lib/constants';

interface DavosMapProps {
  events: DavosEvent[];
  recommendations: Recommendation[];
  activeFilter: string;
  onMapReady?: () => void;
}

interface MarkerData {
  marker: mapboxgl.Marker;
  element: HTMLDivElement;
  event: DavosEvent;
}

export function DavosMap({ events, recommendations, activeFilter, onMapReady }: DavosMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markers = useRef<Record<string, MarkerData>>({});
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    mapboxgl.accessToken = CONFIG.MAPBOX_TOKEN;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: CONFIG.DAVOS_CENTER,
      zoom: CONFIG.DEFAULT_ZOOM,
      pitch: CONFIG.DEFAULT_PITCH,
      bearing: CONFIG.DEFAULT_BEARING,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'bottom-right');

    map.current.on('load', () => {
      setMapLoaded(true);
      onMapReady?.();
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [onMapReady]);

  // Add markers when events change
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    // Clear existing markers
    Object.values(markers.current).forEach(({ marker }) => marker.remove());
    markers.current = {};

    // Add new markers
    events.forEach((event) => {
      const el = document.createElement('div');
      el.className = 'marker';
      el.style.width = '14px';
      el.style.height = '14px';
      el.style.backgroundColor = getTrackColor(event.track);
      el.style.borderRadius = '50%';
      el.style.border = '2px solid white';
      el.style.cursor = 'pointer';
      el.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
      el.style.transition = 'all 0.3s ease';

      const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
        <div style="font-family: 'JetBrains Mono', monospace; background: rgba(10, 22, 40, 0.95); padding: 1rem; border-radius: 12px; color: #f8fafc; min-width: 250px;">
          <div style="font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">${event.title}</div>
          <div style="font-size: 0.8rem; color: #06b6d4; margin-bottom: 0.25rem;">📍 ${event.venue}</div>
          <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.5rem;">${event.address || event.location || ''}</div>
          <span style="display: inline-block; padding: 0.25rem 0.5rem; background: rgba(6, 182, 212, 0.2); border-radius: 4px; font-size: 0.65rem; color: #06b6d4; text-transform: uppercase;">${event.track}</span>
          ${event.website ? `<a href="${event.website}" target="_blank" style="display: block; margin-top: 0.5rem; color: #10b981; font-size: 0.8rem; text-decoration: none;">🔗 Visit Website</a>` : ''}
        </div>
      `);

      const marker = new mapboxgl.Marker(el)
        .setLngLat([event.lon, event.lat])
        .setPopup(popup)
        .addTo(map.current!);

      markers.current[event.id] = { marker, element: el, event };
    });
  }, [events, mapLoaded]);

  // Handle recommendations highlighting
  useEffect(() => {
    if (!mapLoaded || activeFilter !== 'all') return;

    if (recommendations.length > 0) {
      // Dim all markers
      Object.values(markers.current).forEach(({ element }) => {
        element.style.opacity = '0.3';
        element.style.transform = 'scale(0.8)';
      });

      // Highlight recommended markers
      recommendations.forEach((rec, index) => {
        const markerData = markers.current[rec.id];
        if (markerData) {
          const { element } = markerData;
          element.style.opacity = '1';
          element.style.transform = 'scale(1.3)';
          element.style.width = '20px';
          element.style.height = '20px';
          element.style.boxShadow = `0 0 20px ${getTrackColor(rec.track)}`;
          element.style.zIndex = String(100 - index);
        }
      });

      // Fly to first recommendation
      const first = recommendations[0];
      map.current?.flyTo({
        center: [first.lon, first.lat],
        zoom: 16,
        pitch: 60,
        duration: 2000,
      });
    } else {
      // Reset all markers
      Object.values(markers.current).forEach(({ element }) => {
        element.style.opacity = '1';
        element.style.transform = 'scale(1)';
        element.style.width = '14px';
        element.style.height = '14px';
        element.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
      });
    }
  }, [recommendations, mapLoaded, activeFilter]);

  // Handle filter changes
  useEffect(() => {
    if (!mapLoaded) return;

    if (activeFilter === 'all') {
      Object.values(markers.current).forEach(({ element }) => {
        element.style.opacity = '1';
        element.style.transform = 'scale(1)';
      });
    } else {
      Object.values(markers.current).forEach(({ element, event }) => {
        if (event.track === activeFilter) {
          element.style.opacity = '1';
          element.style.transform = 'scale(1.2)';
        } else {
          element.style.opacity = '0.2';
          element.style.transform = 'scale(0.7)';
        }
      });
    }
  }, [activeFilter, mapLoaded]);

  const resetView = useCallback(() => {
    map.current?.flyTo({
      center: CONFIG.DAVOS_CENTER,
      zoom: CONFIG.DEFAULT_ZOOM,
      pitch: CONFIG.DEFAULT_PITCH,
      bearing: CONFIG.DEFAULT_BEARING,
      duration: 1500,
    });

    Object.values(markers.current).forEach(({ element }) => {
      element.style.opacity = '1';
      element.style.transform = 'scale(1)';
      element.style.width = '14px';
      element.style.height = '14px';
      element.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
    });
  }, []);

  const toggle3D = useCallback(() => {
    const currentPitch = map.current?.getPitch() || 0;
    map.current?.easeTo({
      pitch: currentPitch > 0 ? 0 : 60,
      duration: 1000,
    });
  }, []);

  const flyToEvent = useCallback((eventId: string) => {
    const markerData = markers.current[eventId];
    if (markerData && map.current) {
      const { marker, event } = markerData;
      map.current.flyTo({
        center: [event.lon, event.lat],
        zoom: 17,
        pitch: 60,
        duration: 1500,
      });
      marker.togglePopup();
    }
  }, []);

  // Expose flyToEvent via ref or context if needed
  (window as any).flyToEvent = flyToEvent;

  return (
    <div className="flex-1 relative max-md:h-[50vh]">
      <div ref={mapContainer} className="w-full h-full" />
      
      <div className="absolute bottom-8 right-8 flex flex-col gap-2">
        <Button
          onClick={resetView}
          variant="outline"
          size="icon"
          className="w-11 h-11 bg-[#0a1628]/90 border-white/10 hover:bg-[#1a4a6e] text-xl"
          title="Reset View"
        >
          🏠
        </Button>
        <Button
          onClick={toggle3D}
          variant="outline"
          size="icon"
          className="w-11 h-11 bg-[#0a1628]/90 border-white/10 hover:bg-[#1a4a6e] text-xl"
          title="Toggle 3D"
        >
          🎢
        </Button>
      </div>
    </div>
  );
}
