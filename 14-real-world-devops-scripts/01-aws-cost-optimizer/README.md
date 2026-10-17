# Real-World Script 01: Automated AWS Cloud Cost Optimizer

---

## 1. Real-World DevOps Problem Statement
In enterprise AWS environments, developers and automated CI pipelines spin up EC2 instances for testing, builds, and experiments. When those EC2 instances are terminated:
1. **Orphaned EBS Volumes**: By default, EBS volumes attached as secondary data disks (e.g. `/dev/xvdf`) are **not** deleted upon instance termination unless the `DeleteOnTermination` flag is explicitly configured. They remain in the `available` state indefinitely, quietly billing the company $0.08–$0.125 per GB/month.
2. **Abandoned EBS Snapshots**: Backup scripts and AMI creation jobs create snapshots daily. Months later, thousands of multi-gigabyte snapshots remain, accruing storage fees even though the parent instance and volume no longer exist.
3. **Financial Impact**: In mid-to-large AWS accounts, orphaned EBS volumes and stale snapshots routinely consume **$2,000 to $15,000+ per month** in pure financial waste.

---

## 2. Complete Code Implementation

See the full script in [aws_ebs_snapshot_cost_optimizer.py](file:///c:/Users/Demon%20Slayer/Documents/PythonForDevOps/14-real-world-devops-scripts/01-aws-cost-optimizer/aws_ebs_snapshot_cost_optimizer.py).

---

## 3. Deep-Dive Code Explanation: What Is It Doing?

### A. AWS Client Initialization with Adaptive Retries
```python
cfg = Config(
    region_name=region,
    retries={'max_attempts': 5, 'mode': 'adaptive'}
)
return boto3.client('ec2', config=cfg)
```
- Sets up an AWS EC2 client using `botocore.config.Config`.
- Uses `mode='adaptive'`, which actively throttles client-side request rates in response to AWS rate-limit signals (HTTP 429 / `RequestLimitExceeded`), preventing script crashes in large multi-account scans.

### B. Detecting Orphaned EBS Volumes
```python
page_iterator = paginator.paginate(
    Filters=[{'Name': 'status', 'Values': ['available']}]
)
```
- Queries the AWS EC2 API using server-side filtering `status=available`.
- Iterates over pages using AWS API Paginators to handle accounts with thousands of volumes without memory exhaustion.
- Checks resource tags: if an engineer has explicitly tagged a volume with `KeepAlive: true`, the script honors the tag and ignores the volume.

### C. Identifying Stale Snapshots with Date Math
```python
cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
```
- Uses timezone-aware UTC timestamps (`datetime.now(timezone.utc)`) to avoid time zone shift bugs.
- Filters snapshots owned exclusively by the current AWS account (`OwnerIds=['self']`), ignoring shared public snapshots.
- Compares `StartTime` against `cutoff_date` (e.g. 30 days old).

### D. Financial Projection Engine
- Calculates total GiB of unattached volumes and calculates approximate monthly savings using standard AWS storage tier coefficients ($0.08/GB for gp3, $0.05/GB for snapshots).
- Computes annual projected cost savings.

### E. Dry-Run Fail-Safe Execution
- The script defaults to **Dry-Run mode** (`--execute` required for actual deletion).
- In dry-run mode, all candidates are logged with full identifiers, sizes, and creation dates, preventing accidental production data loss.

---

## 4. Libraries Used & Why

| Library | Why It Was Chosen |
|:---|:---|
| `boto3` | The official AWS SDK for Python. Provides full API coverage for AWS EC2, EBS, and CloudWatch. |
| `botocore.config.Config` | Enables setting exponential backoff, retry limits, and client timeouts at the socket layer. |
| `argparse` | Standard library CLI argument parsing. Allows configuring regions, age thresholds, and dry-run flags without third-party dependencies. |
| `logging` | Standard library logging configured to emit structured JSON logs. Ensures output can be piped directly into AWS CloudWatch Logs or Datadog. |
| `datetime` | Precise, timezone-aware date arithmetic for calculating snapshot aging across UTC boundaries. |

---

## 5. Real-World Problems, Edge Cases & Code Fixes

### Problem 1: Snapshots Tied to Active AMIs
- **Real-World Incident**: An automated script attempts to delete a snapshot, but AWS rejects it with `ClientError: ResourceInUse: The snapshot snap-xxx is currently in use by ami-yyy`.
- **The Code Fix**: Before deleting any snapshot, query `ec2.describe_images(Filters=[{'Name': 'block-device-mapping.snapshot-id', 'Values': [snap_id]}])`. If any image references the snapshot, skip it and log the associated AMI.

### Problem 2: Race Condition on Volume Attachment
- **Real-World Incident**: A volume appears `available` during the initial scan, but an Auto Scaling group or Kubernetes CSI driver attaches it seconds later. Deleting it immediately causes volume corruption.
- **The Code Fix**: Always wrap deletion in a dedicated `try/except ClientError` block checking for `VolumeInUse`. Furthermore, enforce a minimum buffer period (e.g., only delete volumes that have been unattached for > 24 hours).

### Problem 3: AWS API Throttling (`RequestLimitExceeded`)
- **Real-World Incident**: Scanning an organization with 20,000 snapshots causes AWS to throttle the API, crashing the script mid-execution.
- **The Code Fix**: Implemented Boto3's `adaptive` retry mode in `Config(retries={'mode': 'adaptive'})`, which dynamically adjusts request velocity based on token bucket capacity.
