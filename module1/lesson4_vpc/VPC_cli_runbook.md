# SEIR Foundations — Module 1, Lab 4
## Cloud Network Automation Scripting: AWS CLI Runbook

**Jira:** [M1-6](https://theowaf.atlassian.net/browse/M1-6)  
**Region:** us-east-1 | **Level:** beginner | **Shell:** Bash

### Purpose

Build the Balerica Bank network manually using AWS CLI commands, then understand how `create_balerica_vpc.sh` automates the same operations. Do not run both deployment methods against the same lab environment. This is a fresh VPC deployment, not an update to your default VPC. Read `RFC_1918_Explanation.md` and `balerica_vpc_explanation.md` alongside this runbook.

By the end you should be able to explain every resource, trace a packet, retrieve AWS resource IDs programmatically, and diagnose a failed deployment without blindly repeating commands.

## Gate 01 — Understand the design

The VPC is a regional logical network; each subnet belongs to exactly one Availability Zone (AZ). Our VPC uses 10.20.0.0/16, a portion of the RFC 1918 10.0.0.0/8 private range. A /16 has 65,536 addresses; each /24 has 256, of which AWS normally reserves five, leaving 251 assignable addresses. For example, 10.20.13.0 through 10.20.13.3 and 10.20.13.255 are reserved in that subnet.

| Tier | us-east-1a | us-east-1b | us-east-1c |
|---|---|---|---|
| Public | 10.20.1.0/24 | 10.20.2.0/24 | 10.20.3.0/24 |
| Private 1 | 10.20.11.0/24 | 10.20.12.0/24 | 10.20.13.0/24 |
| Private 2 | 10.20.21.0/24 | 10.20.22.0/24 | 10.20.23.0/24 |

The third octet encodes the tier and AZ. For example, 10.20.22.47 belongs to the database tier in AZ B. AZ letters can map to different physical zones in different AWS accounts. The /24 convention is our teaching standard, not a universal AWS requirement.

Initially EC2 with SQLite belongs in Public A. Lab 5 introduces Aurora in Private 2. Later the public ALB receives client traffic, EC2 ASG instances occupy Private 1, and Aurora remains in Private 2. No NAT gateway, EC2, ALB or database is created by this network-only runbook. Security groups and application deployment are separate exercises.

## Gate 02 — Prepare your terminal

Use AWS CloudShell in us-east-1, or Bash on Linux, macOS or WSL with AWS CLI v2 and authorized credentials. Do not paste Bash into PowerShell or CMD. Use a dedicated student account or authorized sandbox. Do not share credentials or session tokens. The commands require permission to describe, create, tag and modify the relevant EC2 networking resources. Never delete the default VPC.

```bash
aws --version
aws sts get-caller-identity
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION="$AWS_REGION"
export AWS_PAGER=""
aws ec2 describe-availability-zones --query 'AvailabilityZones[].{AZ:ZoneName,State:State,ID:ZoneId}' --output table
```

The STS output identifies the account and principal. Confirm both before continuing. Check that a, b and c are available. Stop if any command fails. CloudShell credentials may expire; reopen the session and verify identity before resuming. Keep one terminal open throughout the lab. A backslash at the end of a line continues the command; do not add spaces after it.

## Gate 03 — Define variables once

```bash
PROJECT=balerica
NETWORK_PREFIX=10.20
VPC_CIDR="${NETWORK_PREFIX}.0.0/16"
STATE_FILE="${PROJECT}-network.env"
AZ_A="${AWS_REGION}a"
AZ_B="${AWS_REGION}b"
AZ_C="${AWS_REGION}c"
printf 'Project: %s\nVPC: %s\nRegion: %s\n' "$PROJECT" "$VPC_CIDR" "$AWS_REGION"
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${PROJECT}-vpc" --query 'Vpcs[].{ID:VpcId,CIDR:CidrBlock}' --output table
ls -l "$STATE_FILE" 2>/dev/null || true
```

If a matching VPC or state file exists, stop and inspect it. Do not overwrite it or create duplicates. Variables are named containers for values; `$VARIABLE` expands the value and `${VARIABLE}` makes its boundary explicit. Double quotes preserve a value as one argument. `export` makes a variable available to child processes. The network prefix must be two valid IPv4 octets defining an approved, nonoverlapping private /16. For this class keep 10.20.

Only after confirming no existing deployment, initialize a private state file:

```bash
umask 077
( set -o noclobber; : > "$STATE_FILE" )
save() { printf '%s=%q\n' "$1" "$2" >> "$STATE_FILE"; }
save AWS_REGION "$AWS_REGION"
save VPC_CIDR "$VPC_CIDR"
```

Stop if initialization fails. The function records shell-safe assignments so later labs can reuse IDs. This is not a secret store or a Terraform state file. Do not publish it with your homework.

## Gate 04 — Create the VPC

```bash
VPC_ID=$(aws ec2 create-vpc --cidr-block "$VPC_CIDR" \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT}-vpc}]" \
  --query 'Vpc.VpcId' --output text)
echo "$VPC_ID"
```

`aws ec2 create-vpc` invokes the EC2 networking API. `--query` selects one field from the response using JMESPath; `--output text` removes JSON formatting. `$(...)` captures stdout into a variable. Confirm a real `vpc-...` ID before proceeding; a blank value or `None` is not success. Tags are labels, not unique identifiers.

```bash
save VPC_ID "$VPC_ID"
aws ec2 wait vpc-available --vpc-ids "$VPC_ID"
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-support '{"Value":true}'
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'
aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --output table
```

Waiters poll until a resource reaches the expected state. DNS support enables VPC DNS resolution; DNS hostnames enables appropriate AWS DNS hostname assignment. Neither creates a public route. AWS automatically creates a main route table, default security group and default network ACL for this VPC.

## Gate 05 — Create and attach the Internet Gateway

```bash
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT}-igw}]" \
  --query 'InternetGateway.InternetGatewayId' --output text)
echo "$IGW_ID"
```

Confirm `igw-...`, then:

```bash
save IGW_ID "$IGW_ID"
aws ec2 attach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID"
aws ec2 describe-internet-gateways --internet-gateway-ids "$IGW_ID" --output table
```

An IGW provides a path between a VPC and the Internet. Attaching it alone does not give every subnet Internet access. A public IPv4 address, suitable routing and security controls are also required for direct IPv4 Internet access by EC2.

## Gate 06 — Create three route tables

Execute each assignment separately and confirm its `rtb-...` output before saving or continuing.

```bash
PUBLIC_RT_ID=$(aws ec2 create-route-table --vpc-id "$VPC_ID" --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-public-rt}]" --query RouteTable.RouteTableId --output text)
echo "$PUBLIC_RT_ID"
save PUBLIC_RT_ID "$PUBLIC_RT_ID"
PRIVATE1_RT_ID=$(aws ec2 create-route-table --vpc-id "$VPC_ID" --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-private1-rt}]" --query RouteTable.RouteTableId --output text)
echo "$PRIVATE1_RT_ID"
save PRIVATE1_RT_ID "$PRIVATE1_RT_ID"
PRIVATE2_RT_ID=$(aws ec2 create-route-table --vpc-id "$VPC_ID" --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-private2-rt}]" --query RouteTable.RouteTableId --output text)
echo "$PRIVATE2_RT_ID"
save PRIVATE2_RT_ID "$PRIVATE2_RT_ID"
aws ec2 create-route --route-table-id "$PUBLIC_RT_ID" --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID"
```

Every table automatically has a local VPC route. The default route matches destinations not covered by a more specific route. Traffic to 10.20.22.47 matches 10.20.0.0/16 rather than 0.0.0.0/0 (longest-prefix match). Private 1 and Private 2 have only local routes today; later their outbound routing requirements differ. A route table is not a firewall.

## Gate 07 — Create nine subnets, one at a time

First execute the complete command for Public A:

```bash
PUBLIC_A_ID=$(aws ec2 create-subnet --vpc-id "$VPC_ID" \
  --cidr-block "${NETWORK_PREFIX}.1.0/24" --availability-zone "$AZ_A" \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-public-a}]" \
  --query Subnet.SubnetId --output text)
echo "$PUBLIC_A_ID"
```

Confirm `subnet-...`. The CIDR must fit inside the VPC and not overlap an existing subnet. The AZ is fixed at creation. To avoid repeating the same long command eight times, define this helper; it still invokes the same AWS CLI operation individually.

```bash
make_subnet() {
  aws ec2 create-subnet --vpc-id "$VPC_ID" \
    --cidr-block "${NETWORK_PREFIX}.$2.0/24" --availability-zone "$3" \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-$1}]" \
    --query Subnet.SubnetId --output text
}
save PUBLIC_A_ID "$PUBLIC_A_ID"
```

`$1`, `$2`, `$3` are function arguments: name suffix, third octet and AZ. Run each following line separately; check its ID before saving it. Do not repeat a successful creation command.

```bash
PUBLIC_B_ID=$(make_subnet public-b 2 "$AZ_B"); echo "$PUBLIC_B_ID"
save PUBLIC_B_ID "$PUBLIC_B_ID"
PUBLIC_C_ID=$(make_subnet public-c 3 "$AZ_C"); echo "$PUBLIC_C_ID"
save PUBLIC_C_ID "$PUBLIC_C_ID"
PRIVATE1_A_ID=$(make_subnet private1-a 11 "$AZ_A"); echo "$PRIVATE1_A_ID"
save PRIVATE1_A_ID "$PRIVATE1_A_ID"
PRIVATE1_B_ID=$(make_subnet private1-b 12 "$AZ_B"); echo "$PRIVATE1_B_ID"
save PRIVATE1_B_ID "$PRIVATE1_B_ID"
PRIVATE1_C_ID=$(make_subnet private1-c 13 "$AZ_C"); echo "$PRIVATE1_C_ID"
save PRIVATE1_C_ID "$PRIVATE1_C_ID"
PRIVATE2_A_ID=$(make_subnet private2-a 21 "$AZ_A"); echo "$PRIVATE2_A_ID"
save PRIVATE2_A_ID "$PRIVATE2_A_ID"
PRIVATE2_B_ID=$(make_subnet private2-b 22 "$AZ_B"); echo "$PRIVATE2_B_ID"
save PRIVATE2_B_ID "$PRIVATE2_B_ID"
PRIVATE2_C_ID=$(make_subnet private2-c 23 "$AZ_C"); echo "$PRIVATE2_C_ID"
save PRIVATE2_C_ID "$PRIVATE2_C_ID"
```

## Gate 08 — Configure subnet attributes and associations

The helper below waits for each subnet, configures automatic public IPv4 assignment and explicitly associates the correct route table. The fourth argument is the state-file variable name for the association ID. `local` limits a variable to the function. `|| return` stops the function if an AWS command fails.

```bash
configure_subnet() {
  local subnet="$1" rt="$2" visibility="$3" key="$4" assoc
  aws ec2 wait subnet-available --subnet-ids "$subnet" || return 1
  if [[ "$visibility" == public ]]; then
    aws ec2 modify-subnet-attribute --subnet-id "$subnet" --map-public-ip-on-launch || return 1
  else
    aws ec2 modify-subnet-attribute --subnet-id "$subnet" --no-map-public-ip-on-launch || return 1
  fi
  assoc=$(aws ec2 associate-route-table --subnet-id "$subnet" --route-table-id "$rt" --query AssociationId --output text) || return 1
  save "$key" "$assoc"
  echo "$subnet -> $rt ($assoc)"
}
```

Run individually, stopping on any error:

```bash
configure_subnet "$PUBLIC_A_ID" "$PUBLIC_RT_ID" public PUBLIC_A_ASSOC_ID
configure_subnet "$PUBLIC_B_ID" "$PUBLIC_RT_ID" public PUBLIC_B_ASSOC_ID
configure_subnet "$PUBLIC_C_ID" "$PUBLIC_RT_ID" public PUBLIC_C_ASSOC_ID
configure_subnet "$PRIVATE1_A_ID" "$PRIVATE1_RT_ID" private PRIVATE1_A_ASSOC_ID
configure_subnet "$PRIVATE1_B_ID" "$PRIVATE1_RT_ID" private PRIVATE1_B_ASSOC_ID
configure_subnet "$PRIVATE1_C_ID" "$PRIVATE1_RT_ID" private PRIVATE1_C_ASSOC_ID
configure_subnet "$PRIVATE2_A_ID" "$PRIVATE2_RT_ID" private PRIVATE2_A_ASSOC_ID
configure_subnet "$PRIVATE2_B_ID" "$PRIVATE2_RT_ID" private PRIVATE2_B_ASSOC_ID
configure_subnet "$PRIVATE2_C_ID" "$PRIVATE2_RT_ID" private PRIVATE2_C_ASSOC_ID
```

Without explicit association a subnet uses the VPC main route table. Automatic public IPv4 assignment affects eligible new instance launches; it does not make a subnet public by itself. A private subnet may later have NAT-based outbound connectivity without becoming public.

## Gate 09 — Verify before deploying anything else

```bash
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[].{Name:Tags[?Key==`Name`]|[0].Value,CIDR:CidrBlock,AZ:AvailabilityZone,PublicIP:MapPublicIpOnLaunch,Free:AvailableIpAddressCount}' --output table
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'length(Subnets)' --output text
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" --query 'RouteTables[].{ID:RouteTableId,Routes:Routes,Associations:Associations}' --output json
aws ec2 describe-vpc-attribute --vpc-id "$VPC_ID" --attribute enableDnsSupport
aws ec2 describe-vpc-attribute --vpc-id "$VPC_ID" --attribute enableDnsHostnames
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VPC_ID" --output table
```

Expected: nine subnets; three with public IPv4 mapping true; six false; four route tables including the AWS-created main table; three explicit associations per custom table; only the public table has an IGW default route; one attached IGW; both DNS attributes true. Inspect the VPC resource map in the console and compare each CIDR with the design. These checks verify configuration, not actual application connectivity.

## Gate 10 — Automation and troubleshooting

The companion `create_balerica_vpc.sh` performs the same network deployment using nested loops, strict Bash error handling, duplicate checks and incremental state recording. Use it only in a fresh authorized environment after instructor-approved cleanup of the manual lab or with a separate approved project and nonoverlapping prefix. On macOS use Bash 4+ (the script uses uppercase expansion `${tier^^}`); CloudShell is recommended.

```bash
bash -n create_balerica_vpc.sh
# Only for a fresh deployment:
AWS_REGION=us-east-1 PROJECT=balerica NETWORK_PREFIX=10.20 bash create_balerica_vpc.sh
```

`bash -n` checks syntax, not AWS permissions or runtime correctness. The script is not idempotent and does not automatically roll back failures. Never remove the state file merely to bypass its safety check.

| Symptom | Investigation |
|---|---|
| Unable to locate credentials / expired token | Reauthenticate; run STS identity check |
| UnauthorizedOperation | Confirm IAM permissions with instructor; do not grant yourself administrator access |
| InvalidSubnet.Conflict | Describe existing subnets; compare CIDRs; do not delete blindly |
| InvalidSubnet.Range | Check containment within VPC and /24 boundary |
| InvalidVpcID.NotFound | Check region, account, variable value and resource state |
| RouteAlreadyExists | Inspect route table; do not blindly recreate or replace routes |
| Public EC2 cannot reach Internet (later) | Check public IP, subnet association, IGW attachment, default route, SG egress, NACL and OS |
| EC2 cannot reach private Aurora (later) | Check endpoint DNS, local route, DB availability, TCP 5432 SG references, NACLs and TLS/authentication |

Security groups are stateful resource-level controls; NACLs are stateless subnet-level controls. Private addressing alone does not block traffic between tiers. Later allow database inbound TCP 5432 from the application SG, not from the entire Internet. For a public EC2 test restrict SSH to your approved source IP; do not expose banking endpoints or real data unnecessarily.

### Resume a later session

Inspect the state file before sourcing it; source only your own trusted file. Recheck account and region first.

```bash
cat balerica-network.env
source ./balerica-network.env
export AWS_REGION AWS_DEFAULT_REGION="$AWS_REGION" AWS_PAGER=""
aws sts get-caller-identity
aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --output table
```

The Private 2 IDs will be used in Lab 5 for an Aurora DB subnet group; Private 1 IDs will be used in the ASG lab. Keep this VPC if continuing the course. For cleanup, follow instructor-approved dependency-aware instructions: remove only lab-owned dependent resources, then subnets, custom route tables, detached IGW and VPC. Do not delete the default VPC or unrelated resources. This runbook intentionally does not automate deletion. Network-only resources here generally do not incur hourly charges, but later public IPv4, NAT, EC2, ALB, Aurora and traffic can incur charges.

## Student deliverables and interview readiness

Submit a GitHub README with your own subnet calculations, sanitized screenshots of the VPC map, CLI subnet inventory, route associations and DNS/IGW checks, plus an explanation of one troubleshooting scenario. Do not commit credentials or the generated state file. Explain why the public EC2 can reach a private database, why a public IP alone is insufficient, and how changing NETWORK_PREFIX regenerates all nine CIDRs. Demonstrate the manual CLI method before the automated alternative. Do not claim live application connectivity until you have tested it in later gates/labs.

Suggested portfolio title: **Cloud Network Automation Scripting — AWS Three-Tier VPC**. Describe what you actually built and verified, not what the future ASG architecture promises.

## References

- RFC 1918: https://www.rfc-editor.org/rfc/rfc1918.html
- AWS VPC documentation: https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
- AWS CLI EC2 reference: https://docs.aws.amazon.com/cli/latest/reference/ec2/

Instructor note: commands are prepared for Bash and AWS CLI v2; live AWS execution has not been performed in this authoring session. Gate numbering in this runbook describes CLI execution checkpoints, not a replacement for the Epic's overall curriculum gates.
