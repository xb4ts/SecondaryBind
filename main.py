import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json

KEY = b"Yg&tc%DEuh6%Zc^8"
IV  = b"6oyZDr22E3ychjM%"

JWT = "eyJhbGciOiJIUzI1.."
URL = "https://loginbp.ggpolarbear.com/MajorSecondaryAccountBind"

EX = "https://100067.connect.garena.com/oauth/token/twitter/exchange"
PA = {
    "token_secret": "zJeoBdaJNLipYm9ON...",
    "create_grant": "false",
    "login_scenario": "app_platform_bind",
    "twitter_access_token": "2082180033108385792-CtSGRKtnw5...",
    "client_id": "100067"
}

def varint(v:int):
    out=[]
    while True:
        b=v & 0x7F
        v >>=7
        if v: b|=0x80
        out.append(b)
        if not v: break
    return bytes(out)

def field_int(fid,val):
    return varint((fid<<3)|0)+varint(val)

def field_str(fid,val):
    raw=val.encode()
    return varint((fid<<3)|2)+varint(len(raw))+raw

garena_headers = {
    "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
    "Content-Type": "application/x-www-form-urlencoded"
}

g_res = requests.post(EX, headers=garena_headers, data=PA)

if g_res.status_code == 200:
    data = g_res.json()
    open_id = data.get("open_id")
    access_token = data.get("access_token")
    platform = data.get("platform", 5)
    
    hex = "3f431b8daa68a439c5530bfbca8..." # access_token
    
    packet = b""
    packet += field_str(1, open_id)
    packet += field_int(2, platform)
    packet += field_str(3, access_token)
    packet += field_str(4, hex)
    packet += field_int(5, 3)

    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    encrypted_packet = cipher.encrypt(pad(packet, 16))

    bytes = {
        "Authorization": f"Bearer {JWT}",
        "X-Unity-Version": "2022.3.47f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB55",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "deflate, gzip"
    }

    r = requests.post(URL, headers=bytes, data=encrypted_packet)

    print(f"[+] Status: {r.status_code}")
    print(f"[+] Response: {r.text}")
else:
    print(f"[-] exchange failed: {g_res.status_code}")
    print(g_res.text)
