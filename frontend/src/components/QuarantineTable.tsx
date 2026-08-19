import type { QuarantineRecord } from "../types/pipeline";
export function QuarantineTable({rows}:{rows:QuarantineRecord[]}) {
  return <div className="table-wrap"><table><thead><tr><th>ID</th><th>Reason</th><th>Event time</th><th>Event</th><th>Product</th><th>Price</th><th>Validation details</th></tr></thead><tbody>
  {rows.map(r=><tr key={r.id}><td>{r.id}</td><td><span className="badge failed"><span/>{r.reason}</span></td><td>{r.event_time ?? "NULL"}</td><td>{r.event_type ?? "NULL"}</td><td>{r.product_id ?? "NULL"}</td><td>{r.price == null ? "NULL" : `€${r.price.toFixed(2)}`}</td><td>{r.details.join(" · ")}</td></tr>)}
  </tbody></table></div>;
}
