import requests

url = "https://www.oklink.com/api/explorer/v1/eth/addresses/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b/tags"
headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(url, headers=headers)
print("API 1:", res.status_code, res.text[:200])

url2 = "https://www.oklink.com/api/explorer/v1/address/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b"
res2 = requests.get(url2, headers=headers)
print("API 2:", res2.status_code, res2.text[:200])
