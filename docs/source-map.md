# Source map and attribution

Based on Kehinde Abiuwa's completed study notes, which use NextWork exercise templates. Original sources remain in the cloud-portfolio repository. The repository brings these exercises together in code and a four-part article series.

## Lecture PDFs

- [Build a Security Monitoring System.pdf](https://github.com/kehindeabiuwa-dotcom/cloud-portfolio/blob/main/STORAGE%2C%20Web%20Hosting%20%26%20SECURITY/Build%20a%20Security%20Monitoring%20System.pdf)
- [Threat Detection with GuardDuty.pdf](https://github.com/kehindeabiuwa-dotcom/cloud-portfolio/blob/main/STORAGE%2C%20Web%20Hosting%20%26%20SECURITY/Threat%20Detection%20with%20GuardDuty.pdf)

## Implementation changes from the notes

- Console configuration becomes a regional CloudFormation stack and runnable tests.
- The secret is generated dummy data. Test scripts suppress its value.
- Corrected the notes' conflicting read/write description: collection includes read management events.
- Successful and denied secret reads have separate metrics and alarms, scoped to all secret reads in this region.
- Alarm notifications are explained as state transitions, not one message per request.
- GuardDuty sample findings validate EventBridge/SNS routing. The vulnerable Juice Shop, credential-exfiltration and malware exercises are not reproduced by this baseline.
- No automated role-deny remediation, Step Functions workflow or malware-protection plan is claimed or deployed.
- Audit bucket retention and deliberate cleanup are explicit.
- New diagrams show intended resources; deployment screenshots and real timings remain to be captured.

## Current technical references

- [GetSecretValue logging](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html)
- [CloudTrail S3 bucket policy](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html)
- [GuardDuty with EventBridge](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings_eventbridge.html)
- [Sample findings and their limits](https://docs.aws.amazon.com/guardduty/latest/ug/sample_findings.html)

- [EventBridge target resource policies](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-use-resource-based.html)

## Extracted screenshots

See the [screenshot gallery](../screenshots/study-notes/README.md) and [page-level provenance](../screenshots/study-notes/sources.json). Screenshots retain their original content and source-page references.
