import requests
import json
import random
import base64
import hmac
import hashlib
import time
from Crypto import Random
from Crypto.Cipher import AES
import logging
logger = logging.getLogger(__name__)

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


class ZebPay:
  def __init__(self, authObj, host):
    self.country_code = authObj['country_code']
    self.mobile_number = authObj['mobile_number']
    self.client_id = authObj['client_id']
    self.client_secret = authObj['client_secret']
    self.api_secret = authObj['api_secret']
    self.authorization_token = authObj['authorization_token']
    self.req_limit_conf = authObj['req_limit_conf']
    self.otp = authObj['otp']
    self.pin = authObj['pin']
    self.host = host
    # self.subscription_key = subscription_key
    logger.debug(['self', json.dumps(self.__dict__)])

  def _pad(self, s):
    return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

  def aesEncrypt(self, text, key):
    return base64.b64encode(AES.new(key.replace('-', '')[:16].encode(), AES.MODE_ECB).encrypt(self._pad(text).encode())).decode()

  def login(self):
    _login_route = 'user/login'
    _body = {
        'country_code': self.country_code,
        'mobile_number': self.mobile_number,
        'client_id': self.client_id,
        'client_secret': self.client_secret,
    }

    return self.init_http_req(_login_route, 'POST', _body)

  def verify_otp(self, verification_code):
    _otp_route = 'user/verifyotp'
    _body = {
        'otp': self.otp,
        'verification_code': verification_code,
        'client_id': self.client_id,
        'client_secret': self.client_secret
    }
    return self.init_http_req(_otp_route, 'POST', _body)

  def verify_pin(self, verification_code):
    _pin_route = 'user/verifypin'
    _body = {
        'grant_type': 'user_credentials',
        'pin': self.pin,
        'verification_code': verification_code,
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        **self.req_limit_conf
    }
    pin_res = self.init_http_req(_pin_route, 'POST', _body).json()
    self.authorization_token = pin_res['data']['access_token']
    return pin_res['data']

  def authenticate_me(self):
    login_res = self.login().json()
    print('login_res........', login_res)

    # if(login_res.statusCode == 200):
    otp_res = self.verify_otp(login_res['data']['verification_code']).json()
    print('otp_res..........', otp_res)
    # if(otp_res.statusCode == 200):
    pin_res = self.verify_pin(otp_res['data']['verification_code'])
    print('Completed authetication........', pin_res)

  def compute_signature(self, target_url, method, body, timestamp):
    print('body........', body)
    seprator = '\n'
    payload_msg = f'POST{seprator}{timestamp}{seprator}{target_url}{body is None if json.dumps({}) else json.dumps(body)}{seprator}client_Id:{self.client_id}'
    payload_msg = bytes(payload_msg, 'utf-8')
    return base64.b64encode(hmac.new(payload_msg, bytes(self.client_secret, 'utf-8'), digestmod=hashlib.sha256).digest())

  def get_secure_header(self, target_url, method, body, timestamp):
    # cs = self.compute_signature(target_url, method, body, timestamp).decode()
    # print('cs.....', cs)
    return {
        'ApiSignature': self.compute_signature(target_url, method, body, timestamp).decode(),
        'Authorization': f'Bearer {self.authorization_token}',
        'Content-Type': 'application/json',
        'RequestId': str(random.randint(100000, 999999)),
        # 'Zebpay-Subscription-Key': self.subscription_key,
        'client_id': self.client_id,
        'timestamp': str(timestamp)
    }

  def get_balance(self, pair):
    _balance_route = f'orders/{pair}/balance'
    return self.init_http_req(_balance_route, 'GET', {})

  def place_instant_order(self, size, trade_pair, side, price):
    _instant_trade_route = '/orders/instant'
    _body = {
        'size': size,
        'trade_pair': trade_pair,
        'side': side,
        'price': price,
        'pin': self.aesEncrypt(self.pin, self.api_secret)
    }
    return self.init_http_req(_instant_trade_route, 'POST', _body)

  def init_http_req(self, url, method, body):
    try:
      target_url = f'{self.host}{url}'
      method = method.upper()
      response = None
      headers_to_sent = self.get_secure_header(
          target_url, method, body, int(time.time()))
      print('headers_to_sent', headers_to_sent)
      if method == 'POST':
        response = requests.post(
            target_url, json=body, headers=headers_to_sent)
        # print('API', response.json())
        # print('API requests', requests.headers)
      elif method == 'GET':
        response = requests.get(target_url, headers=headers_to_sent)

      return response
    except Exception as e:
      print('Error', e)
