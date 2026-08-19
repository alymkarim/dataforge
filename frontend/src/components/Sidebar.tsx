import { NavLink } from "react-router-dom";
import {
  Activity,
  BarChart3,
  BrainCircuit,
  Database,
  GitBranch,
  Layers3,
  Network,
  ShieldCheck,
  TableProperties,
  Trash2,
  Workflow,
} from "lucide-react";

const groups = [
  {
    label: "DATA",
    links: [
      ["/datasets", "Datasets", Database],
      ["/explorer", "Data Explorer", TableProperties],
      ["/quarantine", "Quarantine", Trash2],
    ],
  },
  {
    label: "PIPELINES",
    links: [
      ["/pipeline", "Pipeline", GitBranch],
      ["/runs", "Pipeline Runs", Layers3],
      ["/lineage", "Data Lineage", Workflow],
      ["/quality", "Data Quality", ShieldCheck],
    ],
  },
  {
    label: "INSIGHTS",
    links: [
      ["/analytics", "Analytics", BarChart3],
      ["/ml-readiness", "ML Readiness", BrainCircuit],
    ],
  },
  {
    label: "PLATFORM",
    links: [
      ["/architecture", "Architecture", Network],
    ],
  },
] as const;

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <Layers3 size={25} />

        <div>
          <strong>DataForge</strong>
          <span>AI Data Platform</span>
        </div>
      </div>

      <NavLink
        to="/"
        end
        className={({ isActive }) =>
          `nav-link ${isActive ? "active" : ""}`
        }
      >
        <Activity size={18} />
        <span>Overview</span>
      </NavLink>

      <nav className="grouped-nav">
        {groups.map((group) => (
          <div className="nav-group" key={group.label}>
            <small>{group.label}</small>

            {group.links.map(([to, label, Icon]) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `nav-link ${isActive ? "active" : ""}`
                }
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-foot">
        <span className="pulse" />
        Platform healthy
      </div>
    </aside>
  );
}