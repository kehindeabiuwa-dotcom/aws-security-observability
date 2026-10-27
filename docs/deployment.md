# Deploy and validate the two alert paths

## Prerequisites and permissions

Use AWS CLI v2, Python 3.9+, and a dedicated sandbox account in a commercial AWS region. The operator needs CloudFormation and creation/deletion permissions for IAM roles, CloudTrail, CloudWatch Logs/alarms, S3, SNS, EventBridge, Secrets Manager and optionally GuardDuty. Also allow `iam:PassRole`, `guardduty:ListDetectors`, `guardduty:CreateSampleFindings`, reads of the stack's dummy secret, and `sts:AssumeRole` on the stack's DeniedTestRole. Organization policies may further restrict these actions.

The denied-test role trusts principals from this account only when their identity policy also permits AssumeRole. Its sole secret-access policy explicitly denies reading the generated dummy secret.

```bash
export AWS_PROFILE=your-sandbox-profile
export AWS_DEFAULT_REGION=eu-west-2
aws sts get-caller-identity
aws guardduty list-detectors
python3 scripts/deploy.py --region "$AWS_DEFAULT_REGION" --email you@example.com
```

If no detector exists and you want this stack to create one, add `--create-detector`. Do not create a second detector in a region that already has one. On later deployments, the script recognizes a detector owned by this stack and preserves that choice automatically, even if the flag is omitted. An existing detector outside this stack is not modified. Deliberately removing a stack-owned detector is a separate CloudFormation change or part of cleanup.

CloudFormation can complete while SNS is still awaiting email confirmation. Confirm the subscription before testing. Verify Trail logging status with the status command.

## Successful read

```bash
python3 scripts/test_security.py read --region "$AWS_DEFAULT_REGION"
python3 scripts/test_security.py status --region "$AWS_DEFAULT_REGION"
```

The script suppresses secret values. CloudTrail delivers the event asynchronously; there is no guaranteed one-minute end-to-end alert latency. Search the log group with `queries/secret-access.logsinsights`; verify the matching metric; then check alarm history and the email.

## Denied read

```bash
python3 scripts/test_security.py denied --region "$AWS_DEFAULT_REGION"
```

This assumes the dedicated role using temporary credentials in subprocess memory and verifies AccessDenied. It does not print credentials. Expect a separate DeniedSecretReads metric and alarm. A failure to assume the role is not the intended secret-access event; grant the operator the scoped AssumeRole permission first.

## GuardDuty sample

```bash
python3 scripts/test_security.py guardduty --region "$AWS_DEFAULT_REGION"
```

Expect a finding labeled `[SAMPLE]`, a matching EventBridge rule invocation and an SNS email. The SNS body contains the finding event JSON. Keep the sample marker visible in evidence. This proves event delivery only; the vulnerable-app exploitation and malware exercises from the notes are not deployed by this baseline.

## Alert behavior

CloudWatch alarms notify on state transitions. A second read while an alarm is already ALARM does not necessarily produce another email. Allow the alarm to return to OK, then generate a new event. Delivery lag, metric timestamps and alarm period can affect observations; inspect logs and history before declaring failure.

Both filters cover all Secrets Manager GetSecretValue calls in the deployment region. The trail records all regional management events, not S3 object data events. This is intentionally a sandbox scope. Narrow the filter by resource/identity before adapting it to a busy environment.

## Evidence

Capture a redacted log event, metric datapoint, alarm transition, email timestamp and GuardDuty sample. Measure observed delays; do not write an invented latency. Record failures and fixes in the evidence folder.

## Optional service-side filter check

```bash
python3 scripts/test_filters.py --region eu-west-2
```

This invokes the read-only `logs:TestMetricFilter` API with the synthetic fixtures under `tests/fixtures/`. It checks both positive and negative matches without deploying resources. It requires AWS credentials and that API permission.
