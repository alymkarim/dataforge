import type { DetectedColumn } from "../types/pipeline";
export function SchemaPreview({ rows }: { rows: DetectedColumn[] }) {
  return <div className="table-wrap"><table><thead><tr><th>Column</th><th>Detected type</th><th>Missing</th><th>Sample</th></tr></thead><tbody>
    {rows.map(r=><tr key={r.name}><td><strong>{r.name}</strong></td><td>{r.type}</td><td>{r.missingPercent.toFixed(1)}%</td><td>{r.sample}</td></tr>)}
  </tbody></table></div>;
}
