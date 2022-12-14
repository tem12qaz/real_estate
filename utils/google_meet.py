import base64
import requests


def get_meet_url_bytes():
    cookies = {
        'HSID': 'AQzYtmnMqnI5QS6IN',
        'SSID': 'AV1G1umsj65ondiH2',
        'APISID': '3h3n8hypB_TGaveY/Ap6O0tmSk12w2QvbB',
        'SAPISID': 'ILf9um-0tN-gpyNF/A6t3SA9HihStMvb0E',
        '__Secure-1PAPISID': 'ILf9um-0tN-gpyNF/A6t3SA9HihStMvb0E',
        '__Secure-3PAPISID': 'ILf9um-0tN-gpyNF/A6t3SA9HihStMvb0E',
        '__Secure-ENID': '7.SE=YgS7e-NF9dlcFEoziWdqqiRWl8bZv8_1Tk-igBXJAUV-eqEHFZiwXQ7FzUgyPiG2_XpC7xIqOK2F3VwfhNtebNv02UjUl0GGp-u9MeIL5qGrJZ2jwbRnum7G2f2TkrF_xLtgUbAJ0lIlSVO2iis5_U3zG-gBKR_7wK0Y8cyjAew0qUMMAO_pKZmccnQJItoJOMzagOF984UgH95eg2l_neaNmZUUc340dJJdqp2EfwEUx9Haz8y7NkIHuK7zKCb74kObK-TDUnuPKw',
        'SEARCH_SAMESITE': 'CgQIhZcB',
        'SID': 'Rwi5za7A2MBYcceF8I3DZ3MlQ1o62rRAGrNgh_elOt4LFT__AjqV7Lclq_V_6tddg6fyeg.',
        '__Secure-1PSID': 'Rwi5za7A2MBYcceF8I3DZ3MlQ1o62rRAGrNgh_elOt4LFT__ZoBndJISTjNSX19zB4xWAg.',
        '__Secure-3PSID': 'Rwi5za7A2MBYcceF8I3DZ3MlQ1o62rRAGrNgh_elOt4LFT___kqmsGdedvizkf-JoVGBiw.',
        'AEC': 'AakniGOXHWgezRLfevR_UjMYZfRtq5s8LYlsxR5SOl3uEKCEq0MDqpJawxk',
        'NID': '511=flNCjdMOM4PZ7TbVKc6YUalxLk1yVVjrIBqLdPwSN01MG5MXuef7u7o4NZW6TpJiQwe9GB2MNYIAacI-uQmAhHvxhToBjxyjeD8X4F5f4HWAIC3fW5fLPSRyIN5wolVdwQY2AFF6021ykcXZ3ok-gj_R85p9e7VNSndciWCpEGt0CDdXkiFswExajFbL2s7c6z8jjUDIqjr7xm_gc3qA76clW5n8Zc-TKHBu3cXskeDnQoWz5XcFThOsxVvE1d0wWBKXrAZj_91i8qfBNCI4eeE7JkqfcjXax2bpsnSiTCtB4i3KX6BqKYPQl5RvyErCfJREUSyAq2JrmPo',
        '1P_JAR': '2022-12-14-03',
        'OSID': 'Rwi5zVPrWiPdLJ9Radh9ABXytpeeth6IB1k-Y-5HwHNrOrG1VJMotujqV4GTL4uIcoSUhA.',
        '__Secure-OSID': 'Rwi5zVPrWiPdLJ9Radh9ABXytpeeth6IB1k-Y-5HwHNrOrG1Ei4e3bSNKG_Quyz23Efkmw.',
        'OTZ': '6811431_44_44_123780_40_436260',
        'COMPASS': 'meet-ui=CgAQw5TlnAYaRwAJa4lXbKHY_YS-23pYX7BVH933fdP9rO13z7UVW_744DHga_SdhYtrQXXd_4FQn15HyziSoJga1xiWR3RU04fGN3NF6R24',
        'SIDCC': 'AIKkIs0rwqcIgvFmBQ_mYeI1qu8NXGO00RusaHsGG6DyqAOQxiRtwjJb1pRbfqcHJj9nN6JPa_6X',
        '__Secure-1PSIDCC': 'AIKkIs2NdoKrLILX6G-emmHcuZ2ZG7NlXfmAxyiIEImmJ4QlZbO0WydfuZyImF9PMiTLMM-ziW4',
        '__Secure-3PSIDCC': 'AIKkIs0X2lq_eeJQ-5rEa8cH9zParTktP7gRlZMVnfFtB8o86x7rRM23ZDUYQOfpWOWTv230qyTY',
    }

    headers = {
        'authority': 'meet.google.com',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en;q=0.8,es;q=0.7',
        'authorization': 'SAPISIDHASH 1670989948_a416608ea2477a98dd185aee5881e1aa01ccd822',
        # 'content-length': '0',
        'content-type': 'application/x-protobuf',
        # 'cookie': 'HSID=AQzYtmnMqnI5QS6IN; SSID=AV1G1umsj65ondiH2; APISID=3h3n8hypB_TGaveY/Ap6O0tmSk12w2QvbB; SAPISID=ILf9um-0tN-gpyNF/A6t3SA9HihStMvb0E; __Secure-1PAPISID=ILf9um-0tN-gpyNF/A6t3SA9HihStMvb0E; __Secure-3PAPISID=ILf9um-0tN-gpyNF/A6t3SA9HihStMvb0E; __Secure-ENID=7.SE=YgS7e-NF9dlcFEoziWdqqiRWl8bZv8_1Tk-igBXJAUV-eqEHFZiwXQ7FzUgyPiG2_XpC7xIqOK2F3VwfhNtebNv02UjUl0GGp-u9MeIL5qGrJZ2jwbRnum7G2f2TkrF_xLtgUbAJ0lIlSVO2iis5_U3zG-gBKR_7wK0Y8cyjAew0qUMMAO_pKZmccnQJItoJOMzagOF984UgH95eg2l_neaNmZUUc340dJJdqp2EfwEUx9Haz8y7NkIHuK7zKCb74kObK-TDUnuPKw; SEARCH_SAMESITE=CgQIhZcB; SID=Rwi5za7A2MBYcceF8I3DZ3MlQ1o62rRAGrNgh_elOt4LFT__AjqV7Lclq_V_6tddg6fyeg.; __Secure-1PSID=Rwi5za7A2MBYcceF8I3DZ3MlQ1o62rRAGrNgh_elOt4LFT__ZoBndJISTjNSX19zB4xWAg.; __Secure-3PSID=Rwi5za7A2MBYcceF8I3DZ3MlQ1o62rRAGrNgh_elOt4LFT___kqmsGdedvizkf-JoVGBiw.; AEC=AakniGOXHWgezRLfevR_UjMYZfRtq5s8LYlsxR5SOl3uEKCEq0MDqpJawxk; NID=511=flNCjdMOM4PZ7TbVKc6YUalxLk1yVVjrIBqLdPwSN01MG5MXuef7u7o4NZW6TpJiQwe9GB2MNYIAacI-uQmAhHvxhToBjxyjeD8X4F5f4HWAIC3fW5fLPSRyIN5wolVdwQY2AFF6021ykcXZ3ok-gj_R85p9e7VNSndciWCpEGt0CDdXkiFswExajFbL2s7c6z8jjUDIqjr7xm_gc3qA76clW5n8Zc-TKHBu3cXskeDnQoWz5XcFThOsxVvE1d0wWBKXrAZj_91i8qfBNCI4eeE7JkqfcjXax2bpsnSiTCtB4i3KX6BqKYPQl5RvyErCfJREUSyAq2JrmPo; 1P_JAR=2022-12-14-03; OSID=Rwi5zVPrWiPdLJ9Radh9ABXytpeeth6IB1k-Y-5HwHNrOrG1VJMotujqV4GTL4uIcoSUhA.; __Secure-OSID=Rwi5zVPrWiPdLJ9Radh9ABXytpeeth6IB1k-Y-5HwHNrOrG1Ei4e3bSNKG_Quyz23Efkmw.; OTZ=6811431_44_44_123780_40_436260; COMPASS=meet-ui=CgAQw5TlnAYaRwAJa4lXbKHY_YS-23pYX7BVH933fdP9rO13z7UVW_744DHga_SdhYtrQXXd_4FQn15HyziSoJga1xiWR3RU04fGN3NF6R24; SIDCC=AIKkIs0rwqcIgvFmBQ_mYeI1qu8NXGO00RusaHsGG6DyqAOQxiRtwjJb1pRbfqcHJj9nN6JPa_6X; __Secure-1PSIDCC=AIKkIs2NdoKrLILX6G-emmHcuZ2ZG7NlXfmAxyiIEImmJ4QlZbO0WydfuZyImF9PMiTLMM-ziW4; __Secure-3PSIDCC=AIKkIs0X2lq_eeJQ-5rEa8cH9zParTktP7gRlZMVnfFtB8o86x7rRM23ZDUYQOfpWOWTv230qyTY',
        'origin': 'https://meet.google.com',
        'referer': 'https://meet.google.com/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"108.0.5359.99"',
        'sec-ch-ua-full-version-list': '"Not?A_Brand";v="8.0.0.0", "Chromium";v="108.0.5359.99", "Google Chrome";v="108.0.5359.99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"10.0.0"',
        'sec-ch-ua-wow64': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-client-data': 'CIe2yQEIprbJAQjBtskBCKmdygEI/+bKAQiTocsBCM35zAEI3/nMAQjr+swBCPD/zAEIhoHNAQiygs0B',
        'x-compass-routing-destination': 'AHSoBRWuZa2p-XjPKxJQSNdeK2I6Mv497vuyiK-oaTwdiLPseG2c8QpomyeNayqqAHO9oJVvz7I1fO43eBe2DAWRmlDYjuIXc7ItWMuNPH4=',
        'x-goog-api-key': 'AIzaSyCG_6Rm6c7ucLr2NwAq33-vluCp2VfSkf0',
        'x-goog-authuser': '0',
        'x-goog-encode-response-if-executable': 'base64',
        'x-goog-meeting-debugid': 'boq_hlane_1BPC1zZBjOe',
        'x-goog-meeting-rtcclient': 'CAEQqgMYASABKAg4AQ==',
        'x-goog-meeting-startsource': '218',
    }

    response = requests.post(
        'https://meet.google.com/$rpc/google.rtc.meetings.v1.MeetingSpaceService/CreateMeetingSpace',
        cookies=cookies,
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