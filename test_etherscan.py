import urllib.request
import json
url = 'https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&address=0x932F2489f417531CceDE0c1C95bcE0d903fF0DCC&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey=5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY'
try:
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
