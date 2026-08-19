import {
  CheckCircle2,
  Database,
  FileSpreadsheet,
  Play,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  PageHeader,
} from "../components/PageHeader";

import {
  useDataset,
} from "../context/DatasetContext";

import {
  profileDataset,
  runDataset,
  uploadDataset,
  validateDataset,
  type DatasetProfile,
  type UploadedDataset,
  type ValidationResult,
} from "../services/pipelineApi";

import type {
  DatasetDomain,
  ProcessingEngine,
  RegisteredDataset,
} from "../types/pipeline";


type WizardStep =
  | 1
  | 2
  | 3
  | 4;


const STEP_LABELS = [
  "Upload",
  "Configure",
  "Validate",
  "Process",
];


export function AddDatasetPage() {
  const navigate = useNavigate();

  const {
    addDataset,
  } = useDataset();

  const [
    step,
    setStep,
  ] = useState<WizardStep>(1);

  const [
    file,
    setFile,
  ] = useState<File | null>(null);

  const [
    name,
    setName,
  ] = useState("");

  const [
    domain,
    setDomain,
  ] = useState<DatasetDomain>(
    "Generic",
  );

  const [
    engine,
    setEngine,
  ] = useState<ProcessingEngine>(
    "Pandas",
  );

  const [
    uploaded,
    setUploaded,
  ] = useState<UploadedDataset | null>(
    null,
  );

  const [
    profile,
    setProfile,
  ] = useState<DatasetProfile | null>(
    null,
  );

  const [
    validation,
    setValidation,
  ] = useState<ValidationResult | null>(
    null,
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    complete,
    setComplete,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {
    setError("");
  }, [step]);


  const supportsGold =
    domain !== "Generic";

  const supportsML =
    domain !== "Generic";


  const fileSize = useMemo(() => {
    if (!file) {
      return "";
    }

    const mb =
      file.size /
      1024 /
      1024;

    if (mb < 1) {
      return `${(
        file.size /
        1024
      ).toFixed(1)} KB`;
    }

    return `${mb.toFixed(1)} MB`;
  }, [file]);


  function chooseFile(
    nextFile: File,
  ) {
    setFile(
      nextFile,
    );

    setName(
      nextFile.name
        .replace(
          /\.[^.]+$/,
          "",
        )
        .replace(
          /[-_]/g,
          " ",
        ),
    );

    setUploaded(
      null,
    );

    setProfile(
      null,
    );

    setValidation(
      null,
    );

    setComplete(
      false,
    );
  }


  async function uploadAndProfile() {
    if (!file) {
      return;
    }

    try {
      setLoading(
        true,
      );

      setError(
        "",
      );

      const uploadResult =
        await uploadDataset(
          file,
        );

      setUploaded(
        uploadResult,
      );

      const profileResult =
        await profileDataset(
          uploadResult.id,
        );

      setProfile(
        profileResult,
      );

      setStep(
        2,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Upload failed.",
      );
    } finally {
      setLoading(
        false,
      );
    }
  }


  async function runValidation() {
    if (!uploaded) {
      setError(
        "Upload the dataset first.",
      );

      return;
    }

    try {
      setLoading(
        true,
      );

      setError(
        "",
      );

      const result =
        await validateDataset(
          uploaded.id,
        );

      setValidation(
        result,
      );

      setStep(
        3,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Validation failed.",
      );
    } finally {
      setLoading(
        false,
      );
    }
  }


  async function processDataset() {
    if (!file || !uploaded) {
      setError(
        "Dataset has not been uploaded.",
      );

      return;
    }

    try {
      setLoading(
        true,
      );

      setError(
        "",
      );

      const result =
        await runDataset(
          uploaded.id,
          domain,
        );

      const registered:
        RegisteredDataset = {
          id: uploaded.id,

          name:
            name ||
            file.name,

          domain,

          filename:
            file.name,

          format:
            (
              file.name
                .split(".")
                .pop()
                ?.toUpperCase()
            ) || "CSV",

          rows:
            profile?.sampleRows ??
            0,

          columns:
            profile?.columnCount ??
            0,

          size:
            fileSize,

          status:
            "Ready",

          lastProcessed:
            "just now",

          description:
            result.message ??
            `${domain} dataset processed through DataForge.`,

          supportsGold,

          supportsML,
        };

      addDataset(
        registered,
      );

      setComplete(
        true,
      );

      setStep(
        4,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Pipeline execution failed.",
      );
    } finally {
      setLoading(
        false,
      );
    }
  }


  return (
    <>
      <PageHeader
        title="Add dataset"
        description="Upload, profile, validate and process a dataset through the data platform."
      />

      <div className="upload-steps">
        {STEP_LABELS.map(
          (
            label,
            index,
          ) => {
            const number =
              index + 1;

            return (
              <div
                key={label}
                className={
                  number <= step
                    ? "active"
                    : ""
                }
              >
                <span>
                  {number}
                </span>

                <strong>
                  {label}
                </strong>
              </div>
            );
          },
        )}
      </div>

      {error && (
        <div
          className="section-card"
          style={{
            borderColor:
              "var(--danger)",
          }}
        >
          <strong>
            Something went wrong
          </strong>

          <p>
            {error}
          </p>
        </div>
      )}

      <section className="section-card upload-workspace">
        {step === 1 && (
          <>
            <div
              className="upload-dropzone"
              onClick={() => {
                document
                  .getElementById(
                    "dataset-file-input",
                  )
                  ?.click();
              }}
            >
              <input
                id="dataset-file-input"
                type="file"
                accept=".csv,.json,.parquet"
                hidden
                onChange={(event) => {
                  const nextFile =
                    event.target.files?.[0];

                  if (nextFile) {
                    chooseFile(
                      nextFile,
                    );
                  }
                }}
              />

              {file ? (
                <FileSpreadsheet
                  size={42}
                />
              ) : (
                <UploadCloud
                  size={42}
                />
              )}

              <h3>
                {file
                  ? file.name
                  : "Drop dataset here"}
              </h3>

              <p>
                {file
                  ? `${fileSize} · ready to upload`
                  : "CSV · JSON · Parquet"}
              </p>

              <button
                type="button"
                className="primary-btn"
              >
                {file
                  ? "Choose another file"
                  : "Browse files"}
              </button>
            </div>

            <div className="wizard-actions">
              <span />

              <button
                className="primary-btn"
                disabled={
                  !file ||
                  loading
                }
                onClick={
                  uploadAndProfile
                }
              >
                {loading
                  ? "Uploading…"
                  : "Upload & profile →"}
              </button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <div className="validation-header">
              <div>
                <span className="eyebrow">
                  DATASET PROFILE
                </span>

                <h3>
                  {profile?.columnCount ??
                    0}{" "}
                  columns detected
                </h3>

                <p>
                  Profile generated
                  from{" "}
                  {profile?.sampleRows.toLocaleString() ??
                    "0"}{" "}
                  sampled rows.
                </p>
              </div>

              <Database
                size={36}
              />
            </div>

            <div className="form-grid">
              <label>
                <span>
                  Dataset name
                </span>

                <input
                  value={name}
                  onChange={(
                    event,
                  ) =>
                    setName(
                      event.target
                        .value,
                    )
                  }
                />
              </label>

              <label>
                <span>
                  Dataset domain
                </span>

                <select
                  value={domain}
                  onChange={(
                    event,
                  ) =>
                    setDomain(
                      event.target
                        .value as DatasetDomain,
                    )
                  }
                >
                  <option>
                    Generic
                  </option>

                  <option>
                    Retail
                  </option>

                  <option>
                    FinTech
                  </option>

                  <option>
                    Transport
                  </option>

                  <option>
                    IoT
                  </option>
                </select>
              </label>

              <label>
                <span>
                  Processing engine
                </span>

                <select
                  value={engine}
                  onChange={(
                    event,
                  ) =>
                    setEngine(
                      event.target
                        .value as ProcessingEngine,
                    )
                  }
                >
                  <option>
                    Pandas
                  </option>

                  <option>
                    Apache Spark
                  </option>
                </select>
              </label>
            </div>

            {profile && (
              <div
                className="table-wrap"
                style={{
                  marginTop:
                    "20px",
                }}
              >
                <table>
                  <thead>
                    <tr>
                      <th>
                        Column
                      </th>

                      <th>
                        Type
                      </th>

                      <th>
                        Missing
                      </th>

                      <th>
                        Unique
                      </th>

                      <th>
                        Sample
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {profile.schema.map(
                      (column) => (
                        <tr
                          key={
                            column.name
                          }
                        >
                          <td>
                            <strong>
                              {
                                column.name
                              }
                            </strong>
                          </td>

                          <td>
                            {
                              column.type
                            }
                          </td>

                          <td>
                            {
                              column.missingPercent
                            }
                            %
                          </td>

                          <td>
                            {
                              column.uniqueValues
                            }
                          </td>

                          <td>
                            {column.sample ??
                              "—"}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}

            <div className="processing-note">
              <Database
                size={18}
              />

              <p>
                <strong>
                  {domain ===
                  "Generic"
                    ? "Generic processing"
                    : `${domain} processing`}
                </strong>

                <br />

                {domain ===
                "Generic"
                  ? "Bronze, profiling, validation, Silver and quarantine are available. Gold analytics require a supported domain transformer."
                  : "This domain can use the platform's domain-specific Gold and ML feature pipeline."}
              </p>
            </div>

            <div className="wizard-actions">
              <button
                className="secondary-btn"
                onClick={() =>
                  setStep(1)
                }
              >
                ← Back
              </button>

              <button
                className="primary-btn"
                disabled={
                  loading
                }
                onClick={
                  runValidation
                }
              >
                {loading
                  ? "Validating…"
                  : "Validate dataset →"}
              </button>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <div className="validation-header">
              <div>
                <span className="eyebrow">
                  QUALITY CHECK
                </span>

                <h3>
                  {validation?.status ===
                  "passed"
                    ? "Validation passed"
                    : "Validation completed with warnings"}
                </h3>

                <p>
                  {validation?.rowsChecked.toLocaleString() ??
                    0}{" "}
                  sampled records
                  checked.
                </p>
              </div>

              <ShieldCheck
                size={38}
              />
            </div>

            <div className="metric-grid">
              <article className="metric-card">
                <div>
                  <span>
                    Rows checked
                  </span>

                  <strong>
                    {validation?.rowsChecked.toLocaleString() ??
                      0}
                  </strong>
                </div>
              </article>

              <article className="metric-card">
                <div>
                  <span>
                    Columns checked
                  </span>

                  <strong>
                    {validation?.columnsChecked ??
                      0}
                  </strong>
                </div>
              </article>

              <article className="metric-card">
                <div>
                  <span>
                    Quality issues
                  </span>

                  <strong>
                    {validation?.issueCount ??
                      0}
                  </strong>
                </div>
              </article>
            </div>

            {validation &&
              validation.issues
                .length >
                0 && (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>
                          Issue
                        </th>

                        <th>
                          Column
                        </th>

                        <th>
                          Affected rows
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {validation.issues.map(
                        (
                          issue,
                          index,
                        ) => (
                          <tr
                            key={`${issue.type}-${issue.column}-${index}`}
                          >
                            <td>
                              {issue.type
                                .replace(
                                  /_/g,
                                  " ",
                                )
                                .replace(
                                  /\b\w/g,
                                  (
                                    value,
                                  ) =>
                                    value.toUpperCase(),
                                )}
                            </td>

                            <td>
                              {
                                issue.column
                              }
                            </td>

                            <td>
                              {issue.affectedRows.toLocaleString()}
                            </td>
                          </tr>
                        ),
                      )}
                    </tbody>
                  </table>
                </div>
              )}

            <div className="wizard-actions">
              <button
                className="secondary-btn"
                onClick={() =>
                  setStep(2)
                }
              >
                ← Back
              </button>

              <button
                className="primary-btn"
                onClick={() =>
                  setStep(4)
                }
              >
                Configure pipeline →
              </button>
            </div>
          </>
        )}

        {step === 4 &&
          !complete && (
            <>
              <div className="pipeline-config-card">
                <span className="eyebrow">
                  PIPELINE PLAN
                </span>

                <h3>
                  {name}
                </h3>

                <div className="pipeline-plan">
                  <div>
                    <strong>
                      Bronze
                    </strong>

                    <span>
                      Raw immutable
                      ingestion
                    </span>
                  </div>

                  <div>
                    <strong>
                      Silver
                    </strong>

                    <span>
                      Validation and
                      normalization
                    </span>
                  </div>

                  <div
                    className={
                      supportsGold
                        ? ""
                        : "disabled"
                    }
                  >
                    <strong>
                      Gold
                    </strong>

                    <span>
                      {supportsGold
                        ? "Domain analytics and aggregates"
                        : "Requires supported domain"}
                    </span>
                  </div>

                  <div
                    className={
                      supportsML
                        ? ""
                        : "disabled"
                    }
                  >
                    <strong>
                      ML Features
                    </strong>

                    <span>
                      {supportsML
                        ? "Training-ready features"
                        : "Requires supported domain"}
                    </span>
                  </div>
                </div>
              </div>

              {loading && (
                <div className="processing-state">
                  <div className="spinner" />

                  <strong>
                    Processing dataset…
                  </strong>

                  <span>
                    FastAPI → pipeline →
                    outputs
                  </span>
                </div>
              )}

              <div className="wizard-actions">
                <button
                  className="secondary-btn"
                  disabled={
                    loading
                  }
                  onClick={() =>
                    setStep(3)
                  }
                >
                  ← Back
                </button>

                <button
                  className="primary-btn"
                  disabled={
                    loading
                  }
                  onClick={
                    processDataset
                  }
                >
                  <Play
                    size={15}
                  />

                  {loading
                    ? "Running…"
                    : "Run Pipeline"}
                </button>
              </div>
            </>
          )}

        {complete && (
          <div className="complete-state">
            <CheckCircle2
              size={56}
            />

            <span className="eyebrow">
              PIPELINE COMPLETE
            </span>

            <h2>
              {name} is ready
            </h2>

            <p>
              The dataset has been
              uploaded, profiled,
              validated and processed.
            </p>

            <button
              className="primary-btn"
              onClick={() =>
                navigate(
                  "/datasets",
                )
              }
            >
              View Datasets →
            </button>
          </div>
        )}
      </section>
    </>
  );
}