# Investigate a notification

1. Identify the path: CloudWatch alarm for successful/denied secret reads, or a GuardDuty finding routed by EventBridge.
2. Record account, region, event/finding ID and UTC timestamp. If `[SAMPLE]` or `service.additionalInfo.sample` is present, classify it as a test.
3. For secret access, inspect eventName, userIdentity, sourceIPAddress, requestParameters.secretId and errorCode. Do not retrieve the secret to investigate the audit event.
4. Compare the principal and time with the authorized test or application activity. A successful read is an observation, not proof of compromise; a denied request does not prove data was exposed.
5. For GuardDuty, inspect finding type, severity, affected resource and recommended AWS investigation steps. Correlate with CloudTrail where applicable.
6. Preserve sanitized evidence. Record the hypothesis, supporting observations, uncertainties and decision.
7. In a real incident, follow your organization's incident process. Any credential revocation, role-policy change or instance isolation must target the confirmed affected resource and have a rollback plan. This repository performs no automatic containment.
8. Close the exercise with verified result, observed latency, false-positive considerations and cleanup status.

## Scope and next steps

GuardDuty sample events test routing, not the effectiveness of threat detection. This baseline has no central multi-account collection, automatic containment, malware-protection plan, immutable archive or dedicated notification dead-letter queue. Those are explicit future extensions. Do not label it a complete SOC or compliance platform.
