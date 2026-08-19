import type { DatasetInfo } from "../types/pipeline";
export function DatasetSchemaTable({dataset}:{dataset:DatasetInfo}) {
  return <div className="table-wrap"><table><thead><tr><th>Column</th><th>Type</th><th>Nullable</th><th>Description</th></tr></thead><tbody>
    {dataset.schema.map(col=><tr key={col.name}><td><strong>{col.name}</strong></td><td>{col.type}</td><td>{col.nullable ? "Yes" : "No"}</td><td>{col.description}</td></tr>)}
  </tbody></table></div>;
}
