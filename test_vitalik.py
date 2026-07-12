import requests
url = "https://api.etherscan.io/v2/api?chainid=1&module=account&action=txlist&address=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&apikey=5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY"
r = requests.get(url)
print(len(r.json().get('result', [])))
