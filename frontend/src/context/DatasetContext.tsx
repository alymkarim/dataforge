import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { RegisteredDataset } from "../types/pipeline";

type DatasetContextValue = {
  datasets: RegisteredDataset[];
  selectedDatasetId: string;
  selectedDataset: RegisteredDataset | null;
  setSelectedDatasetId: (id: string) => void;
  addDataset: (dataset: RegisteredDataset) => void;
};

const DatasetContext = createContext<DatasetContextValue | null>(null);

export function DatasetProvider({ children }: { children: ReactNode }) {
  const [datasets, setDatasets] = useState<RegisteredDataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState("ecommerce");

  useEffect(() => {
    fetch("/demo-data/datasets.json")
      .then(r => {
        if (!r.ok) throw new Error("Unable to load dataset registry");
        return r.json();
      })
      .then((rows: RegisteredDataset[]) => setDatasets(rows))
      .catch(() => setDatasets([]));
  }, []);

  const selectedDataset = useMemo(
    () => datasets.find(d => d.id === selectedDatasetId) ?? datasets[0] ?? null,
    [datasets, selectedDatasetId],
  );

  function addDataset(dataset: RegisteredDataset) {
    setDatasets(current => [dataset, ...current]);
    setSelectedDatasetId(dataset.id);
  }

  return (
    <DatasetContext.Provider value={{ datasets, selectedDatasetId, selectedDataset, setSelectedDatasetId, addDataset }}>
      {children}
    </DatasetContext.Provider>
  );
}

export function useDataset() {
  const value = useContext(DatasetContext);
  if (!value) throw new Error("useDataset must be used inside DatasetProvider");
  return value;
}
