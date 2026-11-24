# SEIR Foundations — Module 1, Lab 4
## RFC 1918, Private IPv4 and Subnetting

Required background for Cloud Network Automation Scripting. Read the original standard: [RFC 1918 — Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918.html), February 1996. This guide is an instructional explanation, not a replacement for the RFC.

### Why private addresses exist

IPv4 uses 32 bits, giving 2^32 possible addresses. RFC 1918 reserves three blocks for private networks. Organizations can reuse these addresses without obtaining globally unique allocations. They are not globally routable on the public Internet; private networks can route them internally and across coordinated private connections. Private addressing alone is not encryption, authentication or a firewall. NAT is one way private hosts can access public services, but RFC 1918 does not require NAT for internal communication.

| CIDR | Inclusive range | Total addresses |
|---|---|---:|
| 10.0.0.0/8 | 10.0.0.0 – 10.255.255.255 | 16,777,216 |
| 172.16.0.0/12 | 172.16.0.0 – 172.31.255.255 | 1,048,576 |
| 192.168.0.0/16 | 192.168.0.0 – 192.168.255.255 | 65,536 |

Not all 172.x addresses are private. 172.32.0.1 is outside RFC 1918. Other special-use ranges exist (loopback, link-local, shared address space); they are not RFC 1918 blocks.

### Binary: no panic required

An octet contains eight bits. Their weights from left to right are 128, 64, 32, 16, 8, 4, 2, 1. Add the weights of the bits set to 1.

```text
Weights: 128 64 32 16  8  4  2  1
10:        0  0  0  0  1  0  1  0 = 8 + 2
20:        0  0  0  1  0  1  0  0 = 16 + 4
13:        0  0  0  0  1  1  0  1 = 8 + 4 + 1
47:        0  0  1  0  1  1  1  1 = 32 + 8 + 4 + 2 + 1
```

10.20.13.47 = `00001010.00010100.00001101.00101111`.

CIDR /24 means the first 24 bits are the network prefix, leaving 8 host bits. Its mask is `11111111.11111111.11111111.00000000` = 255.255.255.0. Bitwise AND of address and mask gives 10.20.13.0. Set all host bits to 1 for the last address, 10.20.13.255. AWS reserves that address even though VPC does not support broadcast.

| Prefix | Mask | Total addresses | AWS assignable per ordinary subnet |
|---|---|---:|---:|
| /16 | 255.255.0.0 | 65,536 | 65,531 |
| /20 | 255.255.240.0 | 4,096 | 4,091 |
| /24 | 255.255.255.0 | 256 | 251 |
| /26 | 255.255.255.192 | 64 | 59 |
| /28 | 255.255.255.240 | 16 | 11 |

Formula: total = 2^(32-prefix). AWS normally reserves five IPv4 addresses per subnet, not per VPC. In 10.20.13.0/24: .0 network, .1 router, .2 reserved for DNS, .3 future use, .255 last address. Assignable range .4–.254. The actual Amazon DNS resolver uses the primary VPC CIDR base plus two (and link-local 169.254.169.253); the .2 address is reserved in every subnet. Traditional subnetting often subtracts two, but AWS subtracts five. A /16 VPC can contain 256 nonoverlapping /24 blocks mathematically; service quotas and reserved addresses still apply.

### Balerica addressing standard

VPC: 10.20.0.0/16 (inside 10.0.0.0/8).

| Tier | AZ A | AZ B | AZ C |
|---|---|---|---|
| Public | 10.20.1.0/24 | 10.20.2.0/24 | 10.20.3.0/24 |
| Private 1 | 10.20.11.0/24 | 10.20.12.0/24 | 10.20.13.0/24 |
| Private 2 | 10.20.21.0/24 | 10.20.22.0/24 | 10.20.23.0/24 |

Nine subnets provide 2,259 normally assignable addresses before resources consume them. The third octet identifies tier and AZ. 10.20.13.47 is application tier C; 10.20.22.81 is database tier B. /24 is our teaching baseline, not a universal engineering rule: larger or smaller subnets should follow capacity planning. /20 boundaries in the third octet are multiples of 16; 10.20.0.0/20 covers third octets 0–15 and overlaps several of our /24s.

### Private IP does not mean private subnet

Both public and private AWS subnets can use RFC 1918 addresses. A public subnet has a direct route to an Internet Gateway. An EC2 instance additionally needs a public IPv4 address and permitted traffic to reach the Internet over IPv4. A private subnet lacks that direct route. It can still reach other VPC subnets via the local route, subject to security rules. NAT can provide outbound connectivity later without direct unsolicited inbound Internet access.

For a packet to 10.20.22.81, the local 10.20.0.0/16 route is more specific than 0.0.0.0/0 and wins by longest-prefix matching. Aurora can therefore remain private while EC2 connects to it. A route is not permission: the database security group must allow the application traffic.

### Avoid overlapping networks

Two isolated VPCs may reuse the same CIDR, but connecting them via peering, VPN or Transit Gateway requires careful nonoverlapping address planning. 10.20.0.0/16 can still overlap a corporate network. Check existing allocations before connecting networks. Do not change or delete the default VPC for this exercise.

### Practice before opening the AWS Console

1. Convert 21 and 23 to binary.
2. Identify the tier and AZ for 10.20.12.50.
3. Calculate the mask, total addresses and AWS assignable addresses for /26.
4. Does 10.20.13.0/24 overlap 10.20.0.0/20?
5. Is 172.31.255.254 RFC 1918? What about 172.32.0.1?
6. Why can an EC2 instance in a public subnet connect to a private Aurora instance without a NAT gateway?
7. Divide 10.20.50.0/24 into four /26 networks.

### Answer key (attempt first)

1. 00010101 and 00010111. 2. Private 1, AZ B. 3. 255.255.255.192; 64 total, 59 AWS assignable. 4. Yes. 5. Yes; no. 6. Local VPC routing plus permitted security controls. 7. 10.20.50.0/26, 10.20.50.64/26, 10.20.50.128/26, 10.20.50.192/26.

### Reading

- [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918.html): sections 2–5, motivation, private address space, advantages/disadvantages and operational considerations.
- [RFC 4632 — CIDR](https://www.rfc-editor.org/rfc/rfc4632.html): prefix notation and aggregation.
- [AWS subnet sizing](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html): AWS-specific reserved addresses.
- [AWS route tables](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html): subnet associations and routing.

Deliverable: explain the three private ranges, show binary calculations, and reproduce the nine-subnet plan without copying the script. Chewbacca expects you to understand the network before automating it.
