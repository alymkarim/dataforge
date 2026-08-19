export function StatusBadge({ status }: { status: string }) {
  const cls = status.toLowerCase() === "failed" ? "failed" : status.toLowerCase() === "warning" ? "warning" : "";
  return <span className={`badge ${cls}`}><span />{status}</span>;
}
