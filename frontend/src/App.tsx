import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { OverviewPage } from "./pages/OverviewPage";
import { PipelinePage } from "./pages/PipelinePage";
import { QualityPage } from "./pages/QualityPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { DataExplorerPage } from "./pages/DataExplorerPage";
import { RunsPage } from "./pages/RunsPage";
import { ArchitecturePage } from "./pages/ArchitecturePage";
import { DatasetPage } from "./pages/DatasetPage";
import { DatasetsPage } from "./pages/DatasetsPage";
import { AddDatasetPage } from "./pages/AddDatasetPage";
import { LineagePage } from "./pages/LineagePage";
import { QuarantinePage } from "./pages/QuarantinePage";
import { MLReadinessPage } from "./pages/MLReadinessPage";
import { RunDetailsPage } from "./pages/RunDetailsPage";


export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/datasets" element={<DatasetsPage />} />
        <Route path="/datasets/add" element={<AddDatasetPage />} />
        <Route path="/dataset" element={<DatasetPage />} />
        <Route path="/pipeline" element={<PipelinePage />} />
        <Route path="/lineage" element={<LineagePage />} />
        <Route path="/quality" element={<QualityPage />} />
        <Route path="/quarantine" element={<QuarantinePage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/ml-readiness" element={<MLReadinessPage />} />
        <Route path="/explorer" element={<DataExplorerPage />} />
        <Route path="/runs" element={<RunsPage />} />
        <Route path="/runs/latest" element={<RunDetailsPage />} />
        <Route path="/architecture" element={<ArchitecturePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
        
      </Routes>
    </AppShell>
  );
}
