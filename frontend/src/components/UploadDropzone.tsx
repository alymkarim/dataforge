import { UploadCloud, FileSpreadsheet } from "lucide-react";
import { useRef } from "react";

export function UploadDropzone({ filename, onFile }: { filename: string; onFile: (file: File) => void }) {
  const ref = useRef<HTMLInputElement>(null);
  return (
    <div className="upload-dropzone" onClick={() => ref.current?.click()}>
      <input ref={ref} type="file" accept=".csv,.json,.parquet" hidden onChange={e => e.target.files?.[0] && onFile(e.target.files[0])}/>
      {filename ? <FileSpreadsheet size={36}/> : <UploadCloud size={38}/>}
      <h3>{filename || "Drop dataset here"}</h3>
      <p>{filename ? "File selected. Continue to inspect its schema." : "CSV · JSON · Parquet"}</p>
      <button type="button" className="primary-btn">{filename ? "Choose another file" : "Browse files"}</button>
    </div>
  );
}
