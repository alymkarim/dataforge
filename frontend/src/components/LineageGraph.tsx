import { ArrowDown } from "lucide-react";
import type { LineageNode } from "../types/pipeline";
export function LineageGraph({nodes}:{nodes:LineageNode[]}) {
  return <div className="lineage-graph">{nodes.map((node,index)=><div key={node.id}>
    <article className={`lineage-node ${node.layer.toLowerCase()}`}>
      <div><span className="lineage-layer">{node.layer}</span><h3>{node.label}</h3><p>{node.description}</p></div>
      <div className="lineage-meta"><span>{node.path}</span><strong>{node.rows.toLocaleString()} rows</strong></div>
      {node.transformations.length>0 && <ul>{node.transformations.map(t=><li key={t}>{t}</li>)}</ul>}
    </article>
    {index<nodes.length-1 && <div className="lineage-arrow"><ArrowDown size={22}/></div>}
  </div>)}</div>;
}
