import os
import requests
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('VITE_TATUM_API_KEY') or os.environ.get('TATUM_API_KEY')
addr = '0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772'
url = f'https://api.tatum.io/v3/bsc/account/transaction/{addr}?pageSize=50'
headers = {"x-api-key": key}
r = requests.get(url, headers=headers)
print("Tatum BSC status:", r.status_code)
if r.status_code == 200:
    data = r.json()
    print("Results:", len(data))
    if len(data) > 0:
        print(data[0])
else:
    print(r.text)
