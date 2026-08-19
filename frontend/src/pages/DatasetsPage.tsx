import { Plus } from "lucide-react";
import { Link } from "react-router-dom";
import { DatasetCard } from "../components/DatasetCard";
import { PageHeader } from "../components/PageHeader";
import { useDataset } from "../context/DatasetContext";

export function DatasetsPage() {
  const { datasets, setSelectedDatasetId } = useDataset();
  return <>
    <div className="page-header-action">
      <PageHeader title="Datasets" description="Register, inspect and process datasets through the platform."/>
      <Link className="primary-btn link-btn" to="/datasets/add"><Plus size={16}/> Add Dataset</Link>
    </div>
    <div className="dataset-grid">
      {datasets.map(d => <DatasetCard key={d.id} dataset={d} onSelect={() => setSelectedDatasetId(d.id)}/>)}
    </div>
    <section className="platform-purpose">
      <span className="eyebrow">HOW IT WORKS</span>
      <h3>One platform, multiple data workloads</h3>
      <p>Generic ingestion, profiling, validation and Silver processing work across tabular datasets. Gold analytics and ML features are enabled for supported domains where meaningful transformations are defined.</p>
    </section>
  </>;
}
