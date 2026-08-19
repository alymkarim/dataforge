export interface PipelineSummary {
  pipelineStatus: string;
  lastRun: string;
  durationSeconds: number;
  bronzeRows: number;
  silverRows: number;
  goldRows: number;
  rejectedRows: number;
  qualityScore: number;
}

export interface DailyMetric {
  date: string;
  revenue: number;
  purchases: number;
  activeUsers: number;
  conversionRate: number;
  views: number;
  carts: number;
}

export interface EventRecord {
  event_time: string;
  event_type: string;
  product_id: number;
  category_code: string | null;
  brand: string | null;
  price: number;
  user_id: number;
  user_session: string;
}

export interface QualityCheck {
  check: string;
  column: string;
  status: "passed" | "warning" | "failed";
  affectedRows: number;
  description: string;
}

export interface PipelineRun {
  id: string;
  startedAt: string;
  duration: string;
  rows: number;
  status: "Completed" | "Failed" | "Running";
}

export interface ProductMetric {
  productId: number;
  brand: string;
  category: string;
  views: number;
  carts: number;
  purchases: number;
  revenue: number;
  conversionRate: number;
}

export interface DashboardData {
  summary: PipelineSummary;
  daily: DailyMetric[];
  events: EventRecord[];
  quality: QualityCheck[];
  runs: PipelineRun[];
  products: ProductMetric[];
}


export interface DatasetInfo {
  name: string;
  source: string;
  sourceType: string;
  records: number;
  period: string;
  format: string;
  estimatedSize: string;
  columns: number;
  description: string;
  schema: {
    name: string;
    type: string;
    nullable: boolean;
    description: string;
  }[];
}

export interface LineageNode {
  id: string;
  label: string;
  layer: string;
  path: string;
  rows: number;
  description: string;
  transformations: string[];
}

export interface QuarantineRecord {
  id: string;
  reason: string;
  event_time: string | null;
  event_type: string | null;
  product_id: number | null;
  price: number | null;
  user_id: number | null;
  details: string[];
}

export interface MLFeatureGroup {
  name: string;
  description: string;
  entity: string;
  features: string[];
  rows: number;
  checks: {
    label: string;
    status: "passed" | "warning" | "failed";
  }[];
}

export interface RunStage {
  name: string;
  durationSeconds: number;
  status: "Completed" | "Failed" | "Running";
  inputRows: number;
  outputRows: number;
}

export interface DetailedPipelineRun {
  id: string;
  startedAt: string;
  finishedAt: string;
  durationSeconds: number;
  rowsPerSecond: number;
  status: "Completed" | "Failed" | "Running";
  stages: RunStage[];
}


export type DatasetStatus = "Ready" | "Uploaded" | "Processing" | "Failed";
export type DatasetDomain = "Retail" | "FinTech" | "Transport" | "IoT" | "Generic";
export type ProcessingEngine = "Pandas" | "Apache Spark";

export interface RegisteredDataset {
  id: string;
  name: string;
  domain: DatasetDomain;
  filename: string;
  format: string;
  rows: number;
  columns: number;
  size: string;
  status: DatasetStatus;
  lastProcessed: string | null;
  description: string;
  supportsGold: boolean;
  supportsML: boolean;
}

export interface DetectedColumn {
  name: string;
  type: string;
  missingPercent: number;
  sample: string;
}

export interface DatasetUploadDraft {
  name: string;
  filename: string;
  domain: DatasetDomain;
  format: string;
  engine: ProcessingEngine;
  deduplicate: boolean;
  validateTypes: boolean;
  handleMissing: boolean;
  quarantineInvalid: boolean;
  generateQualityReport: boolean;
}
