import os
import subprocess
import json
import re
import sys
import time

def run_cmd(cmd, shell=True, capture=False):
    print(f"\n[EXEC] {cmd}")
    result = subprocess.run(cmd, shell=shell, text=True, capture_output=capture)
    if result.returncode != 0 and not capture:
        print(f"[FAIL] Command failed: {cmd}")
    return result.stdout if capture else result.returncode

def extract_id(text, pattern):
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def main():
    base_dir = os.getcwd()
    workers_dir = os.path.join(base_dir, "workers")
    
    os.chdir(base_dir)
    print("=====================================================")
    print("    NEMESIS CLOUDFLARE INFRASTRUCTURE DEPLOYER")
    print("=====================================================")
    
    # Check wrangler installation
    print("\n[*] Checking Wrangler CLI...")
    version_out = run_cmd("npx wrangler --version", capture=True)
    if "not recognized" in version_out or "No such file" in version_out:
        print("[!] Wrangler not found. Installing wrangler globally...")
        run_cmd("npm install -g wrangler")
    else:
        print(f"[+] Wrangler version: {version_out.strip()}")
        
    # Set Cloudflare Environment Variables for auto-authentication
    os.environ["CLOUDFLARE_API_TOKEN"] = "cfat_5n4KEasKCRbb8kQGAwqCNsVYjy6ROZls3FWSg6Ly54012944"
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "bcbea5647c46bc2cf236023b6be7719d"
    
    print("\n[*] Cloudflare API Token and Account ID injected successfully for automatic deployments.")

    # 1. D1 Database
    print("\n[+] Creating Cloudflare D1 Database (NEMESIS_DB)...")
    d1_out = run_cmd('npx wrangler d1 create NEMESIS_DB', capture=True)
    d1_id = extract_id(d1_out, r'database_id = "([^"]+)"')
    if not d1_id:
        print("    [!] Could not extract D1 ID. Looking for existing DB...")
        d1_list = run_cmd('npx wrangler d1 list', capture=True)
        for line in d1_list.split('\n'):
            if "NEMESIS_DB" in line:
                parts = line.split()
                if len(parts) > 1:
                    d1_id = parts[0]
                    break
    print(f"    -> D1 ID: {d1_id}")

    # 2. KV Namespace
    print("\n[+] Creating Cloudflare KV Namespace (NEMESIS_CACHE)...")
    kv_out = run_cmd('npx wrangler kv:namespace create "NEMESIS_CACHE"', capture=True)
    kv_id = extract_id(kv_out, r'id = "([^"]+)"')
    if not kv_id:
        print("    [!] Could not extract KV ID. Searching for existing...")
        kv_list = run_cmd('npx wrangler kv:namespace list', capture=True)
        try:
            ns_list = json.loads(kv_list)
            for ns in ns_list:
                if "NEMESIS_CACHE" in ns.get("title", ""):
                    kv_id = ns.get("id")
                    break
        except:
            pass
    print(f"    -> KV ID: {kv_id}")

    # 3. Queue
    print("\n[+] Creating Cloudflare Queue (nemesis-trace-queue)...")
    queue_out = run_cmd('npx wrangler queues create nemesis-trace-queue', capture=True)
    if "already taken" in queue_out or "already exists" in queue_out:
        print("    -> Queue already exists, skipping creation.")

    # 4. Generate wrangler.toml
    print("\n[+] Generating workers/wrangler.toml configuration...")
    toml_content = f"""name = "nemesis-backend"
main = "src/index.ts"
compatibility_date = "2024-03-20"

[[durable_objects.bindings]]
name = "INVESTIGATION_SESSION"
class_name = "InvestigationSession"

[[migrations]]
tag = "v1"
new_sqlite_classes = ["InvestigationSession"]

[[queues.producers]]
binding = "TRACE_QUEUE"
queue = "nemesis-edge-trace-queue"

# [[queues.consumers]]
# queue = "nemesis-edge-trace-queue"
# max_batch_size = 10
# max_batch_timeout = 5
# max_retries = 3

[[d1_databases]]
binding = "NEMESIS_DB"
database_name = "NEMESIS_DB"
database_id = "{d1_id if (d1_id and d1_id.strip() != '│') else 'ec376c57-5dce-496b-8b55-db6975b52acb'}"

[[kv_namespaces]]
binding = "NEMESIS_CACHE"
id = "{kv_id if kv_id else 'f4099ea1458e4e62ba838734f172846f'}"

[vars]
# You must set your Python API URL manually if using Cloudflare Tunnels
PYTHON_API_URL = "http://127.0.0.1:8000"
"""
    with open(os.path.join(workers_dir, "wrangler.toml"), "w") as f:
        f.write(toml_content)
    
    # 5. Deploy Worker
    print("\n[+] Deploying API Gateway Edge Worker...")
    os.chdir(workers_dir)
    run_cmd("npm install")
    worker_out = run_cmd("npx wrangler deploy", capture=True)
    print(worker_out)
    
    # Extract Worker URL
    worker_url = None
    match = re.search(r'https://nemesis-backend\.[^\s]+\.workers\.dev', worker_out)
    if match:
        worker_url = match.group(0)
        print(f"\n    [SUCCESS] Edge Worker Deployed at: {worker_url}")
    else:
        print("\n    [!] WARNING: Could not extract Worker URL!")
        os.chdir(base_dir)
    
    # 6. Deploy Frontend Pages
    print("\n[+] Deploying Frontend to Cloudflare Pages...")
    os.chdir(base_dir)
    print("    -> Deploying 'frontend' directory to Cloudflare Pages (nemesis-frontend)...")
    pages_out = run_cmd('npx wrangler pages deploy frontend --project-name nemesis-frontend', capture=True)
    print(pages_out)

    print("\n=====================================================")
    print("    DEPLOYMENT AUTOMATION COMPLETE")
    print("=====================================================")

if __name__ == "__main__":
    main()
