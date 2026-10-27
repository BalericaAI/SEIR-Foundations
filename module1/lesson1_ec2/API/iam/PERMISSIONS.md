# IAM Role — Legacy Bank `/ask` (Amazon Bedrock)

## Why this exists

`POST /ask` (served by `agents/balerica.py`) tries Amazon Bedrock first and
falls back to an offline knowledge base if Bedrock can't be reached. That
fallback is silent by design — there's no error in the API response, no
stack trace, nothing in the `curl` output to tell you *why* it fell back.
The only visible sign is `"source": "offline-knowledge-base"` instead of
`"source": "amazon-bedrock"`.

That silence hides three independent requirements, and all three have to
be true at once for Bedrock to actually answer:

1. **An IAM role is attached to the EC2 instance**, with permission to call
   Bedrock. No role → every `invoke_model()` call raises immediately →
   always offline, no matter what else is configured.
2. **`AWS_REGION` matches the region where you enabled model access.**
   `balerica.py` defaults to `us-east-1` if `AWS_REGION` isn't set. If you
   enabled Claude in a different region's Bedrock console, the SDK is
   calling the wrong region and will never find it.
3. **`BEDROCK_MODEL_ID` is a real model/inference-profile ID.** The code
   ships with a deliberately invalid placeholder
   (`anthropic.claude-sonnet-4.X`) as a "Student Challenge" — see
   `runbook.md` Step 8. Newer Claude models require the *inference
   profile* ID (starts with `us.`), not the bare base-model ID.

Get any one of these wrong and the symptom is identical: a quiet fallback
to the offline knowledge base. Check all three in order before assuming
something else is broken.

## What's in this folder

- `ec2-trust-policy.json` — lets EC2 instances assume this role.
- `bedrock-invoke-policy.json` — grants exactly one permission,
  `bedrock:InvokeModel`. Nothing else. This lab never calls any other AWS
  API from the running instance, so the role should never need more than
  this.

## Instructor setup (one-time per AWS account)

```bash
aws iam create-role --role-name BalericaLegacyBankEC2Role \
  --assume-role-policy-document file://ec2-trust-policy.json

aws iam put-role-policy --role-name BalericaLegacyBankEC2Role \
  --policy-name BedrockInvokeModel \
  --policy-document file://bedrock-invoke-policy.json

aws iam create-instance-profile --instance-profile-name BalericaLegacyBankEC2Role

aws iam add-role-to-instance-profile \
  --instance-profile-name BalericaLegacyBankEC2Role \
  --role-name BalericaLegacyBankEC2Role
```

Then attach it to each student's running instance (repeat per instance,
or bake it into the launch template/AMI so every new instance already has
it):

```bash
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxxxxxxxxxxxxxx \
  --iam-instance-profile Name=BalericaLegacyBankEC2Role \
  --region <the region the instance is actually running in>
```

Role/instance-profile creation requires IAM admin privileges — this is an
instructor action, not something students should need to do themselves.

## Verifying it's attached (student or instructor)

From the AWS Console: **EC2 → Instances → (your instance) → Security tab →
IAM Role**. If it says "none", Bedrock will never work no matter what else
you fix — ask your instructor to attach the role.

From the CLI (needs `ec2:DescribeInstances`):

```bash
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxxxxxx \
  --query 'Reservations[0].Instances[0].IamInstanceProfile'
```

`null` means no role is attached.
