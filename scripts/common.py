"""Standard-library helpers. Requires AWS CLI v2; never reads credentials directly."""
import json
import os
import subprocess
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def aws(*args, env=None):
    result = subprocess.run(["aws", *map(str, args), "--output", "json", "--no-cli-pager"],
                            text=True, capture_output=True, env=env)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else {}

def outputs(stack):
    stacks = aws("cloudformation", "describe-stacks", "--stack-name", stack)["Stacks"]
    return {x["OutputKey"]: x["OutputValue"] for x in stacks[0].get("Outputs", [])}

def run_command(instance, commands):
    response = aws("ssm", "send-command", "--instance-ids", instance,
                   "--document-name", "AWS-RunShellScript", "--parameters",
                   json.dumps({"commands": ["set -eu", *commands], "executionTimeout": ["120"]}))
    command_id = response["Command"]["CommandId"]
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            result = aws("ssm", "get-command-invocation", "--command-id", command_id,
                         "--instance-id", instance)
        except RuntimeError as exc:
            if "InvocationDoesNotExist" not in str(exc):
                raise
            time.sleep(2)
            continue
        status = result["Status"]
        if status == "Success":
            print(result.get("StandardOutputContent", "").strip())
            return result
        if status not in ("Pending", "InProgress", "Delayed", "Cancelling"):
            raise RuntimeError(f"SSM {status}: {result.get('StandardErrorContent', '')}")
        time.sleep(3)
    raise TimeoutError("SSM command did not finish within 180 seconds")
