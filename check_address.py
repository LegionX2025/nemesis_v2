import urllib.request
try:
    print('Testing PolygonScan V1')
    print(urllib.request.urlopen("https://api.polygonscan.com/api?module=account&action=txlist&address=0x28C6c06298d514Db089934071355E5743bf21d60&startblock=0&endblock=99999999&page=1&offset=1&sort=desc&apikey=5HVRJGR3D1FGAG1VQXEIPN5HE7WU399CDY").read().decode()[:100])
except Exception as e:
    print(e)
