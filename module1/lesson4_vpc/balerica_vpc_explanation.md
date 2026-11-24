# SEIR Foundations — Module 1, Lab 4
## Cloud Network Automation Scripting

Companion to `create_balerica_vpc.sh` | Jira: M1-6

### What are we building?

A VPC is a logically isolated AWS network. This script creates one VPC in us-east-1, nine subnets, one Internet Gateway and three custom route tables. AWS also creates a main route table, default security group and default network ACL. The script does not deploy EC2, Aurora, NAT, ALB or ASG, and does not create custom security groups.

| Tier | AZ A | AZ B | AZ C | Future role |
|---|---|---|---|---|
| Public | 10.20.1.0/24 | 10.20.2.0/24 | 10.20.3.0/24 | EC2 initially; ALB later |
| Private 1 | 10.20.11.0/24 | 10.20.12.0/24 | 10.20.13.0/24 | EC2 ASG later |
| Private 2 | 10.20.21.0/24 | 10.20.22.0/24 | 10.20.23.0/24 | Aurora later |

The VPC is 10.20.0.0/16. The units digit of the third octet identifies the AZ; the tens digit identifies the tier. AZ letters are account-relative; use AZ IDs when coordinating across accounts.

### Before running

Use AWS CloudShell or Bash 4+ with AWS CLI installed and authenticated. The script uses Bash uppercase expansion (`${tier^^}`), which is not supported by the older Bash shipped with some macOS systems. Check your account and permissions; you need EC2 describe, create, tag, modify, attach and associate permissions for the resources involved. Use a designated lab account. Do not run this in production.

```bash
bash --version
aws --version
aws sts get-caller-identity
bash -n create_balerica_vpc.sh
bash create_balerica_vpc.sh
```

ClickOps, individual CLI commands and this script are alternative ways of deploying the same network. Do not deploy duplicates. Never delete the default VPC.

### Read the script in execution order

1. `#!/usr/bin/env bash` selects Bash. `set -Eeuo pipefail` stops on many command failures, catches unset variables, propagates pipeline errors and inherits ERR traps. It does not roll back AWS resources.
2. `export AWS_REGION="${AWS_REGION:-us-east-1}"` sets a default if the variable is unset or empty. AWS_DEFAULT_REGION matches it; AWS_PAGER is disabled. PROJECT defaults to balerica and NETWORK_PREFIX to 10.20. The script derives the /16 VPC and /24 subnets from the two-octet prefix. Example: `NETWORK_PREFIX=10.30 PROJECT=balerica-dev bash create_balerica_vpc.sh`. Use a valid private /16 prefix and check overlap before changing it.
3. The ERR trap reports the failing line. `command -v aws` checks the CLI; STS identifies the account. Existing state files and matching VPC names cause the script to stop. The AZ loop checks a, b and c are available. These checks are not a comprehensive permission or overlap test.
4. `umask 077` restricts permissions on new files. `save()` writes shell-escaped key/value pairs to the state file using `printf '%s=%q\n'`. IDs are saved as resources are created, including during partial deployment.
5. `VPC_ID=$(aws ec2 create-vpc ... --query Vpc.VpcId --output text)` captures the ID from AWS. `--query` uses JMESPath to select a field; `--output text` avoids JSON wrapping. Tags provide readable names; IDs identify actual resources. The waiter checks availability before DNS attributes are enabled.
6. The Internet Gateway is created, its ID saved and it is attached to the VPC. An attached gateway alone does not make any subnet public.
7. The outer loop runs for public, private1 and private2. `case` assigns base 0, 10 or 20. A custom route table is created per tier. Only public receives `0.0.0.0/0` pointing to the IGW. All tables have a local VPC route automatically.
8. The inner loop runs for AZ a, b and c. `n=$((n+1))` increments the counter. `cidr="$NETWORK_PREFIX.$((base+n)).0/24"` generates the subnet. Example: private1, AZ c => base 10 + 3 => 10.20.13.0/24. The counter resets for each tier. Nine iterations create nine subnets.
9. Each subnet ID is saved, the waiter checks availability, and public IPv4 auto-assignment is explicitly enabled for public or disabled for private. The subnet is associated with its tier's route table; the association ID is saved. `${tier^^}` and `${az^^}` uppercase variable names, yielding PRIVATE1_C_ID, for example.
10. The final describe-subnets command prints an inventory. This is a useful visual check, not a complete automated verification of every route or security rule.

### Routing and security

| Destination | Public | Private 1 | Private 2 |
|---|---|---|---|
| 10.20.0.0/16 | local | local | local |
| 0.0.0.0/0 | IGW | absent | absent |

A public subnet has a direct route to an IGW. IPv4 Internet access also requires a public IPv4 address and appropriate security controls. Private subnets can communicate over the local route, subject to security groups and NACLs. Later, allow PostgreSQL TCP 5432 from the application security group to the Aurora security group, not from the entire Internet. Private 1 will need NAT or suitable endpoints for outbound dependencies; Private 2 remains without a direct Internet route. Route tables choose paths, security groups are stateful resource-level filters, and NACLs are stateless subnet-level filters.

### Reuse your resource IDs

```bash
source ./balerica-network.env
export AWS_REGION AWS_DEFAULT_REGION="$AWS_REGION"
aws sts get-caller-identity
aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --output table
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --output table
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" --output json
aws ec2 describe-internet-gateways --internet-gateway-ids "$IGW_ID"
```

Source only your own trusted state file: sourcing executes shell code. The file contains IDs, not credentials; keep it out of public Git repositories. Confirm account and region before reuse. The future Aurora subnet group uses PRIVATE2_A_ID, PRIVATE2_B_ID and PRIVATE2_C_ID; the ASG uses PRIVATE1 equivalents.

### Troubleshooting without panic

| Symptom | Check |
|---|---|
| aws not found | Install CLI or use CloudShell |
| AccessDenied / expired token | STS identity, session and IAM permissions; do not grant blanket admin access as a workaround |
| AZ unavailable | Describe availability zones in the selected account/region |
| Invalid CIDR | Prefix, /16 parent, /24 boundary and overlapping subnets |
| State file or VPC already exists | Inspect existing resources; do not delete the state file just to bypass protection |
| Public EC2 cannot reach Internet | Public IPv4, IGW attachment, explicit route association, default route, SG, NACL and OS |
| Private EC2 cannot download packages | Expected without outbound connectivity; NAT/endpoints are later work |
| Script stops halfway | Inspect line, saved IDs and AWS console; partial resources may remain. No automatic rollback or resume. |

The network resources created here generally have no hourly charge by themselves; later EC2, public IPv4, NAT, ALB and Aurora may incur charges. Follow instructor-approved cleanup, never delete the default VPC or resources used by other labs. Do not rerun until partial deployment is resolved.

### Portfolio and evidence

Submit your script, a diagram, nine subnet CIDRs, sanitized CLI output, screenshots of route associations and a troubleshooting explanation. Explain why the two private route tables are separate despite identical initial routes. Demonstrate changing the prefix on paper or with echo, not by creating unnecessary infrastructure. Interview question: how does this script avoid hardcoded resource IDs, and what would you improve for idempotency, rollback, validation and Terraform migration?

Validation: companion explanation is based on the supplied script. Live AWS execution has not been verified here.
