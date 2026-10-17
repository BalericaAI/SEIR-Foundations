#!/bin/bash
# SEIR Foundations - Amazon Linux 2023 EC2 User Data
# Combined SSH/dashboard + HTTP web server configuration
# Paste this entire file into:
# EC2 > Advanced details > User data

set -u

###############################################################################
# PART 1 — SEIR FOUNDATIONS SSH DASHBOARD
###############################################################################

cat > /usr/local/bin/seir-dashboard <<'DASH'
#!/bin/bash
# Interactive SSH dashboard; no AWS credentials or external packages required.
[ -t 1 ] || exit 0

RESET='\033[0m'
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'

printf "${CYAN}"

cat <<'ART'
  ____  _____ ___ ____     _____ ___  _   _ _   _ ____    _  _____ ___ ___  _   _ ____
 / ___|| ____|_ _|  _ \   |  ___/ _ \| | | | \ | |  _ \  / \|_   _|_ _/ _ \| \ | / ___|
 \___ \|  _|  | || |_) |  | |_ | | | | | | |  \| | | | |/ _ \ | |  | | | | | |  \| \___ \
  ___) | |___ | ||  _ <   |  _|| |_| | |_| | |\  | |_| / ___ \| |  | | |_| | |\  |___) |
 |____/|_____|___|_| \_\  |_|   \___/ \___/|_| \_|____/_/   \_\_| |___\___/|_| \_|____/
ART

printf "${RESET}\n"
printf "${GREEN}CHEWBACCA OPERATIONS CENTER${RESET}  |  Welcome to your first EC2!\n"
printf "${BLUE}-----------------------------------------------------------------------${RESET}\n"

hostname_val=$(hostname 2>/dev/null || echo unknown)
uptime_val=$(uptime -p 2>/dev/null || echo unavailable)
cores=$(nproc 2>/dev/null || echo '?')
load=$(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || echo unavailable)
mem=$(free -h 2>/dev/null | awk '/^Mem:/ {print $3 " used / " $2 " total"}')
disk=$(df -h / 2>/dev/null | awk 'NR==2 {print $3 " used / " $2 " total (" $5 " full)"}')

# /proc/stat counters sampled 0.2 seconds apart;
# reflects approximate system-wide CPU busy percent.
read -r _ u n s i w irq sirq st _ < /proc/stat
idle1=$((i+w))
total1=$((u+n+s+i+w+irq+sirq+st))

sleep 0.2

read -r _ u n s i w irq sirq st _ < /proc/stat
idle2=$((i+w))
total2=$((u+n+s+i+w+irq+sirq+st))

dt=$((total2-total1))
di=$((idle2-idle1))

if [ "$dt" -gt 0 ]; then
    cpu=$((100*(dt-di)/dt))
else
    cpu=0
fi

printf "Hostname      : %s\n" "$hostname_val"
printf "Uptime        : %s\n" "$uptime_val"
printf "CPU           : %s%% busy (approx.) | %s vCPU(s)\n" "$cpu" "$cores"
printf "Load average  : %s (1, 5, 15 minutes)\n" "$load"
printf "Memory        : %s\n" "${mem:-unavailable}"
printf "Root disk     : %s\n" "${disk:-unavailable}"

# IMDSv2 only. If unavailable, skip metadata without delaying SSH login.
token=$(curl -fsS --connect-timeout 1 --max-time 2 -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token 2>/dev/null || true)

if [ -n "$token" ]; then

    meta() {
        curl -fsS --connect-timeout 1 --max-time 2 \
          -H "X-aws-ec2-metadata-token: $token" \
          "http://169.254.169.254/latest/meta-data/$1" 2>/dev/null || true
    }

    iid=$(meta instance-id)
    itype=$(meta instance-type)
    az=$(meta placement/availability-zone)

    printf "Instance ID   : %s\n" "${iid:-unavailable}"
    printf "Instance type : %s\n" "${itype:-unavailable}"
    printf "AWS zone      : %s\n" "${az:-unavailable}"
fi

printf "${BLUE}-----------------------------------------------------------------------${RESET}\n"
printf "${YELLOW}COST REALITY CHECK${RESET}\n"
printf "  CPU at 1%% does NOT mean free. Charges depend on instance type,\n"
printf "  running time, storage, network usage, and your AWS account benefits.\n"
printf "  Check AWS Billing > Free Tier and Cost Explorer. Set a budget alert.\n"
printf "  Stop the instance when the lab is done (EBS storage can still cost).\n"
printf "${BLUE}-----------------------------------------------------------------------${RESET}\n"
printf "${GREEN}RRRAAAWWWRRR!${RESET} Chewbacca says: Verify first. Panic later.\n"
printf "Run ${CYAN}seir-dashboard${RESET} anytime to see this again.\n\n"
DASH

chmod 755 /usr/local/bin/seir-dashboard

###############################################################################
# PART 2 — AUTOMATIC DASHBOARD ON SSH LOGIN
###############################################################################

cat > /etc/profile.d/seir-dashboard.sh <<'PROFILE'
if [ -n "${PS1:-}" ] && [ -t 1 ] && [ -z "${SEIR_DASHBOARD_SHOWN:-}" ]; then
    export SEIR_DASHBOARD_SHOWN=1
    /usr/local/bin/seir-dashboard || true
fi
PROFILE

chmod 644 /etc/profile.d/seir-dashboard.sh

echo 'SEIR dashboard installed.'

###############################################################################
# PART 3 — INSTALL APACHE HTTP SERVER FOR PORT 80
###############################################################################

# Install Apache HTTP server
yum update -y
yum install -y httpd

# Start Apache immediately
systemctl start httpd

# Make Apache start automatically after reboot
systemctl enable httpd

###############################################################################
# PART 4 — RETRIEVE EC2 INSTANCE METADATA USING IMDSv2
###############################################################################

# Get the IMDSv2 token
TOKEN=$(curl -X PUT \
    "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Retrieve metadata
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    -s http://169.254.169.254/latest/meta-data/local-ipv4 \
    &> /tmp/local_ipv4 &

curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    -s http://169.254.169.254/latest/meta-data/placement/availability-zone \
    &> /tmp/az &

curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/ \
    &> /tmp/macid &

# Wait for all background metadata requests
wait

macid=$(cat /tmp/macid)
local_ipv4=$(cat /tmp/local_ipv4)
az=$(cat /tmp/az)

# Retrieve VPC ID
vpc=$(curl \
    -H "X-aws-ec2-metadata-token: $TOKEN" \
    -s \
    http://169.254.169.254/latest/meta-data/network/interfaces/macs/${macid}/vpc-id)

###############################################################################
# PART 5 — CREATE THE PORT 80 WEB PAGE
###############################################################################

cat > /var/www/html/index.html <<EOF
<!doctype html>
<html lang="en" class="h-100">
<head>
    <title>Details for EC2 instance</title>
</head>

<body>
<div>
    <h1>AWS Instance Details: Class 8 Edition</h1>
    <h1>Dusty Cloud Engineer in training!</h1>
    <h2>I will survive the AI Tsunami!</h2>

    <br>

    <img src="https://www.w3schools.com/images/w3schools_green.jpg"
         alt="W3Schools.com">

    <br>

    <p>
        <b>Instance Name:</b>
        $(hostname -f)
    </p>

    <p>
        <b>Instance Private Ip Address:</b>
        ${local_ipv4}
    </p>

    <p>
        <b>Availability Zone:</b>
        ${az}
    </p>

    <p>
        <b>Virtual Private Cloud (VPC):</b>
        ${vpc}
    </p>

</div>
</body>
</html>
EOF

###############################################################################
# PART 6 — CLEAN UP
###############################################################################

rm -f /tmp/local_ipv4
rm -f /tmp/az
rm -f /tmp/macid

echo 'Apache HTTP server installed and configured.'
echo 'SEIR SSH dashboard installed.'
echo 'Combined EC2 user-data script completed.'
