import { Database, ChevronDown } from "lucide-react";
import { useDataset } from "../context/DatasetContext";

export function DatasetSelector() {
  const { datasets, selectedDatasetId, setSelectedDatasetId } = useDataset();
  return (
    <label className="dataset-selector">
      <Database size={16}/>
      <select value={selectedDatasetId} onChange={e => setSelectedDatasetId(e.target.value)}>
        {datasets.map(d => <option value={d.id} key={d.id}>{d.name}</option>)}
      </select>
      <ChevronDown size={14}/>
    </label>
  );
}
