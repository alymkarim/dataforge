import type {
  DashboardData,
  DatasetInfo,
  LineageNode,
  QuarantineRecord,
  MLFeatureGroup,
  DetailedPipelineRun,
} from "../types/pipeline";


const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://localhost:8000";


async function getJson<T>(
  path: string,
): Promise<T> {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(
      `Failed to load ${path}`,
    );
  }

  return response.json() as Promise<T>;
}


async function apiRequest<T>(
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
      const body = await response.json();

      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Ignore response parsing errors.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}


/* =========================================================
   DASHBOARD JSON LOADERS
   ========================================================= */

export async function loadDashboardData(): Promise<DashboardData> {
  const [
    summary,
    daily,
    events,
    quality,
    runs,
    products,
  ] = await Promise.all([
    getJson<DashboardData["summary"]>(
      "/demo-data/pipeline-summary.json",
    ),

    getJson<DashboardData["daily"]>(
      "/demo-data/daily-metrics.json",
    ),

    getJson<DashboardData["events"]>(
      "/demo-data/sample-events.json",
    ),

    getJson<DashboardData["quality"]>(
      "/demo-data/quality-results.json",
    ),

    getJson<DashboardData["runs"]>(
      "/demo-data/pipeline-runs.json",
    ),

    getJson<DashboardData["products"]>(
      "/demo-data/product-metrics.json",
    ),
  ]);

  return {
    summary,
    daily,
    events,
    quality,
    runs,
    products,
  };
}


export async function loadDatasetInfo() {
  return getJson<DatasetInfo>(
    "/demo-data/dataset-info.json",
  );
}


export async function loadLineage() {
  return getJson<LineageNode[]>(
    "/demo-data/lineage.json",
  );
}


export async function loadQuarantine() {
  return getJson<QuarantineRecord[]>(
    "/demo-data/quarantine-records.json",
  );
}


export async function loadMLReadiness() {
  return getJson<MLFeatureGroup[]>(
    "/demo-data/ml-readiness.json",
  );
}


export async function loadDetailedRun() {
  return getJson<DetailedPipelineRun>(
    "/demo-data/run-details.json",
  );
}


/* =========================================================
   FASTAPI TYPES
   ========================================================= */

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

  status:
    | "passed"
    | "warning";
}


export interface DatasetRunResult {
  status: string;

  datasetId: string;

  domain: string;

  mode?: string;

  message?: string;

  result?: Record<
    string,
    unknown
  >;
}


/* =========================================================
   FASTAPI ENDPOINTS
   ========================================================= */

export async function getHealth() {
  return apiRequest<{
    status: string;
    service: string;
  }>(
    "/api/health",
  );
}


export async function getDatasets() {
  return apiRequest<
    Array<{
      id: string;
      filename: string;
      format: string;
      sizeBytes: number;
      status: string;
    }>
  >(
    "/api/datasets",
  );
}


export async function uploadDataset(
  file: File,
): Promise<UploadedDataset> {
  const body =
    new FormData();

  body.append(
    "file",
    file,
  );

  return apiRequest<UploadedDataset>(
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
  return apiRequest<DatasetProfile>(
    `/api/datasets/${datasetId}/profile`,
  );
}


export async function validateDataset(
  datasetId: string,
): Promise<ValidationResult> {
  return apiRequest<ValidationResult>(
    `/api/datasets/${datasetId}/validate`,
    {
      method: "POST",
    },
  );
}


export async function runDataset(
  datasetId: string,
  domain: string,
): Promise<DatasetRunResult> {
  return apiRequest<DatasetRunResult>(
    `/api/datasets/${datasetId}/run?domain=${encodeURIComponent(
      domain,
    )}`,
    {
      method: "POST",
    },
  );
}