from app.monitoring.kpis import track_kpis

# Simulated logs
logs = [
    {"confidence_score": 0.9, "latency_ms": 420, "tool_error": False},
    {"confidence_score": 0.75, "latency_ms": 370, "tool_error": True, "action": "FLAG_FOR_HUMAN_REVIEW"},
    ...
]

metrics = track_kpis(logs)

print("=== KPI Metrics ===")
for k, v in metrics.items():
    print(f"{k}: {v:.2f}")