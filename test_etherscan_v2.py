import os
import requests
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get('VITE_ETHERSCAN_API_KEY')
addr = '0x030c0c65DBb914e423992F35b4Fe956F5E90b045'
url = f'https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist&address={addr}&startblock=0&endblock=99999999&page=1&offset=5&sort=desc&apikey={key}'
r = requests.get(url)
data = r.json()
print("status:", data.get('status'), "msg:", data.get('message'), "results:", len(data.get('result', [])))
