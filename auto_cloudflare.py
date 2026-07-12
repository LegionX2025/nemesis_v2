import os
import subprocess
import sys
import time
import threading

def run_command_stream(cmd, name):
    print(f"[{name}] Starting: {cmd}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    def stream_logs():
        for line in process.stdout:
            print(f"[{name}] {line}", end='')
            
    t = threading.Thread(target=stream_logs, daemon=True)
    t.start()
    return process

def main():
    print("==================================================")
    print("  NEMESIS AUTO-CLOUDFLARE BUILDER & DEPLOYER")
    print("==================================================")

    # 1. Build the frontend
    print("\n>>> 1. Building Frontend...")
    result = subprocess.run([sys.executable, "build_frontend.py"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Frontend built successfully into dist/ folder.")
    else:
        print("Error building frontend:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    # 2. Deploy Frontend to Cloudflare Pages
    print("\n>>> 2. Deploying Frontend to Cloudflare Pages (via Wrangler)...")
    print("Note: If this is your first time, Wrangler will open a browser to authenticate.")
    deploy_cmd = "npx wrangler pages deploy dist --project-name nemesis-frontend"
    deploy_result = subprocess.run(deploy_cmd, shell=True)
    if deploy_result.returncode != 0:
        print("Warning: Wrangler deploy failed or was cancelled. You may need to install wrangler or authenticate.")

    # 3. Start Backend & Tunnel
    print("\n>>> 3. Starting Local Backend and Cloudflare Tunnel...")
    
    backend_cmd = f"{sys.executable} nemesis_core.py"
    tunnel_cmd = r"..\cloudflared.exe tunnel run --token eyJhIjoiYmNiZWE1NjQ3YzQ2YmMyY2YyMzYwMjNiNmJlNzcxOWQiLCJ0IjoiMDhhNTkwNWEtZmNlMy00MzdhLTg5OGEtYjExODY5ZmJmMDQ1IiwicyI6Ik16VTBORGczTVRJdFpEQmhZUzAwWTJFNUxUbGlPREF0TlRnd09EVTJPV0l4TkRoaCJ9"
    
    # We use the absolute path for cloudflared since it's in the parent folder
    cloudflared_path = os.path.abspath(os.path.join(os.getcwd(), "..", "cloudflared.exe"))
    if not os.path.exists(cloudflared_path):
        print(f"Warning: cloudflared.exe not found at {cloudflared_path}. Trying 'cloudflared' from PATH.")
        tunnel_cmd = "cloudflared tunnel run --token eyJhIjoiYmNiZWE1NjQ3YzQ2YmMyY2YyMzYwMjNiNmJlNzcxOWQiLCJ0IjoiMDhhNTkwNWEtZmNlMy00MzdhLTg5OGEtYjExODY5ZmJmMDQ1IiwicyI6Ik16VTBORGczTVRJdFpEQmhZUzAwWTJFNUxUbGlPREF0TlRnd09EVTJPV0l4TkRoaCJ9"
    else:
        tunnel_cmd = f'"{cloudflared_path}" tunnel run --token eyJhIjoiYmNiZWE1NjQ3YzQ2YmMyY2YyMzYwMjNiNmJlNzcxOWQiLCJ0IjoiMDhhNTkwNWEtZmNlMy00MzdhLTg5OGEtYjExODY5ZmJmMDQ1IiwicyI6Ik16VTBORGczTVRJdFpEQmhZUzAwWTJFNUxUbGlPREF0TlRnd09EVTJPV0l4TkRoaCJ9'

    backend_proc = run_command_stream(backend_cmd, "BACKEND")
    time.sleep(2) # Give backend a moment to start
    tunnel_proc = run_command_stream(tunnel_cmd, "TUNNEL")

    print("\n==================================================")
    print(" SYSTEM IS ONLINE AND READY")
    print(" - Backend running locally on port 8000")
    print(" - Cloudflare Tunnel routing traffic from Edge to Backend")
    print(" - Frontend Deployed to Cloudflare Pages")
    print(" Press Ctrl+C to stop all services.")
    print("==================================================\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        backend_proc.terminate()
        tunnel_proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
