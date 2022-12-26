import requests

cookies = {
    '__Secure-ENID': '8.SE=n06ft24FbTYTWU5ENyp-vL0fxN9IUS-54HiKBNUeA0jvtm5Zv60AmgBWPNs3li0GASvA7nDESsnK4gCbCSu0qcRxIHgR6DTQo94-tfzR86tz_uZPDGAflWOWP_Zrvj0XbeiyYR2oIyFph-P1OpSG1y14mTfDfvuVWqBXjm8gwPPGCWY7DYh4MG9z7ivvD2Df0wXnUPQVnk9-C3SdlcQaM1aNnANZwDeju_MlJKRzk_IChE2UNhk3GAP-ULWH0MV33NOl_4k1GelJ2w',
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
    'AEC': 'AakniGNewK4usJ7UpEwV5HrTNtmyc7U9n6nRe08XVE3UrvhaagEFcrHeZQ',
    'OSID': 'SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxujev4G6mAlngNtmC_AK1KQ.',
    '__Secure-OSID': 'SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxW7zVZHGl-IYYYFlXifYJWA.',
    'OTZ': '6828078_44_44_123780_40_436260',
    '1P_JAR': '2022-12-25-21',
    'NID': '511=hmQDfXRlqQwPOmm65D7wqwvu2LHwwoGDN8HExpWvNH5tf2MPKo7hjUd81m7xMHZKr2h5M-K6e6XMNqVDpob5F8foTSKy4r1mlWuVBfj7U84HDLUDapU3iq0vlTHVEFgX4OVj1Z0YUP8oVsUaqNNmxWpvvfi91nEapYNa3YqtJtjGYEWjnYRpmX27rzfwek5fJ8C47gwwTlIFLTX3KH36FWyMsRbfor25KsGwmGxxome3jL8jFeGUYkmivF-Qe1S-Ck7zb70COU2ffV2ZLBIp-UsaX_o8jgQHVwDYPhPNYhbPUtgSPGy3nWwHh796Uhx5kiRqTeSmxPhxyFnPBbK-giQAEOvTKs9ww4lhMrFfqMbJs-7FbSR6EuvKjDqQ',
    'COMPASS': 'meet-ui=CgAQtv-inQYaRwAJa4lXbKHY_YS-23pYX7BVH933fdP9rO13z7UVW_744DHga_SdhYtrQXXd_4FQn15HyziSoJga1xiWR3RU04fGN3NF6R24',
    'SIDCC': 'AIKkIs2s5XnSSjuVBxnPNeTjjfxEVt5tZ0V2fmlgGbjOkbTxf9MtX5K5mDHZxhaRjX541rOF8WfF',
    '__Secure-1PSIDCC': 'AIKkIs0BDlOhI3UvoBvHOYr76P3muMw5r9RHF9aKgIAhkWO_r55h2W9fDlD4OJEbjmF7zQ9yVU7M',
    '__Secure-3PSIDCC': 'AIKkIs0W3MkJizpUjrxDrMlpNaiZXzU-HECll1GzQBEaU1EejCewJ6uuLbCKVo0AWI4BpJT1O5Am',
}

headers = {
    'authority': 'meet.google.com',
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en;q=0.8,es;q=0.7',
    'authorization': 'SAPISIDHASH 1672003271_d717e2387a63058194658b30f290c54fe1d8a5bc',
    'content-type': 'application/x-protobuf',
    # 'cookie': '__Secure-ENID=8.SE=n06ft24FbTYTWU5ENyp-vL0fxN9IUS-54HiKBNUeA0jvtm5Zv60AmgBWPNs3li0GASvA7nDESsnK4gCbCSu0qcRxIHgR6DTQo94-tfzR86tz_uZPDGAflWOWP_Zrvj0XbeiyYR2oIyFph-P1OpSG1y14mTfDfvuVWqBXjm8gwPPGCWY7DYh4MG9z7ivvD2Df0wXnUPQVnk9-C3SdlcQaM1aNnANZwDeju_MlJKRzk_IChE2UNhk3GAP-ULWH0MV33NOl_4k1GelJ2w; SEARCH_SAMESITE=CgQI-JYB; HSID=A83_3ClQv9kIA2y7p; SSID=AsVpRa0UtQaLuMPNE; APISID=A6CbeBx8NJh0jU32/A704VpRQC41VXavIN; SAPISID=4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW; __Secure-1PAPISID=4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW; __Secure-3PAPISID=4kF3Ixz3c4pqeWXK/AqN9j_vIzOikIBsvW; SID=SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94F71zFdz38ipff84tvxK3WA.; __Secure-1PSID=SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94BTHFCCYieP10lfcTzk0bGg.; __Secure-3PSID=SAi5zTUd2DmC60-wQL3kf3w5bCzNcfoN0h0Xc6R90NPYKo94vV3WbO0fAktTb50xo-WCBg.; AEC=AakniGNewK4usJ7UpEwV5HrTNtmyc7U9n6nRe08XVE3UrvhaagEFcrHeZQ; OSID=SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxujev4G6mAlngNtmC_AK1KQ.; __Secure-OSID=SAi5zaIhsYgagRRfwQN_ucHvqabR4BbGeCbfsCrOvdGtZibxW7zVZHGl-IYYYFlXifYJWA.; OTZ=6828078_44_44_123780_40_436260; 1P_JAR=2022-12-25-21; NID=511=hmQDfXRlqQwPOmm65D7wqwvu2LHwwoGDN8HExpWvNH5tf2MPKo7hjUd81m7xMHZKr2h5M-K6e6XMNqVDpob5F8foTSKy4r1mlWuVBfj7U84HDLUDapU3iq0vlTHVEFgX4OVj1Z0YUP8oVsUaqNNmxWpvvfi91nEapYNa3YqtJtjGYEWjnYRpmX27rzfwek5fJ8C47gwwTlIFLTX3KH36FWyMsRbfor25KsGwmGxxome3jL8jFeGUYkmivF-Qe1S-Ck7zb70COU2ffV2ZLBIp-UsaX_o8jgQHVwDYPhPNYhbPUtgSPGy3nWwHh796Uhx5kiRqTeSmxPhxyFnPBbK-giQAEOvTKs9ww4lhMrFfqMbJs-7FbSR6EuvKjDqQ; COMPASS=meet-ui=CgAQtv-inQYaRwAJa4lXbKHY_YS-23pYX7BVH933fdP9rO13z7UVW_744DHga_SdhYtrQXXd_4FQn15HyziSoJga1xiWR3RU04fGN3NF6R24; SIDCC=AIKkIs2s5XnSSjuVBxnPNeTjjfxEVt5tZ0V2fmlgGbjOkbTxf9MtX5K5mDHZxhaRjX541rOF8WfF; __Secure-1PSIDCC=AIKkIs0BDlOhI3UvoBvHOYr76P3muMw5r9RHF9aKgIAhkWO_r55h2W9fDlD4OJEbjmF7zQ9yVU7M; __Secure-3PSIDCC=AIKkIs0W3MkJizpUjrxDrMlpNaiZXzU-HECll1GzQBEaU1EejCewJ6uuLbCKVo0AWI4BpJT1O5Am',
    'origin': 'https://meet.google.com',
    'referer': 'https://meet.google.com/hna-dqow-yzi',
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
    'x-compass-routing-destination': 'AHSoBRVtplKi9XWRMt_xziqIn2ThgdJNhFB4br8Js_j_MDCnIsb0SEz7EacexJRb6AzPp1NSrxUAEoSL7tlXV6rUe8KRqwikOnlmLutIkvA=',
    'x-goog-api-key': 'AIzaSyCG_6Rm6c7ucLr2NwAq33-vluCp2VfSkf0',
    'x-goog-authuser': '0',
    'x-goog-encode-response-if-executable': 'base64',
    'x-goog-meeting-debugid': 'boq_hlane_2WaQGHQvm90',
    'x-goog-meeting-rtcclient': 'CAEQqgMYASABKAg4AQ==',
    'x-goog-meeting-token': '1672003256132;AMz87TOsUAQ3r-zA71Nf-xJNeW4cpnVpoJnEKfn220gmMQPw7b-C1yDhEXavjyKXrTAS0T4oNEXPzIBBbJgfgQ8FdUO3H0lNW49IVTOxxjIJD8oJpjRzWf95KeVLUC_JL6pSAe_zhtsVxI4Dhg5xOjY8HzHsB56Ct-EjaUt0TFflfjpJWKTQcYeq7vJu3LjJ-M95dNkMH56uZ_vnCNxBmFdcUobnSo31u_1yjjpVd0IJD6EnZRRTmn0',
}

data = '\nD\n@spaces/cd2Omf-fMUYB/devices/8f53c99d-ba9e-4faa-ba60-680ef89a68ca \x01'

response = requests.post(
    'https://meet.google.com/$rpc/google.rtc.meetings.v1.MeetingDeviceService/UpdateMeetingDevice',
    cookies=cookies,
    headers=headers,
    data=data,
)
print(response.content)