# zeb_py
Zebpay REST Client

This is a simple example package to help people in integrating Zebpay REST APIs using `python`.

Getting Started

The file `./zebpay_client/zebpay_rest_client.py` comes with folowing API implementations

1. Login
2. Verify OTP
3. Verify PIN
4. Balance
5. Instant Buy/Sell

You can call function - `authenticate_me` which will initiate Login, VerifyOTP and VerfiyPIN APIs and autherize with your details provided via `ZebPay` class instance.

 Sample use

```
# Create an instance of `ZebPay` class in your code which can be find in `project_directory/zebpay_client/zebpay_rest_client.py`

z1 = ZebPay({
  'country_code': '<country_code>',
  'mobile_number': '<mobile_number>',
  'client_id': '<client_id>',
  'client_secret': '<client_secret>',
  'api_secret': '<api_secret>',
  'authorization_token': '<this_will_be_set_after_successful_authentication>',
  'req_limit_conf': {
    'daily_trade_limit': <your_choice>,
    'daily_withdraw_limit': <your_choice>,
    'total_trade_limit': <your_choice>,
    'total_withdraw_limit': <your_choice>,
    'scope': '<your_choice example - openid profile wallet:transactions:read wallet:transactions:send wallet:address:read trade:read trade:create offline_access>',
  },
  'otp': '<your_otp>',
  'pin': '<your_pin>'
  }, 'https://www.zebpay.com/api/v1/')

  print('Completed authetication........', z1.authenticate_me())
  print('Balances................', z1.get_balance('BTC-AUD').json())
  print('Instant................', z1.place_instant_order(0.005, 'BTC-AUD', 'buy', 14000.61).json())

```

