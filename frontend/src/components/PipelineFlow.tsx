import { ArrowRight } from "lucide-react";
import { StageNode } from "./StageNode";
export function PipelineFlow({bronze,silver,gold}:{bronze:number;silver:number;gold:number}) {
 const stages=[["Raw ingestion","bronze",bronze,"Immutable source events"],["Validation","silver",silver,"Schema, duplicates and business rules"],["Feature layer","gold",gold,"Analytics and model-ready features"]] as const;
 return <div className="pipeline-flow">{stages.map((s,i)=><div className="flow-item" key={s[0]}><StageNode name={s[0]} layer={s[1]} rows={s[2]} description={s[3]}/>{i<stages.length-1&&<ArrowRight className="flow-arrow"/>}</div>)}</div>;
}