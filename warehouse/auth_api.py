import json
import random
import string
import threading

# Initialize authorization token
token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))


# token gen function
def keyGen():
    aes_key: str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return aes_key


# Every month call the keyGen function once to rotate the key
def timer():
    timer_gen = threading.Timer(2626560, timer, )
    timer_gen.start()
    # Refresh token
    token = keyGen()
    print(token)


def lambda_handler(event, context):
    print(event)
    auth = 'Deny'
    if event['authorizationToken'] == token:
        auth = 'Allow'
    else:
        auth = 'Deny'
    authResponse = {
        'principalId': token,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Resource": ["arn:aws:execute-api:us-east-1:855479483274:kx473b4cs0/*/POST/items",
                                 "arn:aws:execute-api:us-east-1:855479483274:kx473b4cs0/*/GET/items"],
                    "Effect": auth
                }
            ]

        }
    }
    return authResponse


timer()