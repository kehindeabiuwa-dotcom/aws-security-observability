# Costs, retention and cleanup

Budget for a generated Secrets Manager secret, CloudWatch log ingestion/storage and alarms, CloudTrail logging where applicable, S3 storage/requests, SNS and GuardDuty if enabled. A new trail can duplicate billable collection where other trails already exist. Check [AWS Pricing Calculator](https://calculator.aws/), [CloudTrail pricing](https://aws.amazon.com/cloudtrail/pricing/) and [GuardDuty pricing](https://aws.amazon.com/guardduty/pricing/) for your region and enabled protection plans.

The audit bucket expires lab objects after 30 days and is **retained** when the stack is deleted. CloudWatch logs have 14-day retention while the stack exists; the log group is deleted with the stack. The generated dummy secret is deleted by CloudFormation (do not put real credentials in it). Export needed evidence first.

```bash
python3 scripts/cleanup.py --region eu-west-2 --confirm-stack security-monitoring-lab
```

Record the retained bucket name printed by the script. The stack-owned detector, if created, is deleted; an existing detector outside the stack remains enabled and can continue incurring charges. The stack does not change organization-managed settings.

After reviewing retained data and confirming the exact lab bucket name, deliberately purge it:

```bash
# Replace only with the retained bucket from this lab's cleanup output.
AUDIT_BUCKET=your-retained-lab-bucket
aws s3 rm "s3://$AUDIT_BUCKET" --recursive
aws s3api delete-bucket --bucket "$AUDIT_BUCKET" --region eu-west-2
```

The bucket is unversioned, so these commands remove its objects and bucket. Check that the trail, alarms, rule, topic, test role, secret and log group are gone. Review any pre-existing detector separately; do not disable shared security monitoring merely to finish this lab.
