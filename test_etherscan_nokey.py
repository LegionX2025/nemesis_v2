import requests
try:
    print(requests.get("https://api.etherscan.io/api?module=account&action=txlist&address=0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772&startblock=0&endblock=99999999&page=1&offset=10&sort=desc").json())
except Exception as e:
    print(e)
