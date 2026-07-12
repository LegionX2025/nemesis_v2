import re

with open("nemesis_core.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add queue and resolved set
content = content.replace("self.broadcast_queue = asyncio.Queue() # HIGH PERFORMANCE BUFFER", "self.broadcast_queue = asyncio.Queue()\n        self.label_queue = asyncio.Queue()\n        self.resolved_labels = set()")

# 2. Add oklink import
if "import oklink_scraper" not in content:
    content = content.replace("import importlib.util", "import importlib.util\nimport oklink_scraper")

# 3. Add label_worker function
worker_code = """
async def label_worker(state, ws_list):
    while not state.target_reached or not state.label_queue.empty():
        try:
            chain, address = await asyncio.wait_for(state.label_queue.get(), timeout=1.0)
            if address in state.resolved_labels:
                state.label_queue.task_done()
                continue
            
            state.resolved_labels.add(address)
            
            try:
                res = await asyncio.to_thread(oklink_scraper.scrape_oklink_tags, chain, address)
                if res and res.get("attributionTags"):
                    tags = res["attributionTags"]
                    label_str = " | ".join(tags)
                    # Classify entity roughly based on tag heuristics
                    classification = "Unknown Entity"
                    cex_keywords = ["exchange", "binance", "okx", "huobi", "kraken", "coinbase", "kucoin", "bitfinex"]
                    defi_keywords = ["defi", "dex", "swap", "pool", "liquidity", "router", "curve", "uniswap"]
                    mixer_keywords = ["mixer", "tornado", "coinjoin", "wasabi"]
                    bridge_keywords = ["bridge", "multichain", "across", "stargate"]
                    
                    is_cex = any(k in label_str.lower() for k in cex_keywords)
                    is_defi = any(k in label_str.lower() for k in defi_keywords)
                    is_mixer = any(k in label_str.lower() for k in mixer_keywords)
                    is_bridge = any(k in label_str.lower() for k in bridge_keywords)
                    
                    if is_mixer: classification = "Mixer Protocol"
                    elif is_cex: classification = "Exchange / Custodial"
                    elif is_bridge: classification = "Bridge Endpoint"
                    elif is_defi: classification = "DeFi Liquidity Pool"
                    
                    payload = {
                        "type": "NODE_UPDATE", 
                        "node": address, 
                        "tags": tags,
                        "label_str": label_str,
                        "classification": classification,
                        "is_cex": is_cex,
                        "is_suspect": is_mixer
                    }
                    for ws in list(ws_list):
                        try: await ws.send_json(payload)
                        except: pass
            except Exception as e:
                print(f"Error in label worker: {e}")
            
            state.label_queue.task_done()
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            pass

async def ws_broadcaster(state, ws_list):
"""
if "def label_worker" not in content:
    content = content.replace("async def ws_broadcaster(state, ws_list):", worker_code)

# 4. Enqueue in process_hop
enqueue_code = """
        state.max_depth = max(state.max_depth, depth)
        
        if target_entity not in state.resolved_labels:
            await state.label_queue.put((chain, target_entity))
            
        state.total_hops += 1
"""
content = content.replace("        state.max_depth = max(state.max_depth, depth)\n        state.total_hops += 1", enqueue_code)

# 5. Start the label_worker task
start_worker_code = """
        broadcaster_task = asyncio.create_task(ws_broadcaster(state, ws_list))
        label_task = asyncio.create_task(label_worker(state, ws_list))
"""
if "label_task = asyncio.create_task" not in content:
    content = content.replace("broadcaster_task = asyncio.create_task(ws_broadcaster(state, ws_list))", start_worker_code)

# 6. Wait for the label_worker task
end_worker_code = """
        await state.broadcast_queue.join()
        await state.label_queue.join()
        await broadcaster_task
        await label_task
"""
if "await label_task" not in content:
    content = content.replace("await state.broadcast_queue.join()\n        await broadcaster_task", end_worker_code)

with open("nemesis_core.py", "w", encoding="utf-8") as f:
    f.write(content)

print("nemesis_core.py patched.")
