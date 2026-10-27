"""Generate lab events without printing secret values or temporary credentials."""
import argparse
import json
import os
import subprocess
from common import aws, outputs
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mode", choices=["read", "denied", "guardduty", "status"])
parser.add_argument("--stack", default="security-monitoring-lab")
parser.add_argument("--region", required=True)
args = parser.parse_args()
os.environ["AWS_DEFAULT_REGION"] = args.region
os.environ["AWS_REGION"] = args.region
out = outputs(args.stack)
if args.mode == "read":
    # CLI query suppresses the secret in stdout; response is not logged by this script.
    aws("secretsmanager", "get-secret-value", "--secret-id", out["SecretArn"], "--query", "ARN")
    print("Successful read generated. Allow for CloudTrail delivery and alarm evaluation.")
elif args.mode == "denied":
    credentials = aws("sts", "assume-role", "--role-arn", out["DeniedTestRoleArn"],
                      "--role-session-name", "portfolio-denied-test")["Credentials"]
    env = os.environ.copy()
    env.pop("AWS_PROFILE", None)
    env.pop("AWS_DEFAULT_PROFILE", None)
    env.update(AWS_ACCESS_KEY_ID=credentials["AccessKeyId"],
               AWS_SECRET_ACCESS_KEY=credentials["SecretAccessKey"],
               AWS_SESSION_TOKEN=credentials["SessionToken"])
    result = subprocess.run(["aws", "secretsmanager", "get-secret-value", "--secret-id", out["SecretArn"],
                             "--query", "ARN", "--output", "json", "--no-cli-pager"],
                            capture_output=True, text=True, env=env)
    if result.returncode == 0 or "AccessDenied" not in result.stderr:
        raise SystemExit("Expected AccessDenied was not observed. Check role assumption and endpoint availability.")
    print("Expected AccessDenied generated. No credential or secret value was printed.")
elif args.mode == "guardduty":
    detectors = aws("guardduty", "list-detectors").get("DetectorIds", [])
    if len(detectors) != 1:
        raise SystemExit("Expected one enabled detector in this region. See deployment guide.")
    aws("guardduty", "create-sample-findings", "--detector-id", detectors[0],
        "--finding-types", "Backdoor:EC2/DenialOfService.Tcp")
    print("SAMPLE finding requested. This tests routing, not real threat detection.")
else:
    alarms = aws("cloudwatch", "describe-alarms", "--alarm-names", out["ReadAlarmName"], out["DeniedAlarmName"])
    for alarm in alarms["MetricAlarms"]:
        print(alarm["AlarmName"], alarm["StateValue"], alarm["StateReason"])
    status = aws("cloudtrail", "get-trail-status", "--name", out["TrailName"])
    print("Trail logging:", status.get("IsLogging"))
    for key in ("LatestDeliveryError", "LatestCloudWatchLogsDeliveryError"):
        if status.get(key): print(key, status[key])
