"""Ask CloudWatch to validate filter semantics using synthetic fixtures; creates no resources."""
import argparse
import json
import os
from common import ROOT, aws
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--region", required=True)
args = parser.parse_args()
os.environ["AWS_DEFAULT_REGION"] = args.region
os.environ["AWS_REGION"] = args.region
template = json.loads((ROOT / "infrastructure/security.json").read_text())
samples = [("successful-read.json", "ReadFilter"), ("denied-read.json", "DeniedFilter")]
for filename, expected_filter in samples:
    message = (ROOT / "tests/fixtures" / filename).read_text()
    for filter_name in ("ReadFilter", "DeniedFilter"):
        pattern = template["Resources"][filter_name]["Properties"]["FilterPattern"]
        result = aws("logs", "test-metric-filter", "--filter-pattern", pattern,
                     "--log-event-messages", json.dumps([message]))
        matched = bool(result.get("matches"))
        if matched != (filter_name == expected_filter):
            raise SystemExit(f"Unexpected match: {filename} -> {filter_name}: {matched}")
print("PASS: successful and denied fixtures match only their intended filters.")
