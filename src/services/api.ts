const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://localhost:8000";


export interface UploadedDataset {
  id: string;
  filename: string;
  storedAs: string;
  sizeBytes: number;
  status: string;
}


export interface DatasetColumn {
  name: string;
  type: string;
  missingPercent: number;
  uniqueValues: number;
  sample: string | null;
}


export interface DatasetProfile {
  datasetId: string;
  filename: string;
  sampleRows: number;
  columnCount: number;
  schema: DatasetColumn[];
}


export interface ValidationIssue {
  type: string;
  column: string;
  affectedRows: number;
}


export interface ValidationResult {
  datasetId: string;
  rowsChecked: number;
  columnsChecked: number;
  issueCount: number;
  issues: ValidationIssue[];
  status: "passed" | "warning";
}


async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_URL}${path}`,
    options,
  );

  if (!response.ok) {
    let message =
      `Request failed: ${response.status}`;

    try {
      const error = await response.json();

      if (error.detail) {
        message = error.detail;
      }
    } catch {
      // Ignore invalid JSON errors.
    }

    throw new Error(message);
  }

  return response.json();
}


export async function getHealth() {
  return request<{
    status: string;
    service: string;
  }>("/api/health");
}


export async function getDatasets() {
  return request<
    Array<{
      id: string;
      filename: string;
      format: string;
      sizeBytes: number;
      status: string;
    }>
  >("/api/datasets");
}


export async function uploadDataset(
  file: File,
): Promise<UploadedDataset> {
  const body = new FormData();

  body.append("file", file);

  return request<UploadedDataset>(
    "/api/datasets/upload",
    {
      method: "POST",
      body,
    },
  );
}


export async function profileDataset(
  datasetId: string,
): Promise<DatasetProfile> {
  return request<DatasetProfile>(
    `/api/datasets/${datasetId}/profile`,
  );
}


export async function validateDataset(
  datasetId: string,
): Promise<ValidationResult> {
  return request<ValidationResult>(
    `/api/datasets/${datasetId}/validate`,
    {
      method: "POST",
    },
  );
}


export async function runPipeline() {
  return request<{
    status: string;
    result: Record<string, unknown>;
  }>(
    "/api/pipeline/run",
    {
      method: "POST",
    },
  );
}