import random
import string
WALLET_PREFIX_LIST = ["8600", "9860"]

def generate_wallet_id(length=12):
    return random.choice(WALLET_PREFIX_LIST)+ ''.join(random.choice(string.digits) for _ in range(length))