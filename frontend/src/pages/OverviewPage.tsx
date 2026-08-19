import { Activity, Database, ShieldCheck, Sparkles } from "lucide-react";
import { useDashboardData } from "../hooks/useDashboardData";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { PipelineFlow } from "../components/PipelineFlow";
import { QualityScore } from "../components/QualityScore";
import { RevenueChart } from "../components/RevenueChart";
import { SectionCard } from "../components/SectionCard";
import { money, number } from "../utils/format";

export function OverviewPage(){
 const {data,loading,error}=useDashboardData();
 if(loading)return <LoadingState/>; if(error||!data)return <ErrorState message={error}/>;
 const revenue=data.daily.reduce((s,d)=>s+d.revenue,0);
 return <><PageHeader title="Platform overview" description="Operational view of ingestion, transformation, validation and analytics readiness."/>
 <div className="metric-grid">
 <MetricCard label="Bronze rows" value={number(data.summary.bronzeRows)} detail="Raw source events" icon={Database}/>
 <MetricCard label="Silver rows" value={number(data.summary.silverRows)} detail={`${data.summary.rejectedRows} quarantined`} icon={ShieldCheck}/>
 <MetricCard label="Gold rows" value={number(data.summary.goldRows)} detail="Model-ready aggregates" icon={Sparkles}/>
 <MetricCard label="Revenue represented" value={money(revenue)} detail="Demo Gold layer" icon={Activity}/>
 </div>
 <SectionCard title="Medallion pipeline" subtitle="Trace data from immutable ingestion to analytics-ready features"><PipelineFlow bronze={data.summary.bronzeRows} silver={data.summary.silverRows} gold={data.summary.goldRows}/></SectionCard>
 <div className="two-col"><SectionCard title="Revenue trend" subtitle="Daily Gold-layer revenue"><RevenueChart data={data.daily}/></SectionCard><SectionCard title="Data quality" subtitle="Latest validation run"><QualityScore score={data.summary.qualityScore}/><div className="quality-summary"><div><span>Status</span><strong>{data.summary.pipelineStatus}</strong></div><div><span>Duration</span><strong>{data.summary.durationSeconds}s</strong></div><div><span>Rejected</span><strong>{data.summary.rejectedRows}</strong></div></div></SectionCard></div></>;
}