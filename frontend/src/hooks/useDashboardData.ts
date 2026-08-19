import { useEffect, useState } from "react";
import { loadDashboardData } from "../services/pipelineApi";
import type { DashboardData } from "../types/pipeline";

export function useDashboardData() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData()
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Unable to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  return { data, error, loading };
}
