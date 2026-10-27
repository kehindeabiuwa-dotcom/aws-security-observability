---
title: "Why My Secret-Access Alert Was Not Firing: CloudWatch and SNS"
published: false
description: "Build event counters and alarms, confirm SNS delivery and troubleshoot the path from a secret read to an email."
tags: "aws, security, cloud, tutorial"
series: "Building an AWS Security Monitoring System"
cover_image: "https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/diagrams/alert-validation.png"
---

# Why My Secret-Access Alert Was Not Firing: CloudWatch and SNS

> **Series:** Building an AWS Security Monitoring System — Part 2 of 4
>
> **Author:** Kehinde Abiuwa

---

I retrieved my test secret and expected an email. Nothing arrived.

That was the point where the monitoring exercise became useful. I had to trace the event through CloudTrail, CloudWatch Logs, the metric filter, the alarm and the SNS subscription instead of assuming the problem was email delivery.

---

## What We Are Building in This Part

The repository has separate counters for successful and denied `GetSecretValue` calls. Each counter has an alarm that notifies the same SNS topic. Separating the two makes it easier to distinguish an actual retrieval from a blocked request.

---

## The Architecture

![Follow the event through each stage before changing the next one.](https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/diagrams/alert-validation.png)
*Follow the event through each stage before changing the next one.*

---

## Step 1 — Match the Secret-Access Event

The successful-read filter matches Secrets Manager, the `GetSecretValue` operation and the absence of an error:

```text
{ ($.eventSource = "secretsmanager.amazonaws.com") && ($.eventName = "GetSecretValue") && ($.errorCode NOT EXISTS) }
```

The denied-read filter matches the same operation with an AccessDenied error. The filters apply to secret reads across the deployment region, which is why the guide uses a sandbox account.

To check the patterns against the supplied fixtures using AWS's read-only test API:

```bash
python3 scripts/test_filters.py --region eu-west-2
```

This checks matching behavior; it does not generate a live access event or prove notification delivery.

---

## Step 2 — Publish a Count for Each Match

In the console, I configured a metric value of `1` and a default of `0`:

![Configuring the metric value and default value for my secret-access counter.](https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/screenshots/study-notes/metric-filter-value.png)
*Configuring the metric value and default value for my secret-access counter. [Source, p. 7](https://github.com/kehindeabiuwa-dotcom/cloud-portfolio/blob/main/STORAGE%2C%20Web%20Hosting%20%26%20SECURITY/Build%20a%20Security%20Monitoring%20System.pdf#page=7).*

Each matching event contributes one to the counter. The new template uses separate metric names for successful and denied reads. Metric filters process newly arriving events; they do not backfill the log group's history.

---

## Step 3 — Create the Alarm and Confirm the Subscriber

| Setting | Repository value | Reason |
|---|---|---|
| Statistic | Sum | Count matching events in the period |
| Period | 60 seconds | Evaluate short windows |
| Threshold | Greater than or equal to 1 | Flag at least one matching event |
| Evaluation periods | 1 | Use one evaluated period |
| Missing data | Not breaching | Missing data alone should not trigger this alarm |

SNS email subscriptions require confirmation. CloudFormation can finish creating the topic while the subscriber is still pending confirmation.

---

## Step 4 — Generate Successful and Denied Reads

```bash
python3 scripts/test_security.py read --region eu-west-2
python3 scripts/test_security.py denied --region eu-west-2
python3 scripts/test_security.py status --region eu-west-2
```

The denied test assumes a dedicated role that explicitly denies access to the dummy secret. The operator must have permission to assume that role. If AssumeRole fails, the intended `GetSecretValue` test has not happened yet.

---

## The Problem I Hit: No Notification After Reading the Secret

In my exercise, I checked that the event existed, the log group was receiving data and the SNS subscription was confirmed. I then changed the alarm from Average over five minutes to Sum over one minute and checked its SNS action.

After retesting, the alarm entered ALARM and I received the notification recorded in my notes:

![The secret-access alarm in ALARM after I retested the original monitoring setup.](https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/screenshots/study-notes/secret-access-alarm.png)
*The secret-access alarm in ALARM after I retested the original monitoring setup. [Source, p. 1](https://github.com/kehindeabiuwa-dotcom/cloud-portfolio/blob/main/STORAGE%2C%20Web%20Hosting%20%26%20SECURITY/Build%20a%20Security%20Monitoring%20System.pdf#page=1).*

Sum matches the goal here: count accesses. The configuration change and subsequent result are the useful evidence; the alarm screenshot alone does not explain every possible cause of a missing email.

---

## What I Learned

An alarm notification is tied to a state transition. Another read while the alarm is already ALARM may not send another email. Wait for it to return to OK before testing a fresh transition.

A one-minute period also does not promise a one-minute end-to-end alert. CloudTrail delivery and ingestion happen before evaluation. Record observed times rather than assuming the period equals total latency.

---

## What's Next

Next, we add GuardDuty findings through EventBridge. That path uses the same notification topic but bypasses these secret-read filters and alarms.

[Previous part: Tracking Secret Access on AWS with Secrets Manager and CloudTrail](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/articles/github/01-secret-audit.md) · [Next part: From a GuardDuty Finding to an SNS Notification with EventBridge](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/articles/github/03-guardduty-events.md)

---

[Code](https://github.com/kehindeabiuwa-dotcom/aws-security-observability) · [Deployment guide](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/deployment.md) · [Validation record](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/validation.md) · [Sources](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/source-map.md)

*Kehinde Abiuwa — AWS Certified Solutions Architect (Professional) | Microsoft AZ-305*
