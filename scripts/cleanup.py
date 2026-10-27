"""Delete lab services; retain the audit bucket until separately reviewed and purged."""
import argparse
import os
from common import aws, outputs
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--stack", default="security-monitoring-lab")
parser.add_argument("--region", required=True)
parser.add_argument("--confirm-stack", required=True)
args = parser.parse_args()
if args.confirm_stack != args.stack:
    parser.error("--confirm-stack must exactly match --stack")
os.environ["AWS_DEFAULT_REGION"] = args.region
os.environ["AWS_REGION"] = args.region
out = outputs(args.stack)
print("Retaining audit bucket:", out["AuditBucketName"])
print("The generated dummy secret is deleted by CloudFormation. Export evidence before continuing.")
aws("cloudformation", "delete-stack", "--stack-name", args.stack)
aws("cloudformation", "wait", "stack-delete-complete", "--stack-name", args.stack)
print("Stack deleted. Retained bucket:", out["AuditBucketName"])
print("Existing GuardDuty detectors were not stack-owned and remain enabled.")
print("See docs/cleanup.md for deliberate removal of retained audit data.")
