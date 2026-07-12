import requests
url = "https://api.etherscan.io/v2/api?chainid=42220&module=account&action=txlist&address=0x3b5D17e2236f4D773DA87EE10B71D80C5e5b5772&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey=5HVRKDR54EFRF7YDK5ZCYE7KIBN7C27G6B"
print(requests.get(url).json())
