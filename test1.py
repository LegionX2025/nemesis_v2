import json
import re

raw_input = """bc1qpa8n0a5ckt7wkdw3cn8eklsz3z0kn89knme5a9		1.6M
ra58paZqDhh2e6LtA4VPQEgAztUz3Z3urq		432K XRP
"bc1qcrdrmxx49pfzrmltx6my4cp62n6t4e58jeu0y7
"		0.7 M USD
0x159a861a3f0838adb1e6895886c7a0be7158be89		"88.2381 ETH
"
 0x2042404183ecd9610da5b251bb5f6e93eb9d3e08		$50,000.00
"uThZSCB2R8UQXHuPKPQLrRC5n7VTdSqUrJDQuoJsNum ,6vMuna31vRDs9u9RAEF8UeCSs9CNu6j4LkXpe4Ko1gBQ ,G2YxRa6wt1qePMwfJzdXZG62ej4qaTC7YURzuh2Lwd3t ,6vMuna31vRDs9u9RAEF8UeCSs9CNu6j4LkXpe4Ko1gBQ ,J7RBLx4gr5QisTidhJEzMj4awHz2ajwWKVREwN2J2TKR, uThZSCB2R8UQXHuPKPQLrRC5n7VTdSqUrJDQuoJsNum
"		
0x60E760222474A10f378cD53A5Bcd2CBd5a70eD1F, 0x0ed649357AbdAaA0222fE452B50D61D3E4a263a8		$44,000 - $45,000
0x6f00b583914fb35d314b36d2d914c145210be24e		
0x53556d7f1553Fa43D446D5363426447c40EDeAb3		$134,900.00
TNcykrU6R99SrR5BnxaqtDZe1V7o2sf664		
0x13d2d1f8e62f1f57eab648076583d7ce9f2af867		$400k
0x7CA30EEE61DD4E2356B2aE59718C23C3C470D3bB		$340k
0xf006878B4232C3281C545ae205Eda784DA6EAEAA 		$31,000.00
		
GCMPTBICKA5R4HN2DMRSNPMFWGYN5YO73R4B3DUD3SG7OZGCI4LRA3BP		
		
r9xM4fYBKM9EJcvECEgzcmwMjG5QQeJP8z		
		262k 
0x041a583db93c1bfc883583d08fbc2bb001edd25a"""

seeds = [s.strip() for s in raw_input.split('\n') if s.strip()]

def detect_chain(val: str, override: str = "AUTO"):
    if override != "AUTO": return override.upper()
    val = val.strip()
    if val.startswith("kaspa:") or (len(val) == 64 and not val.startswith("0x")): return "KASPA"
    elif val.startswith("r") and 25 <= len(val) <= 35: return "XRP" 
    elif val.startswith("G") and len(val) == 56: return "STELLAR"
    elif len(val) >= 32 and len(val) <= 44 and not val.startswith("0x") and not val.startswith("bc1") and not val.startswith("T"): return "SOLANA" 
    elif val.startswith("0x"): return "ETHEREUM"
    elif val.startswith("T") and len(val) == 34: return "TRON"
    elif val.startswith("1") or val.startswith("3") or val.startswith("bc1"): return "BITCOIN"
    else: return "ETHEREUM"

parsed_target = None
actual_seeds = []
raw_tokens = []
for s in seeds:
    raw_tokens.extend(re.split(r'[\s,\"]+', s))
    
for tok in raw_tokens:
    tok = tok.strip()
    if not tok: continue
    
    # Is it an address?
    # Bitcoin, Ethereum, Solana, Ripple, Tron, Stellar
    if (tok.startswith("0x") and len(tok) == 42) or \
       (tok.startswith("bc1") and len(tok) >= 42) or \
       (tok.startswith("1") and 25 <= len(tok) <= 34) or \
       (tok.startswith("3") and 25 <= len(tok) <= 34) or \
       (tok.startswith("r") and 25 <= len(tok) <= 35) or \
       (tok.startswith("T") and len(tok) == 34) or \
       (tok.startswith("G") and len(tok) == 56) or \
       (tok.startswith("kaspa:") and len(tok) > 60) or \
       (len(tok) >= 32 and len(tok) <= 44 and tok.isalnum() and not tok.startswith("0x") and not tok.startswith("bc1")):
        # Deduplicate seeds while keeping order
        if tok not in actual_seeds:
            actual_seeds.append(tok)
        continue
        
    # If not an address, maybe an amount?
    upper_tok = tok.upper()
    num_match = re.search(r'^[\$]?(\d+(?:\.\d+)?)', tok.replace(',', ''))
    if num_match:
        val = float(num_match.group(1))
        if "K" in upper_tok: val *= 1000
        if "M" in upper_tok: val *= 1000000
        if val > 0:
            # Prefer larger amounts or last specified? Let's keep the last parsed target, 
            # OR we can sum them up if they are independent, but taking the max is safer.
            if parsed_target is None or val > parsed_target:
                parsed_target = val

print("Parsed Target:", parsed_target)
for addr in actual_seeds:
    print(f"[{detect_chain(addr):10}] {addr}")