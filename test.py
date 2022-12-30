import json

import requests


data = json.dumps(
    {
        'users': [772311962],
        'text': 'ee',
        'sum': 'ref'
    }
)

response = requests.post(
    'https://4roonas.xyz/1559698745UZuq7Ftdmcov6HnSdvT33iX5MFaKepI3',
    data=data,
)
print(response.content)