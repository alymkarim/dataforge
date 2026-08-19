import { StatusBadge } from "./StatusBadge";
export function StageNode({name,layer,rows,description}:{name:string;layer:string;rows:number;description:string}) {
  return <article className={`stage-node ${layer.toLowerCase()}`}><div className="stage-top"><span>{layer}</span><StatusBadge status="Completed"/></div><h3>{name}</h3><p>{description}</p><div className="stage-stats"><span>{rows.toLocaleString()} rows</span><span>Parquet</span></div></article>;
}