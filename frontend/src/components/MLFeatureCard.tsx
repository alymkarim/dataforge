import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import type { MLFeatureGroup } from "../types/pipeline";
export function MLFeatureCard({group}:{group:MLFeatureGroup}) {
  return <article className="ml-card">
    <div className="ml-card-head"><div><span className="eyebrow">{group.entity}</span><h3>{group.name}</h3><p>{group.description}</p></div><strong>{group.rows.toLocaleString()} rows</strong></div>
    <div className="feature-tags">{group.features.map(f=><span key={f}>{f}</span>)}</div>
    <div className="ml-checks">{group.checks.map(c=><div key={c.label}>{c.status==="passed"?<CheckCircle2 size={16}/>:c.status==="warning"?<AlertTriangle size={16}/>:<XCircle size={16}/>}<span>{c.label}</span></div>)}</div>
  </article>;
}
