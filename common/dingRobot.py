import os
import urllib.parse
import requests
import time
import hmac
import hashlib
import base64


def get_dingtalk_conf():
    """
    读取钉钉机器人凭据。

    优先级：环境变量 > conf/config.ini 的 [DINGTALK] 段 > 空字符串。
    凭据不写在代码里，避免随代码提交到公开仓库被泄露。
    本地使用时在 conf/config.ini（该文件已被 .gitignore 忽略）里配置：
        [DINGTALK]
        access_token = 你的机器人access_token
        secret = 你的加签密钥
    也可以设置环境变量 DINGTALK_ACCESS_TOKEN / DINGTALK_SECRET。
    :return: (access_token, secret)
    """
    access_token = os.environ.get('DINGTALK_ACCESS_TOKEN', '')
    secret = os.environ.get('DINGTALK_SECRET', '')
    if access_token and secret:
        return access_token, secret

    try:
        from conf.operationConfig import OperationConfig
        conf = OperationConfig()
        access_token = access_token or conf.get_section_for_data('DINGTALK', 'access_token')
        secret = secret or conf.get_section_for_data('DINGTALK', 'secret')
    except Exception:
        pass
    return access_token, secret


def generate_sign():
    """
    签名计算
    把timestamp+"\n"+密钥当做签名字符串，使用HmacSHA256算法计算签名，然后进行Base64 encode，
    最后再把签名参数再进行urlEncode，得到最终的签名（需要使用UTF-8字符集）
    :return: 返回当前时间戳、加密后的签名
    """
    # 当前时间戳
    timestamp = str(round(time.time() * 1000))
    # 钉钉机器人中的加签密钥
    secret = get_dingtalk_conf()[1]
    secret_enc = secret.encode('utf-8')
    str_to_sign = '{}\n{}'.format(timestamp, secret)
    # 转成byte类型
    str_to_sign_enc = str_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, str_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_dd_msg(content_str, at_all=True):
    """
    向钉钉机器人推送结果
    :param content_str: 发送的内容
    :param at_all: @全员，默认为True
    :return:
    """
    timestamp_and_sign = generate_sign()
    # url(钉钉机器人Webhook地址) + timestamp + sign
    access_token = get_dingtalk_conf()[0]
    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp_and_sign[0]}&sign={timestamp_and_sign[1]}'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "text",
        "text": {
            "content": content_str
        },
        "at": {
            "isAtAll": at_all
        },
    }
    res = requests.post(url, json=data, headers=headers)
    return res.text
