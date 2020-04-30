# @Time : 2020/4/28 16:56 
# @Author : lixiang
# @File : rc4_decode.py 
# @Software: PyCharm
import base64

from rest_framework.exceptions import NotAuthenticated


def rc4_decode_main(key = "init_key", message = "init_message"):
    if message:
        try:
            s_box = rc4_init_sbox(key)
            crypt = rc4_excrypt(message, s_box)
            return crypt
        except:
            raise NotAuthenticated("message信息有误，解析失败！")
    else:
        raise NotAuthenticated("没有传入message")
def rc4_init_sbox(key):
    s_box = list(range(256))  # 我这里没管秘钥小于256的情况，小于256不断重复填充即可
    # print("原来的 s 盒：%s" % s_box)
    j = 0
    for i in range(256):
        j = (j + s_box[i] + ord(key[i % len(key)])) % 256
        s_box[i], s_box[j] = s_box[j], s_box[i]
    # print("混乱后的 s 盒：%s"% s_box)
    return s_box
def rc4_excrypt(plain, box):
    # print("调用解密程序成功。")
    plain = base64.b64decode(plain.encode('utf-8'))
    plain = bytes.decode(plain)
    res = []
    i = j = 0
    for s in plain:
        i = (i + 1) % 256
        j = (j + box[i]) % 256
        box[i], box[j] = box[j], box[i]
        t = (box[i] + box[j]) % 256
        k = box[t]
        res.append(chr(ord(s) ^ k))
    # print("res用于解密字符串，解密后是：%res" %res)
    cipher = "".join(res)
    # print("解密后的字符串是：%s" %cipher)
    # print("解密后的输出(没经过任何编码):")
    return  cipher