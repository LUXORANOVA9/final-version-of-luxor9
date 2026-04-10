import { useState, useEffect } from 'react';

export function useLuxorAPI() {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchHierarchy = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/system/hierarchy`);
      if (\!res.ok) throw new Error('Failed to fetch hierarchy');
      return await res.json();
    } catch (e) {
      console.error("Hierarchy Fetch Error:", e);
      return null;
    }
  };

  const bootSystem = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/system/boot`, { method: 'POST' });
      return res.ok;
    } catch (e) {
      console.error("Boot Error:", e);
      return false;
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/metrics/live`);
      return await res.json();
    } catch (e) {
      console.error("Metrics Error:", e);
      return null;
    }
  };

  return { fetchHierarchy, bootSystem, fetchMetrics };
}
