@echo off
set CLOUDFLARE_API_TOKEN=cfat_lVUjDxc627SN7J4qci0gn0mfLlybA75ECrRDvcuw00a2ae7e
set CLOUDFLARE_ACCOUNT_ID=bcbea5647c46bc2cf236023b6be7719d

echo Deploying TypeScript Worker...
cd C:\Users\LEGIONX\Downloads\nemesis\tracer_scripts\workers
call npx -y wrangler deploy > deploy_worker_log.txt 2>&1
echo Done Worker.

echo Deploying Python API...
cd C:\Users\LEGIONX\Downloads\nemesis\tracer_scripts\backend
call npx -y wrangler deploy > deploy_api_log.txt 2>&1
echo Done API.
