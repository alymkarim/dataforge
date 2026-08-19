import { Database, FileText, Rows3, Table2 } from "lucide-react";
import { useEffect, useState } from "react";
import { DatasetSchemaTable } from "../components/DatasetSchemaTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { SectionCard } from "../components/SectionCard";
import { loadDatasetInfo } from "../services/pipelineApi";
import type { DatasetInfo } from "../types/pipeline";

export function DatasetPage(){
 const [dataset,setDataset]=useState<DatasetInfo|null>(null); const [error,setError]=useState("");
 useEffect(()=>{loadDatasetInfo().then(setDataset).catch(e=>setError(e instanceof Error?e.message:"Unable to load dataset"));},[]);
 if(error)return <ErrorState message={error}/>; if(!dataset)return <LoadingState/>;
 return <><PageHeader title="Dataset" description="Source data used to simulate a high-volume ecommerce production event stream."/>
 <div className="metric-grid"><MetricCard label="Records" value={dataset.records.toLocaleString()} detail={dataset.period} icon={Rows3}/><MetricCard label="Columns" value={String(dataset.columns)} detail="Event schema" icon={Table2}/><MetricCard label="Format" value={dataset.format} detail={dataset.estimatedSize} icon={FileText}/><MetricCard label="Source" value={dataset.source} detail={dataset.sourceType} icon={Database}/></div>
 <SectionCard title={dataset.name} subtitle={dataset.description}><div className="dataset-notes"><p><strong>Purpose:</strong> The dataset is the raw source used to demonstrate ingestion, validation, transformation, observability and ML feature generation.</p><p><strong>Why ecommerce?</strong> Event data has timestamps, users, products, sessions, categories and transactions, which makes it ideal for testing realistic data-engineering workflows.</p></div></SectionCard>
 <SectionCard title="Dataset schema" subtitle="Fields expected by the ingestion and Silver validation layers"><DatasetSchemaTable dataset={dataset}/></SectionCard></>;
}
