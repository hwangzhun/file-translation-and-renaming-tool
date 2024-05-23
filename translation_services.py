import requests
import hashlib
import time

def translate_text_google(text, target_language, api_key, proxy):
    url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'q': text,
        'target': target_language,
        'format': 'text'
    }
    proxies = {
        'http': proxy,
        'https': proxy
    }
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    
    if response.status_code == 200:
        return response.json()['data']['translations'][0]['translatedText']
    else:
        return text

def translate_text_baidu(text, target_language, appid, secret_key, proxy):
    baidu_language_codes = {
        "zh-CN": "zh",
        "en": "en",
        "ja": "jp",
        "ko": "kor",
        "fr": "fra"
    }
    target_language = baidu_language_codes.get(target_language, target_language)
    
    url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
    salt = str(time.time())
    sign = hashlib.md5((appid + text + salt + secret_key).encode('utf-8')).hexdigest()
    
    params = {
        'q': text,
        'from': 'auto',
        'to': target_language,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    response = requests.get(url, params=params, proxies=proxies)
    
    if response.status_code == 200:
        result = response.json()
        if 'trans_result' in result:
            return result['trans_result'][0]['dst']
        else:
            return text
    else:
        return text

def translate_text_bing(text, target_language, subscription_key, region, proxy):
    url = "https://api.cognitive.microsofttranslator.com/translate"
    params = {
        'api-version': '3.0',
        'to': target_language
    }
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json'
    }
    data = [{'Text': text}]
    
    proxies = {
        'http': proxy,
        'https': proxy
    }
    
    response = requests.post(url, headers=headers, params=params, json=data, proxies=proxies)
    
    if response.status_code == 200:
        result = response.json()
        if result:
            return result[0]['translations'][0]['text']
        else:
            return text
    else:
        return text
