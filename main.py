import argparse, os
from .config import load_config
from .report import Reporter
from .alerts.emailer import send_email
from .logging_utils import upload_log_s3
from .checks.aws_s3 import list_public_buckets
from .checks.aws_ec2 import ec2_ssh_world
from .checks.aws_iam import users_with_admin_and_no_mfa
from .checks.ssl_check import check_ssl_hosts

def run(cfg, do_aws=True, do_gcp=False, do_ssl=True):
    r = Reporter()
    aws_profile = cfg["aws"]["profile"]
    region = cfg["aws"]["region"]

    if do_aws:
        # S3
        try:
            pubs = list_public_buckets(aws_profile, region)
            for b in pubs:
                r.add("HIGH", "AWS:S3", b, f"S3 bucket '{b}' appears PUBLIC")
        except Exception as e:
            r.add("MEDIUM", "AWS:S3", "-", f"S3 check error: {e}")
        # EC2
        try:
            risky = ec2_ssh_world(aws_profile, region)
            for i in risky:
                r.add("HIGH", "AWS:EC2", i, f"EC2 {i} has SSH open to world (0.0.0.0/0 or ::/0)")
        except Exception as e:
            r.add("MEDIUM", "AWS:EC2", "-", f"EC2 check error: {e}")
        # IAM
        try:
            risky_users = users_with_admin_and_no_mfa(aws_profile)
            for uname, _ in risky_users:
                r.add("HIGH", "AWS:IAM", uname, f"IAM user '{uname}' has Admin/FullAccess and NO MFA")
        except Exception as e:
            r.add("MEDIUM", "AWS:IAM", "-", f"IAM check error: {e}")

    if do_ssl and cfg.get("ssl", {}).get("hosts"):
        results = check_ssl_hosts(cfg["ssl"]["hosts"])
        for host, days in results:
            if days == -9999:
                r.add("MEDIUM", "SSL", host, f"Could not check SSL certificate")
            elif days < 0:
                r.add("CRITICAL", "SSL", host, f"SSL certificate EXPIRED {abs(days)} days ago")
            elif days <= 15:
                r.add("HIGH", "SSL", host, f"SSL certificate expires in {days} days")
            else:
                r.add("LOW", "SSL", host, f"SSL certificate OK, {days} days left")

    # Email & logs
    summary = r.summary_text()
    print(summary)

    # Email
    email_cfg = cfg.get("email", {})
    if email_cfg.get("enabled"):
        try:
            send_email(
                email_cfg["smtp_host"],
                int(email_cfg.get("smtp_port", 587)),
                email_cfg["username"],
                email_cfg["password"],
                email_cfg.get("to", []),
                subject="[ShadowEye] Cloud Misconfig Report",
                body=summary
            )
            print(f"📩 Email alert sent to {', '.join(email_cfg.get('to', []))}")
        except Exception as e:
            print(f"Email failed: {e}")

    # Upload logs to S3 (NDJSON)
    from .report import Reporter
    ndjson = Reporter().to_ndjson()  # empty schema container
    # replace with real findings NDJSON
    ndjson = "\n".join([f.replace("\n", " ") for f in summary.splitlines()])
    log_uri = ""
    try:
        log_uri = upload_log_s3(ndjson, cfg["aws"].get("log_bucket",""), cfg["aws"].get("log_prefix","shadoweye/logs/"))
        if log_uri:
            print(f"📝 Log stored at {log_uri}")
    except Exception as e:
        print(f"Log upload failed: {e}")

def main():
    ap = argparse.ArgumentParser(description="ShadowEye – Cloud Misconfiguration Detective")
    ap.add_argument("--all", action="store_true", help="Run all available checks")
    ap.add_argument("--aws", action="store_true", help="Run AWS checks")
    ap.add_argument("--gcp", action="store_true", help="Run GCP checks (placeholder)")
    ap.add_argument("--ssl-only", action="store_true", help="Run SSL checks only")
    ap.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    args = ap.parse_args()

    cfg = load_config(args.config)

    do_aws = args.all or args.aws
    do_gcp = args.all or args.gcp
    do_ssl = args.all or args.ssl_only or (not args.aws and not args.gcp and not args.all)

    run(cfg, do_aws=do_aws, do_gcp=do_gcp, do_ssl=do_ssl)

if __name__ == "__main__":
    main()
