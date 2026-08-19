import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell({ children }: { children: ReactNode }) {
  return <div className="app-shell"><Sidebar/><main className="app-main"><Topbar/><div className="content">{children}</div></main></div>;
}
