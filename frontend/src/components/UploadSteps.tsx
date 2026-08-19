const labels = ["Upload", "Configure", "Validate", "Process"];
export function UploadSteps({ step }: { step: number }) {
  return <div className="upload-steps">{labels.map((label,i)=><div className={i+1 <= step ? "active" : ""} key={label}><span>{i+1}</span><strong>{label}</strong></div>)}</div>;
}
