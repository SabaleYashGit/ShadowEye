# ShadowEye – Cloud Misconfiguration Detective

Automated Python tool that scans for common AWS/GCP misconfigurations, generates a human-friendly incident report, emails alerts, and stores logs to S3.

## Key Checks (MVP)
- AWS: Public S3 buckets
- AWS: EC2 SSH open to the world (0.0.0.0/0 or ::/0)
- AWS: IAM users with admin/full access and **no MFA**
- SSL certificate expiry for configured hostnames
- (Hooks in place for GCP; add service account & enable APIs to extend)

## Quick Start
```bash
# 1) Create & activate venv (optional)
python3 -m venv .venv && source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Configure credentials
#    - AWS: export AWS_PROFILE=<profile> or use env keys
#    - Email: set in config.yaml (use app password)
#    - S3 log bucket: create and put name in config.yaml

# 4) Edit config.yaml as needed
# 5) Run a scan
python -m shadoweye.main --all
# or selective scans
python -m shadoweye.main --aws --ssl-only
```

## Config
See `config.yaml` for knobs. Example:
```yaml
aws:
  profile: default
  region: ap-south-1
  log_bucket: your-log-bucket
  log_prefix: shadoweye/logs/
email:
  enabled: true
  smtp_host: smtp.gmail.com
  smtp_port: 587
  username: cloud-admin@example.com
  password: "APP_PASSWORD_HERE"
  to: ["cloud-admin@example.com"]
ssl:
  hosts:
    - example.com
    - api.example.com
gcp:
  enabled: false
  project_id: your-project
  # add service account auth if enabling
```

## Output
Sample console/report style:
```
✅ IAM user 'backup' is secure
⚠️ EC2 i-0xabc has SSH open to public (0.0.0.0:22)
⚠️ S3 bucket 'user-data-prod' is public
📩 Email alert sent to cloud-admin@example.com
📝 Log stored at s3://cloudeye/logs/incident_2025_06_30.txt
```

## Notes
- Use least-privilege on AWS creds; **read-only** where possible.
- For Gmail SMTP, use an App Password (not your main password).
- Extend GCP checks in `shadoweye/checks/gcp_storage.py` (placeholder included).
- This project is educational; review before production use.
