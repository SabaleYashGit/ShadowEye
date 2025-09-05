from datetime import datetime
from typing import List, Dict

class Reporter:
    def __init__(self) -> None:
        self.findings: List[Dict] = []

    def add(self, severity: str, service: str, resource: str, message: str) -> None:
        self.findings.append({
            "time": datetime.utcnow().isoformat() + "Z",
            "severity": severity.upper(),
            "service": service,
            "resource": resource,
            "message": message
        })

    def summary_text(self) -> str:
        lines = []
        icon = {"INFO":"ℹ️","LOW":"✅","MEDIUM":"⚠️","HIGH":"❗","CRITICAL":"🚨"}
        for f in self.findings:
            i = icon.get(f["severity"], "•")
            lines.append(f"{i} [{f['service']}] {f['message']} ({f['resource']})")
        if not lines:
            lines.append("✅ No issues found")
        return "\n".join(lines)

    def to_ndjson(self) -> str:
        import json
        return "\n".join([json.dumps(f) for f in self.findings])
