---
title: "Investigating AWS Security Alerts and Preserving the Evidence"
published: false
description: "Use a practical runbook to distinguish authorized access, denied requests and test findings, then clean up the lab deliberately."
tags: "aws, security, cloud, tutorial"
series: "Building an AWS Security Monitoring System"
cover_image: "https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/diagrams/investigation.png"
---

# Investigating AWS Security Alerts and Preserving the Evidence

> **Series:** Building an AWS Security Monitoring System — Part 4 of 4
>
> **Author:** Kehinde Abiuwa

---

An email tells you that something matched a rule. The useful work comes next: identify the caller or resource, understand the activity and decide whether it was expected.

My secret-access exercise and GuardDuty exercise produced different kinds of evidence. A successful secret read, an AccessDenied event and a GuardDuty finding should not all lead to the same conclusion.

---

## What We Are Building in This Part

This part brings the project together with an investigation runbook, a repeatable evidence checklist and a cleanup procedure. The baseline observes and notifies; it does not automatically change permissions or isolate instances.

---

## The Investigation Flow

![Start with the notification, establish context, correlate the evidence and document the decision.](https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/diagrams/investigation.png)
*Start with the notification, establish context, correlate the evidence and document the decision.*

---

## Step 1 — Identify Which Path Triggered the Notification

Determine whether the message came from a secret-read CloudWatch alarm or a GuardDuty finding routed through EventBridge.

| Observation | What it establishes |
|---|---|
| Successful secret read | A caller retrieved the secret; authorization still needs context |
| AccessDenied on GetSecretValue | The request was blocked; it does not prove secret disclosure |
| GuardDuty finding | Activity warrants investigation according to its finding type |
| GuardDuty sample | The event is a test; it can validate routing |

Record account, region, timestamp and the event or finding ID. Do this before jumping to a response action.

---

## Step 2 — Inspect the Supporting Record

For secret access, use the repository query:

```text
fields @timestamp, userIdentity.arn, eventName, sourceIPAddress, errorCode, requestParameters.secretId
| filter eventSource = "secretsmanager.amazonaws.com" and eventName = "GetSecretValue"
| sort @timestamp desc
| limit 50
```

Compare the principal and time with the authorized test or application activity. There is no need to retrieve the secret again to investigate its audit record.

For GuardDuty, inspect finding type, severity and affected resource, as shown in Part 3's screenshot. Correlate with CloudTrail where applicable and follow the investigation guidance for that particular finding.

---

## Step 3 — Check the Monitoring System's Status

```bash
python3 scripts/test_security.py status --region eu-west-2
```

The script reports alarm states and trail delivery errors. Use the results to distinguish a quiet system from one that is failing to collect or deliver events.

Local template validation and regression tests are documented in `docs/validation.md`. They support code review but do not replace live alarm and email verification.

---

## Step 4 — Keep a Small, Useful Evidence Record

For each live test, record:

- The command and time it ran.
- The expected result and actual result.
- The relevant audit event or finding.
- The alarm transition or EventBridge invocation.
- The received notification and observed delay.

The screenshots already included in this series document my earlier console exercises. Put fresh deployment results in `evidence/` with their own dates, rather than treating those earlier screenshots as proof that a new stack worked.

---

## Troubleshooting: A Notification Without Enough Context

If you have an email but cannot identify the original event or test time, record that gap. Do not turn it into a precise latency claim or assume that the caller was malicious.

Similarly, a sample finding should remain labelled as a sample. Its successful delivery is useful evidence for routing, even though it is not evidence of a detected attack.

---

## Step 5 — Export Evidence and Clean Up

```bash
python3 scripts/cleanup.py --region eu-west-2   --confirm-stack security-monitoring-lab
```

The script reports the retained S3 audit bucket. Review its contents before using the separate purge commands in the cleanup guide. The log group and generated dummy secret are removed with the stack, so export anything needed first.

A detector created by this stack is deleted during cleanup. A detector that existed beforehand stays enabled; deleting a lab should not silently disable shared monitoring.

---

## What I Learned

A useful alert needs a traceable explanation: what happened, which identity or resource was involved, what evidence supports the conclusion and what remains uncertain. The runbook gives each test that structure.

---

## What's Next

The next practical step is to deploy the automated version in a sandbox and capture both alert paths end to end. Longer-term extensions could include notification dead-letter handling or a carefully scoped response workflow, each with its own tests and rollback procedure.

[Previous part: From a GuardDuty Finding to an SNS Notification with EventBridge](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/articles/github/03-guardduty-events.md)

---

[Code](https://github.com/kehindeabiuwa-dotcom/aws-security-observability) · [Deployment guide](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/deployment.md) · [Validation record](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/validation.md) · [Sources](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/source-map.md)

*Kehinde Abiuwa — AWS Certified Solutions Architect (Professional) | Microsoft AZ-305*
