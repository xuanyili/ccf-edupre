import requests

def tianditu_display(key, mid, loc, file="tianditu.png"):
    url = 'http://api.tianditu.gov.cn/staticimage?center={},{}&width=500&height=500&zoom=15&layers=vec_c,cva_c&markers={},{}&tk={}'.format(mid[0],mid[1],loc[0],loc[1],key)
    res=requests.get(url)
    with open(file, 'wb') as f:
        f.write(res.content)