"""Deploy this lab using the configured AWS CLI identity and explicit region."""
import argparse
import os
import subprocess
from common import ROOT, aws, outputs
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--stack", default="security-monitoring-lab")
parser.add_argument("--region", required=True)

parser.add_argument("--email", required=True)
parser.add_argument("--create-detector", action="store_true")

args = parser.parse_args()
os.environ["AWS_DEFAULT_REGION"] = args.region
os.environ["AWS_REGION"] = args.region
identity = aws("sts", "get-caller-identity")
print("Deploying to account", identity["Account"], "region", args.region, "stack", args.stack)
command = ["aws", "cloudformation", "deploy", "--template-file", str(ROOT / "infrastructure/security.json"),
           "--stack-name", args.stack, "--capabilities", "CAPABILITY_IAM", "--no-fail-on-empty-changeset",
           "--region", args.region, "--no-cli-pager"]

detectors = aws("guardduty", "list-detectors").get("DetectorIds", [])
try:
    existing = outputs(args.stack)
except RuntimeError as exc:
    if "does not exist" not in str(exc):
        raise
    existing = {}
owned_detector = existing.get("DetectorId")
create_detector = args.create_detector or bool(owned_detector)
if create_detector and detectors and owned_detector not in detectors:
    parser.error("A detector exists outside this stack. Re-run without --create-detector.")
if not create_detector and not detectors:
    print("GuardDuty is not enabled here; the audit path works, but finding delivery requires a detector.")
if owned_detector:
    print("Preserving this stack's existing GuardDuty detector on update.")
command += ["--parameter-overrides", "AlertEmail=" + args.email,
            "CreateGuardDutyDetector=" + ("true" if create_detector else "false")]
subprocess.run(command, check=True)
print("Deployment completed. Follow docs/deployment.md for verification.")
