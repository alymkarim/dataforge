import { Moon, Sun } from "lucide-react";
import { useLocation } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";
import { DatasetSelector } from "./DatasetSelector";

const names: Record<string,string> = {
  "/":"Overview","/datasets":"Datasets","/datasets/add":"Add Dataset","/dataset":"Dataset",
  "/pipeline":"Pipeline","/lineage":"Data Lineage","/quality":"Data Quality","/quarantine":"Quarantine Explorer",
  "/analytics":"Analytics","/ml-readiness":"ML Readiness","/explorer":"Data Explorer","/runs":"Pipeline Runs",
  "/runs/latest":"Run Details","/architecture":"Architecture"
};

export function Topbar() {
  const { pathname } = useLocation();
  const { theme, toggleTheme } = useTheme();
  return <header className="topbar">
    <div><p className="eyebrow">AI DATA INFRASTRUCTURE</p><h1>{names[pathname] ?? "Dashboard"}</h1></div>
    <div className="topbar-actions"><DatasetSelector/><button className="icon-btn" onClick={toggleTheme} aria-label="Toggle theme">{theme==="dark"?<Sun size={18}/>:<Moon size={18}/>}</button></div>
  </header>;
}
