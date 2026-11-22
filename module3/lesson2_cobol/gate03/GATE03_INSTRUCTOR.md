# Instructor guide — Gate 03

## Intended learning outcomes
1. Establish a clean desired=2/running=2, healthy=2 baseline.
2. Stop exactly one RUNNING ECS service task and observe replacement.
3. Separate ECS service events, stopped reasons, target group health, CloudWatch logs and app-level readiness.
4. Show a LOCAL broken COBOL backend that leaves FastAPI `/health` intact but makes `/ready` return 503.
5. Produce an evidence-backed incident report and clean up billable infrastructure.

## Guardrails
- **Never run against production/shared clusters.** Use only a dedicated disposable Gate 02 stack.
- Task-stop requires both `TASK_ARN` and `ACK_STOP_TASK=yes`. Script checks that selected ARN is a running member of this specific service, baseline task counts are 2, and exactly two targets are healthy.
- The failure example never deletes a VPC, changes IAM, touches databases, disables security groups, or edits ALB health check settings.
- Don't change desiredCount to zero; that tests scaling, not failure recovery.
- Don't deploy a broken image into the live ECS service for the core exercise. Broken COBOL readiness is reproduced *locally* to distinguish app health from ALB behavior without incurring repeated service churn.
- The stop task operation can temporarily lower healthy backend capacity. Prefer a controlled teaching window.
- If a previous deployment is in progress, finish it before invoking the task-stop script.
- A `runningCount=2` alone is insufficient: ALB must report two healthy targets and the ECS service must stabilize.
- The current two-AZ, single-NAT teaching topology is not truly fully AZ independent. A NAT failure in the NAT AZ can affect egress of tasks in the second AZ.
- The HTTP ALB is intentionally CIDR restricted and unencrypted: synthetic data only.

## Teaching checkpoints
**Phase A:** Show running tasks, service events, target health, task ID suffixes and AZ placement. Baseline screenshot.
**Phase B:** Stop one task, watch timeline; distinguish transient healthy target count from desired task count. Run `gate03_compare.sh` to prove one replacement task ARN and one retained task.
**Phase C:** Confirm `/ready` and calculation endpoints after stabilization, then inspect CloudWatch logs and report.
**Phase D:** Run local broken backend test; ask students whether `/health` alone is a sufficient ALB health check (no).
**Phase E:** Remove resources using Gate 02 `ACK_DELETE=yes bash scripts/cleanup.sh` once no further gates depend on them.

## Marking rubric (100 points)
- Accurate baseline evidence (15)
- Controlled stop with correct target identification (15)
- ECS/ALB timeline, including task replacement (25)
- Successful post-recovery API verification (15)
- Correct readiness-failure demonstration and explanation (15)
- Incident report quality and cleanup evidence (15)

## Recovery troubleshooting
- No replacement: check ECS service events, quotas, available subnets/IPs, IAM execution role, image pull and task stopped reasons.
- `running=2` but target unhealthy: inspect `/ready`, target reason, task security group and logs; observe grace period and target-group thresholds.
- `CannotPullContainerError`: inspect image digest and ECR access, NAT route and logs endpoints.
- AWS CLI stop returns AccessDenied: insufficient `ecs:StopTask` permissions for your sandbox; don't widen IAM casually.
- `target_health=initial`: health checks are still warming up. Observe rather than guessing.
- No `stopped` tasks in collect output: ECS stopped-task visibility is limited, and the service might have already aged them out; use snapshots and service events.
- If ALB intermittently fails, record failures. Availability is not guaranteed by desiredCount alone.
