# The DevOps Engineer's Guide to Coding Independently with Official Docs

> **"A senior engineer does not memorize code. A senior engineer knows how to decompose problems, navigate official documentation in 30 seconds, and assemble the standard library into robust solutions."**

If you try to memorize 30 or 50 Python scripts for an interview, you will panic the moment an interviewer tweaks a requirement. But if you master **how to think, how to break down problems, and how to read the official documentation**, you can write any automation program from scratch with zero outside help.

This guide teaches you the exact mental framework, doc navigation system, and built-in Python inspection tools needed to code independently.

---

## 🧠 Phase 1: The 5-Step Problem Deconstruction Framework

Whenever an interviewer hands you a coding prompt, **do not start typing code immediately**. Follow this 5-step method:

```
┌─────────────────────────┐
│ 1. Define I/O Contract  │ What goes in? What comes out? Data types?
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 2. Map to Standard Lib  │ Which built-in module solves this? (re, os, heapq, socket)
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 3. Query Official Docs  │ Lookup module syntax, signatures, and return values
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 4. REPL Prototyping     │ Test small 1-line functions in python terminal with dir()/help()
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 5. Assemble & Protect   │ Add typing, timeouts, exception handling & edge cases
└─────────────────────────┘
```

### Step 1: Define the Input/Output Contract
Before writing code, write down the function signature and expected types in plain English:
* **Prompt**: *"Find all IP addresses in a log file with more than 5 failed logins."*
* **Input**: `log_lines: List[str]`, `threshold: int = 5`
* **Output**: `Dict[str, int]` (mapping offending IP -> count)
* **Edge cases**: Empty log lines, malformed lines, lines from successful logins.

### Step 2: The DevOps Standard Library Mental Map
Python’s standard library is called "batteries included". 90% of DevOps interview problems are solved using just 10 modules:

| What you need to do | Standard Library Module | Official Docs Section |
|:---|:---|:---|
| Text patterns, log scraping, IP extraction | `re` | `docs.python.org/3/library/re.html` |
| Frequency counting, grouping, queues, stacks | `collections` | `docs.python.org/3/library/collections.html` |
| Top-K elements, priority merging, min-heap | `heapq` | `docs.python.org/3/library/heapq.html` |
| Files, directories, paths cross-platform | `pathlib`, `os`, `shutil` | `docs.python.org/3/library/pathlib.html` |
| Subnet checks, CIDR matching, IP validation | `ipaddress` | `docs.python.org/3/library/ipaddress.html` |
| Timeouts, exponential backoff, dates | `time`, `datetime`, `random` | `docs.python.org/3/library/datetime.html` |
| Port checks, socket connections, TCP probes | `socket`, `ssl` | `docs.python.org/3/library/socket.html` |
| Safe command execution (CLI tools) | `subprocess` | `docs.python.org/3/library/subprocess.html` |
| Safe file buffers, scratch files | `tempfile` | `docs.python.org/3/library/tempfile.html` |
| Concurrent network/disk sweeps | `concurrent.futures`, `threading` | `docs.python.org/3/library/concurrent.futures.html` |
| Cryptography, checksums | `hashlib`, `hmac` | `docs.python.org/3/library/hashlib.html` |
| CLI arguments with flags | `argparse` | `docs.python.org/3/library/argparse.html` |

---

## 🔍 Phase 2: How to Navigate Official Docs in 30 Seconds

When allowed to reference [docs.python.org](https://docs.python.org/3/) or cloud SDK documentation, **do not read the entire page**. Look for three specific sections:

### 1. The Function Signature Block
Every official doc entry looks like this:
```python
re.search(pattern, string, flags=0) -> Match object or None
```
What this tells you immediately:
- **`pattern`**: The regex string or compiled pattern.
- **`string`**: The target line you are scanning.
- **Return value**: A `Match` object if found, or `None` if not found.
*Immediate Coding Rule*: You must write `match = re.search(...)` followed by `if match:`, or your script will throw `AttributeError: 'NoneType' object has no attribute 'group'`.

### 2. The Return Object Methods
Click or scroll directly to the return object (e.g., `Match` objects):
- `match.group(0)`: The full match string.
- `match.group(1)`: The first capture group `(...)`.
- `match.groupdict()`: All named capture groups `(?P<name>...)` as a clean dictionary.

### 3. The "Examples" / "Recipes" Section
Every Python doc page ends with a **"Cookbook" or "Examples" section**.
- Need a sliding window? Check the `collections.deque` examples at the bottom of the page.
- Need a priority queue? Check the `heapq` examples at the bottom of the page.
- Need a subprocess runner? Check the `subprocess` examples at the bottom of the page.
The Python documentation team already wrote canonical, idiomatic snippets for you!

---

## 💻 Phase 3: The Secret Weapon — The Interactive Python REPL

In live interviews (and on remote servers), you have access to the Python interactive shell. You do not even need internet access to read docs!

### 1. `help(module_or_function)`
Inside your terminal, open Python and query built-in docstrings directly:
```bash
$ python3
>>> import re
>>> help(re.search)
Help on function search in module re:
search(pattern, string, flags=0)
    Scan through string looking for a match to the pattern, returning
    a corresponding match object, or None if no match was found.
```

### 2. `dir(object)` — Discovering Methods on the Fly
Forgot what methods an IP address or socket object has? Use `dir()`:
```python
>>> import ipaddress
>>> net = ipaddress.ip_network("192.168.1.0/24")
>>> [m for m in dir(net) if not m.startswith("_")]
['broadcast_address', 'hosts', 'is_private', 'netmask', 'network_address', 'num_addresses', 'overlaps', 'prefixlen', 'subnets', 'supernet']
```
Instantly you discover `net.is_private`, `net.num_addresses`, and `net.netmask`!

### 3. Interactive Prototyping (`python -i script.py`)
Run your script with the `-i` (interactive) flag:
```bash
python -i my_script.py
```
This executes your code and leaves the Python terminal open with all variables in memory so you can inspect them live!

---

## 🛠️ Phase 4: Walkthrough — Solving a Problem from Zero Using Docs

Let’s walk through how a Senior SRE writes a solution from scratch using **only** documentation.

### The Problem:
> *"Write a program that takes a list of microservices and their dependencies, and outputs the exact build/deploy order. If there is a circular dependency (e.g. A requires B, B requires A), fail with an error."*

### Step 1: Deconstruct
- **Problem Type**: Directed Acyclic Graph (DAG) / Topological Sort.
- **Input**: `{"web": ["api", "cache"], "api": ["db"], "cache": [], "db": []}`
- **Output**: Order list: `["db", "api", "cache", "web"]`

### Step 2: Open Docs (`docs.python.org/3/library/collections.html`)
- You remember that graph traversals require:
  1. A graph mapping nodes to outgoing edges (`collections.defaultdict(list)`).
  2. In-degree tracking (`collections.defaultdict(int)`).
  3. A queue to process nodes with 0 dependencies (`collections.deque`).
- Search `collections` page for `defaultdict` and `deque`.
- Doc says: `deque.append()` adds to right, `deque.popleft()` pops from left in $O(1)$ time.

### Step 3: Write the Mental Algorithm (Kahn's Algorithm)
1. Calculate in-degree (number of incoming dependencies) for each node.
2. Put all nodes with in-degree 0 into a `deque`.
3. While queue is not empty:
   - Pop node $U$, append to `deploy_order`.
   - For every neighbor $V$ that depends on $U$, decrement in-degree of $V$.
   - If in-degree of $V$ becomes 0, add $V$ to queue.
4. If `len(deploy_order) != total_nodes`, there is a circular dependency cycle!

### Step 4: Write the Code
```python
from collections import defaultdict, deque
from typing import Dict, List

def resolve_deploy_order(dependencies: Dict[str, List[str]]) -> List[str]:
    # Invert dependency mapping: if web depends on api, api must build before web
    # Edge: dependency -> service
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set(dependencies.keys())

    for service, deps in dependencies.items():
        for dep in deps:
            all_nodes.add(dep)
            graph[dep].append(service)
            in_degree[service] += 1

    # Initialize queue with nodes that have 0 incoming dependencies
    queue = deque([node for node in all_nodes if in_degree[node] == 0])
    deploy_order = []

    while queue:
        current = queue.popleft()
        deploy_order.append(current)

        for dependent in graph[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(deploy_order) != len(all_nodes):
        raise ValueError("Circular dependency detected! Cannot determine deployment order.")

    return deploy_order
```
*You solved a Hard/Medium interview question in 30 lines of clean Python using only `collections`!*

---

## 📑 Phase 5: The DevOps Standard Library "When to Use What" Cheatsheet

### 1. For Strings & Text
* `line.strip()`: Remove whitespace/newlines.
* `line.split(" ", 1)`: Split into only 2 pieces (keeps the rest intact).
* `str.join(list)`: Combine tokens.
* `re.compile(r'...')`: Compile regex once for loops.
* `match.groupdict()`: Named regex groups into dict.

### 2. For Collections & Counting
* `collections.Counter(iterable)`: Count occurrences in 1 line; `.most_common(N)` for top items.
* `collections.defaultdict(list)`: Group items by key without `if key not in d:` checks.
* `collections.deque(maxlen=N)`: High-speed sliding window buffer.
* `heapq.heappush()` / `heapq.heappop()`: Priority queues and K-way merging.

### 3. For File & Disk Operations
* `pathlib.Path(dir).glob("**/*.log")`: Recursive file search.
* `path.stat().st_size`: Size in bytes.
* `path.stat().st_mtime`: Modification time (compare with `time.time() - (days * 86400)`).
* `shutil.disk_usage("/")`: Free/used space in 1 line.

### 4. For APIs & Network
* `urllib.parse.urlparse(url)`: Extract scheme, hostname, port, and path cleanly.
* `socket.create_connection((host, port), timeout=...)`: Fast TCP port check.
* `requests.Session()` + `HTTPAdapter(max_retries=...)`: Connection pooling & retries.

### 5. For Cloud Automation (AWS Boto3 Docs)
When opening [boto3.amazonaws.com](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html):
* Click the service on the left navigation (e.g. `EC2`, `S3`).
* Scroll to **Paginators** (e.g., `describe_instances`, `list_objects_v2`).
* Copy the 4-line paginator pattern:
  ```python
  paginator = client.get_paginator('describe_volumes')
  for page in paginator.paginate(Filters=[...]):
      for item in page['Volumes']: ...
  ```

---

## 🎯 The Mindset for Success
1. **Never panic**: Read the prompt twice. Clarify input and output.
2. **State your plan out loud**: *"I will use `collections.defaultdict` to group by IP, and then `heapq` or `Counter` to get the top 5."* Interviewers award major points for structure before code.
3. **Write defensive code**: Check for `None`, check for empty lists, use timeouts, wrap API calls in `try/except`.
4. **Test your code on paper or in REPL**: Run through a 2-item example line-by-line.
