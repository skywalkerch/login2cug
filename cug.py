import argparse
import hashlib
import hmac
import json
import math
import urllib.request
import urllib.parse
import re
import base64

class Login:
    def __init__(self, username, password):
        self.HOST = ''
        self.USERNAME = username
        self.PASSWORD = password
        self.AC_ID = '1'               
        self.IP = ''               
        self._PADCHAR = "="
        self._ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"
    def get_md5(self,password, token):
        return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()
    def get_sha1(self, value):
        return hashlib.sha1(value.encode()).hexdigest()
    def s(self,a, b):
        c = len(a)
        v = []
        # 彻底解决索引越界问题：自动判定剩余长度并进行 0 值填充
        for i in range(0, c, 4):
            val = 0
            for j in range(4):
                if i + j < c:
                    val |= (a[i + j] << (j * 8))
            v.append(val)
        if b:
            v.append(c)
        return v
    def l(self,a, b):
        d = len(a)
        c = (d - 1) << 2
        if b:
            m = a[-1]
            if m < c - 3 or m > c:
                return ""
            c = m
        ret = []
        for i in range(d):
            ret.append(chr(a[i] & 0xff) + chr(a[i] >> 8 & 0xff) + chr(a[i] >> 16 & 0xff) + chr(a[i] >> 24 & 0xff))
        if b:
            return "".join(ret)[:c]
        else:
            return "".join(ret)
    def xtea_encrypt(self, string, key):
        if string == "":
            return ""
        v = self.s(string.encode(), True)
        k = self.s(key.encode(), False)
        if len(k) < 4:
            k = k + [0] * (4 - len(k))
        n = len(v) - 1
        z = v[n]
        y = v[0]
        c = 0x86014019 | 0x183639A0
        q = math.floor(6 + 52 / (n + 1))
        sum_val = 0
        while 0 < q:
            sum_val = (sum_val + c) & 0xffffffff
            e = sum_val >> 2 & 3
            for p in range(n):
                y = v[p + 1]
                # 彻底还原 JS 的 32位溢出操作并且兼容 JS 特有运算优先级
                m = ((z >> 5) ^ ((y << 2) & 0xffffffff)) & 0xffffffff
                m = (m + (((y >> 3) ^ ((z << 4) & 0xffffffff)) ^ (sum_val ^ y))) & 0xffffffff
                m = (m + (k[(p & 3) ^ e] ^ z)) & 0xffffffff
                v[p] = (v[p] + m) & 0xffffffff
                z = v[p]
            y = v[0]
            m = ((z >> 5) ^ ((y << 2) & 0xffffffff)) & 0xffffffff
            m = (m + (((y >> 3) ^ ((z << 4) & 0xffffffff)) ^ (sum_val ^ y))) & 0xffffffff
            m = (m + (k[(n & 3) ^ e] ^ z)) & 0xffffffff
            v[n] = (v[n] + m) & 0xffffffff
            z = v[n]
            q -= 1
        return self.l(v, False)
    def get_base64(self,s):
        i = 0
        x = []
        imax = len(s) - len(s) % 3
        while i < imax:
            b10 = (ord(s[i]) << 16) | (ord(s[i + 1]) << 8) | ord(s[i + 2])
            x.append(self._ALPHA[(b10 >> 18)])
            x.append(self._ALPHA[((b10 >> 12) & 63)])
            x.append(self._ALPHA[((b10 >> 6) & 63)])
            x.append(self._ALPHA[(b10 & 63)])
            i += 3
        if len(s) - imax == 1:
            b10 = ord(s[i]) << 16
            x.append(self._ALPHA[(b10 >> 18)] + self._ALPHA[((b10 >> 12) & 63)] + self._PADCHAR + self._PADCHAR)
        elif len(s) - imax == 2:
            b10 = (ord(s[i]) << 16) | (ord(s[i + 1]) << 8)
            x.append(self._ALPHA[(b10 >> 18)] + self._ALPHA[((b10 >> 12) & 63)] + self._ALPHA[((b10 >> 6) & 63)] + self.    _PADCHAR)
        return "".join(x)
    def get_info(self, username, password, client_ip, acid, token):
        info_json = {
            "username": username,
            "password": password,
            "ip": client_ip,
            "acid": acid,
            "enc_ver": "srun_bx1"
        }
        encoded = self.xtea_encrypt(json.dumps(info_json).replace(' ', ''), token)
        return "{SRBX1}" + self.get_base64(encoded)      
    def srun_login(self):
        print("⏳ [1/3] 正在获取挑战码 (Challenge Token)...")
        url_challenge = f"{self.HOST}/cgi-bin/get_challenge?callback=jsonp&username={self.USERNAME}&ip={self.IP}"
        req = urllib.request.Request(url_challenge)
        resp = urllib.request.urlopen(req).read().decode()
        
        token_match = re.search(r'"challenge":"(.*?)"', resp)
        ip_match = re.search(r'"client_ip":"(.*?)"', resp)
        
        if not token_match:
            print("❌ 无法获取 Token，请检查 HOST 地址是否正确！")
            return

        token = token_match.group(1)
        client_ip = ip_match.group(1) if ip_match else self.IP
        print(f"👉 成功! Token: {token} | IP: {client_ip}")

        print("⏳ [2/3] 计算 XXTEA 及拼凑密码散列...")
        info = self.get_info(self.USERNAME, self.PASSWORD, client_ip, self.AC_ID, token)
        print(info)
        hmd5 = self.get_md5(self.PASSWORD, token)
        chkstr = f"{token}{self.USERNAME}{token}{hmd5}{token}{self.AC_ID}{token}{client_ip}{token}200{token}1{token}{info}"
        chksum = self.get_sha1(chkstr)

        print("⏳ [3/3] 正向服务器进行请求认证...")
        data = {
            'action': 'login',
            'username': self.USERNAME,
            'password': '{MD5}' + hmd5,
            'os': 'Windows 10',
            'name': 'Windows',
            'double_stack': '0',
            'chksum': chksum,
            'info': info,
            'ac_id': self.AC_ID,
            'ip': client_ip,
            'n': '200',
            'type': '1'
        }
        
        query = urllib.parse.urlencode(data)
        url_auth = f"{self.HOST}/cgi-bin/srun_portal?callback=jsonp&{query}"
        
        req = urllib.request.Request(url_auth)
        res = urllib.request.urlopen(req).read().decode()
        
        if '"error":"ok"' in res or 'action":"login_ok"' in res:
            print("🎉 恭喜！命令行静默认证成功！")
        else:
            print("⚠ 服务器返回异常响应，请检查参数，详情：")
            print(res)

class Decryptor:
    def __init__(self,token,info):
        self.token=token
        self.info=info 
        self._PADCHAR = "="
        self._ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"
        # 标准的 Base64 字典，用于做替换桥梁
        self._STD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    def s(self,a, b):
        c = len(a)
        v = []
        # 彻底解决索引越界问题：自动判定剩余长度并进行 0 值填充
        for i in range(0, c, 4):
            val = 0
            for j in range(4):
                if i + j < c:
                    val |= (a[i + j] << (j * 8))
            v.append(val)
        if b:
            v.append(c)
        return v
    def l(self,a, b):
        d = len(a)
        c = (d - 1) << 2
        if b:
            m = a[-1]
            if m < c - 3 or m > c:
                return ""
            c = m
        ret = []
        for i in range(d):
            ret.append(chr(a[i] & 0xff) + chr(a[i] >> 8 & 0xff) + chr(a[i] >> 16 & 0xff) + chr(a[i] >> 24 & 0xff))
        if b:
            return "".join(ret)[:c]
        else:
            return "".join(ret)
    def decode_base64(self, s):
        """逆向自定义字典的 Base64"""
        # 建立从自定义字典到标准字典的映射
        trans = str.maketrans(self._ALPHA, self._STD_ALPHA)
        # 将自定义 Base64 字符串转换为标准 Base64 字符串
        std_b64 = s.translate(trans)
        # 使用标准库解码，得到原始的 bytes
        decoded_bytes = base64.b64decode(std_b64)
        return decoded_bytes
    def xtea_decrypt(self,encrypted_bytes, key):
        """逆向 XXTEA 解密"""
        if not encrypted_bytes:
            return ""
            
        v = self.s(encrypted_bytes, False)
        k = self.s(key.encode(), False)
        if len(k) < 4:
            k = k + [0] * (4 - len(k))
            
        n = len(v) - 1
        if n < 1:
            return self.l(v, True)
            
        c = 0x86014019 | 0x183639A0
        q = math.floor(6 + 52 / (n + 1))
        
        sum_val = (q * c) & 0xffffffff
        y = v[0]
        
        while sum_val != 0:
            e = sum_val >> 2 & 3
            for p in range(n, -1, -1):
                z = v[p - 1] if p > 0 else v[n]
                m = ((z >> 5) ^ ((y << 2) & 0xffffffff)) & 0xffffffff
                m = (m + (((y >> 3) ^ ((z << 4) & 0xffffffff)) ^ (sum_val ^ y))) & 0xffffffff
                m = (m + (k[(p & 3) ^ e] ^ z)) & 0xffffffff
                v[p] = (v[p] - m) & 0xffffffff
                y = v[p]
            sum_val = (sum_val - c) & 0xffffffff
            
        return self.l(v, True)
    def decrypt_info(self):
        """入口：解密 SRBX1 载荷"""
        
        # 1. 第一步：必须先进行 URL 解码！解决所有的 %XX 问题
        url_decoded_payload = urllib.parse.unquote(self.info)
        
        # 2. 剥离头部标识
        if url_decoded_payload.startswith("{SRBX1}"):
            b64_str = url_decoded_payload[7:]
        else:
            b64_str = url_decoded_payload
            
        # 3. 逆向 Base64
        encrypted_bytes = self.decode_base64(b64_str)
        
        # 4. 逆向 XXTEA 解密
        decrypted_str = self.xtea_decrypt(encrypted_bytes, self.token)
        
        # 5. 解析 JSON
        return json.loads(decrypted_str)

    

 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('--info', required=False ,default='')
    #parser.add_argument('--token', required=False ,default='')
    #parser.add_argument('--login', type=bool,required=True, default=True)
    parser.add_argument('--username', required=False ,default='')
    parser.add_argument('--password', required=False ,default='')
    args = parser.parse_args()
    #if(args.login):
    #    login=Login(args.username, args.password)
    #    
    #else:
    #    decryptor=Decryptor(args.token,args.info)
    #    decrypted_info=decryptor.decrypt_info()
    #    print("账号: ", decrypted_info.get("username"))
    #    print("密码: ", decrypted_info.get("password"))
    #    print("IP: ", decrypted_info.get("ip"))  
    login=Login(args.username, args.password)
    login.srun_login()