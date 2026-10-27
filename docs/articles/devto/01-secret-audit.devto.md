---
title: "Tracking Secret Access on AWS with Secrets Manager and CloudTrail"
published: false
description: "Create a test secret, capture retrieval activity and inspect who accessed it without exposing the secret value."
tags: "aws, security, cloud, tutorial"
series: "Building an AWS Security Monitoring System"
cover_image: "https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/diagrams/architecture.png"
---

# Tracking Secret Access on AWS with Secrets Manager and CloudTrail

> **Series:** Building an AWS Security Monitoring System — Part 1 of 4
>
> **Author:** Kehinde Abiuwa

---

Storing a password in Secrets Manager solves one problem. It does not answer the next question: who retrieved it?

In my monitoring exercise, I created a test secret, accessed it through the console and CLI, and checked the resulting audit activity. This series follows that path from a secret read to a notification, then adds GuardDuty findings and an investigation runbook.

> The screenshots are from my completed console exercises. The repository adds an automated version and repeatable tests. Diagrams show that repository design.

---

## What We Are Building in This Series

| Part | Focus |
|---|---|
| 1 | Store a test secret and capture access with CloudTrail |
| 2 | Turn access events into CloudWatch alarms and SNS notifications |
| 3 | Route GuardDuty findings through EventBridge |
| 4 | Investigate alerts, preserve evidence and clean up |

---

## The Architecture

![The full monitoring design. This part follows secret access into CloudTrail and its log destinations.](https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/diagrams/architecture.png)
*The full monitoring design. This part follows secret access into CloudTrail and its log destinations.*

There are two notification paths. Secret-access events use CloudWatch metric filters and alarms. GuardDuty findings use EventBridge. Both end at SNS, but they are tested separately.

---

## Step 1 — Create a Test Secret

I used a secret named `TopSecretInfo` for the original exercise:

![My test secret's details page, with the secret value still hidden.](https://raw.githubusercontent.com/kehindeabiuwa-dotcom/aws-security-observability/main/screenshots/study-notes/secrets-manager-details.png)
*My test secret's details page, with the secret value still hidden. [Source, p. 3](https://github.com/kehindeabiuwa-dotcom/cloud-portfolio/blob/main/STORAGE%2C%20Web%20Hosting%20%26%20SECURITY/Build%20a%20Security%20Monitoring%20System.pdf#page=3).*

Use dummy data for this exercise. The CloudFormation version generates a separate value automatically rather than putting a password in the template. The test scripts suppress the value in their output.

The screenshot shows the AWS-managed `aws/secretsmanager` encryption key. A customer-managed key introduces additional key-policy and decrypt-permission decisions; it is not necessary for this baseline.

---

## Step 2 — Configure CloudTrail to Capture Reads

The operation to watch is `GetSecretValue`. My notes contain a correction worth keeping: an early section described retrieval as write activity, while the event I later inspected showed `readOnly: true`.

The template collects both read and write management events:

```json
{
  "ReadWriteType": "All",
  "IncludeManagementEvents": true
}
```

A write-only selection would miss the reads this project is intended to monitor. The trail is regional; it is not a multi-account collection service or an S3 object data-event trail.

---

## Step 3 — Send Records to S3 and CloudWatch Logs

The trail has two destinations with different uses:

| Destination | Purpose in the project |
|---|---|
| S3 audit bucket | Retain audit records for later review |
| CloudWatch Logs | Search events and create metric filters |

The template includes the service role and bucket policy required for delivery. The bucket is retained on stack deletion; the cleanup guide explains how to remove it deliberately after reviewing its contents.

To deploy the combined lab:

```bash
export AWS_PROFILE=your-sandbox-profile
python3 scripts/deploy.py --region eu-west-2 --email you@example.com
```

Review the deployment guide first, including permissions and the GuardDuty detector option. Confirm the SNS subscription email before testing notifications in Part 2.

---

## Step 4 — Retrieve the Secret and Inspect the Event

```bash
python3 scripts/test_security.py read --region eu-west-2
python3 scripts/test_security.py status --region eu-west-2
```

The first command generates a retrieval without displaying the value. Open the log group and run `queries/secret-access.logsinsights`.

Inspect `eventName`, `userIdentity`, `sourceIPAddress`, `requestParameters.secretId` and `errorCode`. These fields help establish who made the request, which secret it concerned and whether it succeeded.

---

## Troubleshooting: The Event Is in History but Not in the Log Group

Check the trail's delivery role, log-group configuration and latest delivery errors. Also allow time for delivery. Finding an event in CloudTrail history does not establish that it has already reached CloudWatch Logs.

Changing an alarm threshold cannot fix a missing audit event, so begin at the start of the path.

---

## What I Learned

The audit event supplies the context for an investigation without needing to expose the secret itself. Collection settings matter: if reads are excluded, the rest of the alerting configuration has nothing to match.

---

## What's Next

Next, we build the metric filters and alarms, including the notification problem I worked through in the original exercise.

[Next part: Why My Secret-Access Alert Was Not Firing: CloudWatch and SNS](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/articles/github/02-cloudwatch-alerts.md)

---

[Code](https://github.com/kehindeabiuwa-dotcom/aws-security-observability) · [Deployment guide](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/deployment.md) · [Validation record](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/validation.md) · [Sources](https://github.com/kehindeabiuwa-dotcom/aws-security-observability/blob/main/docs/source-map.md)

*Kehinde Abiuwa — AWS Certified Solutions Architect (Professional) | Microsoft AZ-305*
