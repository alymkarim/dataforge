import type { DetailedPipelineRun } from "../types/pipeline";
import { StatusBadge } from "./StatusBadge";
export function RunStageBreakdown({run}:{run:DetailedPipelineRun}) {
  return <div className="run-details">
    <div className="run-summary-grid">
      <div><span>Status</span><StatusBadge status={run.status}/></div>
      <div><span>Duration</span><strong>{run.durationSeconds.toFixed(1)}s</strong></div>
      <div><span>Throughput</span><strong>{run.rowsPerSecond.toLocaleString()} rows/s</strong></div>
      <div><span>Started</span><strong>{run.startedAt}</strong></div>
    </div>
    <div className="stage-breakdown">
      {run.stages.map((stage,index)=><div className="run-stage" key={stage.name}>
        <div className="stage-index">{String(index+1).padStart(2,"0")}</div>
        <div className="stage-body"><div className="stage-title"><strong>{stage.name}</strong><StatusBadge status={stage.status}/></div>
        <div className="stage-bar"><span style={{width:`${Math.min(100,Math.max(7,stage.durationSeconds/run.durationSeconds*100))}%`}}/></div>
        <div className="stage-foot"><span>{stage.durationSeconds.toFixed(1)}s</span><span>{stage.inputRows.toLocaleString()} → {stage.outputRows.toLocaleString()} rows</span></div></div>
      </div>)}
    </div>
  </div>;
}
