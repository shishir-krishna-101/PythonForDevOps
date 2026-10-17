# 10 - Cloud Automation with AWS Boto3 for DevOps

---

## 1. What It Is
`boto3` is the official AWS SDK for Python. It provides Python developers and DevOps engineers with direct programmatic control over more than 200 AWS services:
- **`boto3.Session`**: Encapsulates configuration state and AWS credentials (access key, secret key, region, IAM profile).
- **Client Interface (`boto3.client('ec2')`)**: Low-level 1:1 mapping to AWS REST APIs. Returns raw dictionaries; supports paginators and waiters.
- **Resource Interface (`boto3.resource('s3')`)**: Higher-level, object-oriented abstraction with OOP attributes and sub-resource collections.
- **Paginators (`client.get_paginator(...)`)**: Built-in mechanism to iterate seamlessly across multi-page API responses (e.g., accounts with 50,000 S3 objects or 5,000 EC2 instances).
- **Waiters (`client.get_waiter(...)`)**: Polling mechanisms that block execution until a cloud resource reaches a desired state (e.g. `instance_running`).

---

## 2. What Is the Use of It in DevOps?
FinOps, CloudOps, and SRE teams rely on Boto3 daily:
1. **Cloud Cost Optimization**: Automatically stop non-production EC2 instances outside business hours (7 PM to 7 AM) and delete unattached EBS volumes older than 7 days.
2. **Tag Governance & Compliance**: Audit all AWS resources to ensure mandatory tags (`Environment`, `Owner`, `CostCenter`, `Project`) are present; alert or terminate non-compliant resources.
3. **Automated S3 Archival & Backup**: Stream database snapshots to S3, enforce Server-Side Encryption (KMS), and configure S3 Glacier lifecycle transitions.
4. **Security & IAM Auditing**: Scan IAM users for access keys older than 90 days, check for open security group ports (`0.0.0.0/0` on port 22/3389), and generate audit reports.

---

## 3. How to Use It

### Clients vs Resources
```python
import boto3

# Low-level client (returns JSON-like dicts)
ec2_client = boto3.client('ec2', region_name='us-east-1')
response = ec2_client.describe_instances()

# High-level resource (object-oriented)
s3_resource = boto3.resource('s3')
bucket = s3_resource.Bucket('my-devops-backup-bucket')
for obj in bucket.objects.all():
    print(obj.key, obj.size)
```

### Paginating Safely Through Thousands of Resources
```python
import boto3

s3_client = boto3.client('s3')
paginator = s3_client.get_paginator('list_objects_v2')

# Avoids memory exhaustion by streaming pages
for page in paginator.paginate(Bucket='prod-logs-bucket'):
    for item in page.get('Contents', []):
        if item['Size'] > 1024 * 1024 * 100: # > 100 MB
            print(f"Large object: {item['Key']}")
```

### Defensive Error Handling with `botocore.exceptions.ClientError`
```python
import boto3
from botocore.exceptions import ClientError

try:
    ec2 = boto3.client('ec2')
    ec2.terminate_instances(InstanceIds=['i-invalid12345'])
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_msg = e.response['Error']['Message']
    print(f"AWS API Error [{error_code}]: {error_msg}")
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Enforcing Non-Production EC2 Shutdown Schedule
```python
import boto3

def stop_idle_dev_instances(region: str = "us-east-1"):
    ec2 = boto3.client("ec2", region_name=region)
    
    # Filter for running instances tagged Environment=dev
    filters = [
        {"Name": "instance-state-name", "Values": ["running"]},
        {"Name": "tag:Environment", "Values": ["dev", "development"]}
    ]
    
    paginator = ec2.get_paginator("describe_instances")
    instances_to_stop = []
    
    for page in paginator.paginate(Filters=filters):
        for reservation in page["Reservations"]:
            for inst in reservation["Instances"]:
                instances_to_stop.append(inst["InstanceId"])

    if instances_to_stop:
        print(f"Stopping dev instances to save cost: {instances_to_stop}")
        ec2.stop_instances(InstanceIds=instances_to_stop)
    else:
        print("No running dev instances found.")
```

### Step B: Using Waiters for Pipeline Automation
```python
import boto3

ec2 = boto3.client('ec2')
instance_id = "i-0123456789abcdef0"

print(f"Starting instance {instance_id}...")
ec2.start_instances(InstanceIds=[instance_id])

# Wait until instance is running before proceeding to SSH
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])
print("Instance is now running!")
```

---

## 5. DevOps Hands-On Example: S3 Bucket Security & Lifecycle Auditor

```python
#!/usr/bin/env python3
"""
AWS Boto3 Cloud Security & S3 Auditor.
Inspects S3 buckets for public access block configuration and server-side encryption.
"""
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def audit_s3_buckets():
    print("=== AWS S3 Bucket Security & Compliance Audit ===")
    
    try:
        s3 = boto3.client('s3')
        buckets_resp = s3.list_buckets()
    except NoCredentialsError:
        print("[SKIP] No AWS credentials configured (AWS_ACCESS_KEY_ID / ~/.aws/credentials).")
        print("Demonstrating simulated audit structure:")
        simulated_buckets = [{"Name": "prod-customer-data"}, {"Name": "dev-temporary-logs"}]
        for b in simulated_buckets:
            print(f"  * Bucket: {b['Name']} -> [SIMULATED CHECK] SSE-KMS Encrypted")
        return

    buckets = buckets_resp.get('Buckets', [])
    print(f"Discovered {len(buckets)} S3 buckets in account.\n")

    for b in buckets:
        name = b['Name']
        print(f"Auditing Bucket: '{name}'")
        
        # Check Public Access Block
        try:
            pab = s3.get_public_access_block(Bucket=name)
            pab_config = pab.get('PublicAccessBlockConfiguration', {})
            all_blocked = all(pab_config.values())
            print(f"  Public Access Block : {'[COMPLIANT]' if all_blocked else '[WARN] Incomplete Block'}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                print("  Public Access Block : [ALERT] No Public Access Block configured!")
            else:
                print(f"  Public Access Block : Error: {e.response['Error']['Code']}")

        # Check Encryption
        try:
            enc = s3.get_bucket_encryption(Bucket=name)
            rules = enc.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
            print(f"  Encryption Status   : [COMPLIANT] Enforced ({len(rules)} rule(s))")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                print("  Encryption Status   : [ALERT] No default server-side encryption!")
            else:
                print(f"  Encryption Status   : Error: {e.response['Error']['Code']}")

def main():
    audit_s3_buckets()

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: What is the architectural difference between a Boto3 Client and a Boto3 Resource?
**Answer:**
- **Client**: Low-level service client that closely matches the AWS service APIs (1:1 with REST endpoints). Returns raw nested dictionaries. Supports paginators and waiters. Always up-to-date with new AWS features.
- **Resource**: Higher-level, object-oriented abstraction. Instead of calling `ec2.describe_instances()`, you do `ec2.instances.all()`. Instances are Python objects with attributes (`instance.id`, `instance.state`).
*Best Practice*: Clients are preferred for production DevOps automation because they have 100% AWS API coverage, lower overhead, and native paginator support.

### Q2: Why should you avoid calling `list_objects` or `describe_instances` without a Paginator in production?
**Answer:**
AWS API methods limit responses to a maximum batch size (e.g., 1,000 objects for S3, 1,000 instances for EC2). If an enterprise S3 bucket holds 500,000 objects, calling `list_objects_v2` without pagination returns only the first 1,000 objects, silently ignoring the other 499,000. Using `client.get_paginator('list_objects_v2')` transparently iterates through `NextContinuationToken`.

### Q3: How do you handle AWS API Throttling (`RequestLimitExceeded` / HTTP 429)?
**Answer:**
1. Configure Boto3's built-in `Config` with `adaptive` retry mode:
```python
from botocore.config import Config
config = Config(
    retries={
        'max_attempts': 10,
        'mode': 'adaptive' # Automatically throttles client based on AWS server response
    }
)
client = boto3.client('ec2', config=config)
```
2. Implement exponential backoff with jitter if writing custom loops.
