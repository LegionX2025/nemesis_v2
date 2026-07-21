import os
import subprocess

def deploy():
    os.environ["CLOUDFLARE_API_TOKEN"] = "cfat_5n4KEasKCRbb8kQGAwqCNsVYjy6ROZls3FWSg6Ly54012944"
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "bcbea5647c46bc2cf236023b6be7719d"
    
    with open(".cfignore", "w") as f:
        f.write("""
*.py
*.bat
*.exe
backend/
workers/
.venv/
__pycache__/
.git/
test_results/
test_results_wallets/
""")
    print("[*] Deploying to Cloudflare Pages (nemesis-frontend)...")
    subprocess.run(["npx", "wrangler", "pages", "deploy", ".", "--project-name", "nemesis-frontend"], shell=True)

if __name__ == "__main__":
    deploy()
