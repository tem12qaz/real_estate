import base64
import threading

import requests


cookies_meet = {
    'SEARCH_SAMESITE': 'CgQI-JYB',
    'HSID': 'A83_3ClQv9kIA2y7p',
    'SSID': 'AsVpRa0UtQaLuMPNE',
    'APISID': 'A6CbeBx8NJh0jU32/A704VpRQC41VXavIN',
    'SAPISID': '4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW',
    '__Secure-1PAPISID': '4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW',
    '__Secure-3PAPISID': '4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW',
    'SID': 'SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94F71zFdz38ipff84tvxK3WA.',
    '__Secure-1PSID': 'SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94BTHFCCYieP10lfcTzk0bGg.',
    '__Secure-3PSID': 'SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94vV3WbO0fAktTb50xo-WCBg.',
    'OSID': 'SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxujev4G6mAlngNtmC_AK1KQ.',
    '__Secure-OSID': 'SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxW7zVZHGl-IYYYFlXifYJWA.',
    'OTZ': '6828078_44_44_123780_40_436260',
    '__Secure-ENID': '9.SE=W3Ykci2eQkCqIxJTC-iFF0VmS0GM0YB8cQzrlorLMsKQpxKUIzTqzvlFvf1Gjt5R9hV_2qG8hw_fjw00BSy1w3XddxDFiT0hUIYnzCOgjYKYvyZGcJjnjzQbmE-tnFnirbzP62tX3TBdqSNty6evVCjrCFin58u9qAwNUblDYPjb1YqWNMWgEO-uMO6AMbAE8sERUrdzRdf8XNSXIagVO9TMtLcjGhc3MEJGodiEnp53VRON-zx8BXz5B2qJq-XTHHg_f9Ow7KbQvA',
    'AEC': 'AakniGNVJZE9_o5yVSSP_MOYrkdRJ8cY9cJzUUVyq-yZNcKbeTgUMGuCbg',
    'NID': '511=VQKpmhGD4LIljEYMKH7iuXgQKGvHmFChRMBaMj6AwX7ge3Z_ah-obQux8p-CfpWfZMdJ17PAlA6DLaCkY27kXlDRK487uqSN7GlHjGIOvzev4pMRz6ZrLQal9t7z92GW6UzfjWLIW5eAgzGcPcvFx8BQTSCEPZR7IkYXZ4HNXBtW3ZPdWvS03ggAtC6-kE-4j7yuOMQOMT1juL-CNVRxRRWjhHL36Vg-R0LA3FcSF_ZBx_O5eh7ir9g8Bt1aZ8sZASBjPC1SwUbilM924Vv1_IqICa1Bc8kiLsiKUrqRaQblf5SvUv-j6dGdoavaEYbp0qQqoduNxT7ccPYbQgtVpDo6iJi51zDPsv0Wis3xV8IujS8skECCyVs37HQQ',
    '1P_JAR': '2022-12-30-02',
    'COMPASS': 'meet-ui=CgAQye-7nQYaRwAJa4lXbKHY_YS-23pYX7BVH933fdP9rO13z7UVW_744DHga_SdhYtrQXXd_4FQn15HyziSoJga1xiWR3RU04fGN3NF6R24',
    'SIDCC': 'AIKkIs1CDQzBK_GstNIDrePDRHa1MnKfRPsP0SCjs9q0JpDxzLCk5N8Os0aPzVM3kt3eAtOw4nYt',
    '__Secure-1PSIDCC': 'AIKkIs0hbYwxUruEUkBjWPoAl6Mf8oM629weVsG1qUJvwFtuB2c4zTG2HvC2rOz5c7O7vWJ4-MIZ',
    '__Secure-3PSIDCC': 'AIKkIs09jJnvrugboBrtoenAxlO7VDxF4CxajmdfwTxna5efWtXkbc1xngZZqcmYSm3Tr8QzEKcz',
}

headers = {
    'authority': 'meet.google.com',
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en;q=0.8,es;q=0.7',
    'authorization': 'SAPISIDHASH 1672410496_29bb5f82e69de3509135974df658e6305753fbe2',
    'content-type': 'application/x-protobuf',
    # 'cookie': 'SEARCH_SAMESITE=CgQI-JYB; HSID=A83_3ClQv9kIA2y7p; SSID=AsVpRa0UtQaLuMPNE; APISID=A6CbeBx8NJh0jU32/A704VpRQC41VXavIN; SAPISID=4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW; __Secure-1PAPISID=4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW; __Secure-3PAPISID=4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW; SID=SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94F71zFdz38ipff84tvxK3WA.; __Secure-1PSID=SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94BTHFCCYieP10lfcTzk0bGg.; __Secure-3PSID=SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94vV3WbO0fAktTb50xo-WCBg.; OSID=SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxujev4G6mAlngNtmC_AK1KQ.; __Secure-OSID=SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxW7zVZHGl-IYYYFlXifYJWA.; OTZ=6828078_44_44_123780_40_436260; __Secure-ENID=9.SE=W3Ykci2eQkCqIxJTC-iFF0VmS0GM0YB8cQzrlorLMsKQpxKUIzTqzvlFvf1Gjt5R9hV_2qG8hw_fjw00BSy1w3XddxDFiT0hUIYnzCOgjYKYvyZGcJjnjzQbmE-tnFnirbzP62tX3TBdqSNty6evVCjrCFin58u9qAwNUblDYPjb1YqWNMWgEO-uMO6AMbAE8sERUrdzRdf8XNSXIagVO9TMtLcjGhc3MEJGodiEnp53VRON-zx8BXz5B2qJq-XTHHg_f9Ow7KbQvA; AEC=AakniGNVJZE9_o5yVSSP_MOYrkdRJ8cY9cJzUUVyq-yZNcKbeTgUMGuCbg; NID=511=VQKpmhGD4LIljEYMKH7iuXgQKGvHmFChRMBaMj6AwX7ge3Z_ah-obQux8p-CfpWfZMdJ17PAlA6DLaCkY27kXlDRK487uqSN7GlHjGIOvzev4pMRz6ZrLQal9t7z92GW6UzfjWLIW5eAgzGcPcvFx8BQTSCEPZR7IkYXZ4HNXBtW3ZPdWvS03ggAtC6-kE-4j7yuOMQOMT1juL-CNVRxRRWjhHL36Vg-R0LA3FcSF_ZBx_O5eh7ir9g8Bt1aZ8sZASBjPC1SwUbilM924Vv1_IqICa1Bc8kiLsiKUrqRaQblf5SvUv-j6dGdoavaEYbp0qQqoduNxT7ccPYbQgtVpDo6iJi51zDPsv0Wis3xV8IujS8skECCyVs37HQQ; 1P_JAR=2022-12-30-02; COMPASS=meet-ui=CgAQye-7nQYaRwAJa4lXbKHY_YS-23pYX7BVH933fdP9rO13z7UVW_744DHga_SdhYtrQXXd_4FQn15HyziSoJga1xiWR3RU04fGN3NF6R24; SIDCC=AIKkIs1CDQzBK_GstNIDrePDRHa1MnKfRPsP0SCjs9q0JpDxzLCk5N8Os0aPzVM3kt3eAtOw4nYt; __Secure-1PSIDCC=AIKkIs0hbYwxUruEUkBjWPoAl6Mf8oM629weVsG1qUJvwFtuB2c4zTG2HvC2rOz5c7O7vWJ4-MIZ; __Secure-3PSIDCC=AIKkIs09jJnvrugboBrtoenAxlO7VDxF4CxajmdfwTxna5efWtXkbc1xngZZqcmYSm3Tr8QzEKcz',
    'origin': 'https://meet.google.com',
    'referer': 'https://meet.google.com/',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-arch': '',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"108.0.5359.125"',
    'sec-ch-ua-full-version-list': '"Not?A_Brand";v="8.0.0.0", "Chromium";v="108.0.5359.125", "Google Chrome";v="108.0.5359.125"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-model': '"Nexus 5"',
    'sec-ch-ua-platform': '"Android"',
    'sec-ch-ua-platform-version': '"6.0"',
    'sec-ch-ua-wow64': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
    'x-client-data': 'CIq2yQEIpLbJAQjBtskBCKmdygEIq4TLAQiSocsBCPOAzQEIo4LNAQiygs0BCN2CzQEI74TNAQ==',
    'x-compass-routing-destination': 'AHSoBRUiqPuOgi61mAe58zctExU0jtZz_kdUUd88pIRRFEetdvQVZ94kAj2uGAWiSjlDxGhuKMeicu4EsPJrM7GqH7E5xv2-Bkga396hfw4=',
    'x-goog-api-key': 'AIzaSyCG_6Rm6c7ucLr2NwAq33-vluCp2VfSkf0',
    'x-goog-authuser': '0',
    'x-goog-encode-response-if-executable': 'base64',
    'x-goog-meeting-debugid': 'boq_hlane_zWvH8HrZMH9',
    'x-goog-meeting-rtcclient': 'CAEQqgMYASABKAg4AQ==',
    'x-goog-meeting-startsource': '187',
}

def get_meet_url_bytes():
    response = requests.post(
        'https://meet.google.com/$rpc/google.rtc.meetings.v1.MeetingSpaceService/CreateMeetingSpace',
        cookies=cookies_meet,
        headers=headers,
    )
    return response.content


def decode_meet_url(base64_url: bytes) -> str:
    sample_string_bytes = base64.b64decode(base64_url)
    string = sample_string_bytes.decode("utf-8")
    start = string.find('https://meet.google.com/')
    string = string[start: start+36]
    return string


def get_meet_url() -> str:
    return decode_meet_url(get_meet_url_bytes())
