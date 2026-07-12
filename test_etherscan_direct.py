import os
import requests
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('VITE_ETHERSCAN_API_KEY')
url = f'https://api.etherscan.io/api?module=account&action=txlist&address=0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&apikey={key}'
r = requests.get(url)
print(r.json())
