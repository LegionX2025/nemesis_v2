@echo off
set CLOUDFLARE_API_TOKEN=cfat_lVUjDxc627SN7J4qci0gn0mfLlybA75ECrRDvcuw00a2ae7e
set CLOUDFLARE_ACCOUNT_ID=bcbea5647c46bc2cf236023b6be7719d
cd C:\Users\LEGIONX\Downloads\nemesis\tracer_scripts\backend
call npx -y wrangler kv namespace create "CACHE_KV" > kv_out.txt 2>&1
call npx -y wrangler d1 create "nemesis-d1" > d1_out.txt 2>&1
