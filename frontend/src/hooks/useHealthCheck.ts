/**
 * Hook for checking backend connection status
 */

import { useState, useEffect, useCallback } from "react";
import { healthCheck } from "@/services/api";

interface UseHealthCheckReturn {
  isConnected: boolean;
  isChecking: boolean;
  lastChecked: Date | null;
  checkNow: () => Promise<void>;
}

const CHECK_INTERVAL = 30000; // 30 seconds

export function useHealthCheck(): UseHealthCheckReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkNow = useCallback(async () => {
    setIsChecking(true);
    try {
      await healthCheck();
      setIsConnected(true);
    } catch {
      setIsConnected(false);
    } finally {
      setIsChecking(false);
      setLastChecked(new Date());
    }
  }, []);

  // Initial check and periodic polling
  useEffect(() => {
    checkNow();

    const interval = setInterval(checkNow, CHECK_INTERVAL);
    return () => clearInterval(interval);
  }, [checkNow]);

  return {
    isConnected,
    isChecking,
    lastChecked,
    checkNow,
  };
}
