import os, io, boto3
from datetime import datetime

def upload_log_s3(text: str, bucket: str, prefix: str = "shadoweye/logs/") -> str:
    if not bucket:
        return ""
    key = f"{prefix}incident_{datetime.utcnow().strftime('%Y_%m_%dT%H%M%SZ')}.ndjson"
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))
    return f"s3://{bucket}/{key}"
