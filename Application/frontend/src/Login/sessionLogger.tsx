// utils/sessionLogger.ts
export interface SessionLog {
  user_id: number;
  email: string;
  action: "login" | "logout" | "force-logout";
  timestamp: string;
}

export function addSessionLog(log: SessionLog) {
  try {
    const logs: SessionLog[] = JSON.parse(localStorage.getItem("sessionLogs") || "[]");

    logs.push(log);

    // Keep only last 500 entries
    const trimmed = logs.slice(-500);
    localStorage.setItem("sessionLogs", JSON.stringify(trimmed));
  } catch (e) {
    console.error("Failed to write session log:", e);
  }
}

export function getSessionLogs(): SessionLog[] {
  try {
    return JSON.parse(localStorage.getItem("sessionLogs") || "[]");
  } catch {
    return [];
  }
}
