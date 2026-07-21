import os
import shutil
import subprocess

def build_and_deploy():
    dist_dir = "dist_pages"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy relevant files
    for file in os.listdir("."):
        if file.endswith((".html", ".js", ".css", ".png", ".jpeg", ".jpg", ".svg", ".ico", ".woff", ".woff2")):
            if os.path.isfile(file):
                shutil.copy2(file, dist_dir)
                
    # Copy specific folders if they contain static assets
    for folder in ["frontend", "logo"]:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(dist_dir, folder), dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.json'))
    if os.path.exists("public"):
        shutil.copytree("public", os.path.join(dist_dir, "public"), dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.json', '*.jsonl'))
            
    print("[*] Deploying from dist_pages...")
    os.environ["CLOUDFLARE_API_TOKEN"] = "cfat_5n4KEasKCRbb8kQGAwqCNsVYjy6ROZls3FWSg6Ly54012944"
    os.environ["CLOUDFLARE_ACCOUNT_ID"] = "bcbea5647c46bc2cf236023b6be7719d"
    subprocess.run(["npx", "wrangler", "pages", "deploy", "dist_pages", "--project-name", "nemesis-frontend"], shell=True)

if __name__ == "__main__":
    build_and_deploy()
