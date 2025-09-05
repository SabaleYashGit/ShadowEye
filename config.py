import os, yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    # env overrides (optional)
    cfg.setdefault("aws", {})
    cfg["aws"].setdefault("profile", os.getenv("AWS_PROFILE", "default"))
    cfg["aws"].setdefault("region", os.getenv("AWS_REGION", "ap-south-1"))
    return cfg
