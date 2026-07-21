import os
import subprocess

def main():
    root_dir = r"c:\Users\LEGIONX\Downloads\cases\local_deploy\nemesis_full"
    os.chdir(root_dir)

    print("[*] Installing tailwindcss...")
    subprocess.run(["npm", "install", "tailwindcss"], shell=True)

    print("[*] Creating tailwind.config.js...")
    with open("tailwind.config.js", "w") as f:
        f.write("""
module.exports = {
  content: [
    "./**/*.html",
    "./**/*.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
""")

    print("[*] Creating input.css...")
    with open("input.css", "w") as f:
        f.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")

    print("[*] Running Tailwind CLI to build tailwind.css...")
    subprocess.run(["npx", "tailwindcss", "-i", "input.css", "-o", "tailwind.css", "--minify"], shell=True)

    print("[*] Patching nemesis_core.py to serve tailwind.css...")
    with open(os.path.join("backend", "nemesis_core.py"), "r", encoding="utf-8") as f:
        core_code = f.read()
    
    if '@app.get("/tailwind.css")' not in core_code:
        # Find where nemesis-ui.css is defined
        inject_marker = 'async def get_css(): \n    if os.path.exists("nemesis-ui.css"): return FileResponse("nemesis-ui.css")\n    return JSONResponse({"status": "not found"}, status_code=404)\n'
        tailwind_route = '\n@app.get("/tailwind.css")\nasync def get_tailwind():\n    if os.path.exists("tailwind.css"): return FileResponse("tailwind.css")\n    return JSONResponse({"status": "not found"}, status_code=404)\n'
        if inject_marker in core_code:
            core_code = core_code.replace(inject_marker, inject_marker + tailwind_route)
            with open(os.path.join("backend", "nemesis_core.py"), "w", encoding="utf-8") as f:
                f.write(core_code)
            print("[+] Patched nemesis_core.py successfully.")
        else:
            print("[-] Could not find inject marker for nemesis_core.py.")
    
    print("[*] Patching HTML files to replace CDN and upgrade Font Awesome...")
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(subdir, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    changed = False
                    if '<script src="https://cdn.tailwindcss.com"></script>' in content:
                        content = content.replace('<script src="https://cdn.tailwindcss.com"></script>', '<link rel="stylesheet" href="/tailwind.css">')
                        changed = True
                    
                    if "font-awesome/6.4.0" in content:
                        content = content.replace("font-awesome/6.4.0", "font-awesome/6.5.2")
                        changed = True
                        
                    if changed:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"[+] Patched {file}")
                except Exception as e:
                    print(f"[-] Error patching {file}: {e}")

if __name__ == "__main__":
    main()
