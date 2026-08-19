import { Database, ArrowRight, Cpu, BrainCircuit } from "lucide-react";
import { Link } from "react-router-dom";
import type { RegisteredDataset } from "../types/pipeline";
import { StatusBadge } from "./StatusBadge";

export function DatasetCard({ dataset, onSelect }: { dataset: RegisteredDataset; onSelect: () => void }) {
  return (
    <article className="dataset-card">
      <div className="dataset-card-top">
        <div className="dataset-card-icon"><Database size={21}/></div>
        <StatusBadge status={dataset.status}/>
      </div>
      <span className="eyebrow">{dataset.domain}</span>
      <h3>{dataset.name}</h3>
      <p>{dataset.description}</p>
      <div className="dataset-card-stats">
        <div><strong>{dataset.rows.toLocaleString()}</strong><span>Rows</span></div>
        <div><strong>{dataset.columns}</strong><span>Columns</span></div>
        <div><strong>{dataset.size}</strong><span>Size</span></div>
      </div>
      <div className="capability-row">
        <span className={dataset.supportsGold ? "enabled" : ""}><Cpu size={14}/> Gold</span>
        <span className={dataset.supportsML ? "enabled" : ""}><BrainCircuit size={14}/> ML</span>
      </div>
      <div className="dataset-card-foot">
        <small>{dataset.lastProcessed ? `Processed ${dataset.lastProcessed}` : "Not processed yet"}</small>
        <Link to="/" onClick={onSelect}>Open <ArrowRight size={14}/></Link>
      </div>
    </article>
  );
}
