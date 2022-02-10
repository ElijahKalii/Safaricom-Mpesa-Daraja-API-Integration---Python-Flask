import requests
from requests.auth import HTTPBasicAuth
from mpesa_exceptions import *
from requests import Response
import time
import os
import json
import base64
from datetime import datetime

mpesa_environment = 'production'          	# "sandbox" if development or "production" if live environment
base_url = 'https://example.com'			#this is the public domain prefix for your App
sandbox_paybill = '123456'					# the sandbox shortcode(paybill) for simulation given by daraja on www.developer.safaricom.co.ke
mpesa_paybill = '654321'					#your business/production shortcode (paybill) number
consumer_key = os.environ.get("MPESA_CONSUMER_KEY")		#The key. This will be displayed on your App at www.developer.safaricom.co.ke.
consumer_secret = os.environ.get("MPESA_CONSUMER_SECRET")   #The secret code. This will be displayed on your App at www.developer.safaricom.co.ke.

if mpesa_environment == 'sandbox':			#define the shortcode based on your environment
    business_short_code = sandbox_paybill
else:
	business_short_code = mpesa_paybill


def api_base_url():
    """This function will change the daraja endpoint domain depending on whether we are in the 
    sandbox (development) environment or the production(live) environment

    Returns:
        domain (url): the prefix domain for our APIs
    """
	if mpesa_environment == 'sandbox':
		return 'https://sandbox.safaricom.co.ke/'
	elif mpesa_environment == 'production':
		return 'https://api.safaricom.co.ke/'


def format_phone_number(phone_number):
    """Format the phone number from the customer to match what daraja API expects

    Args:
        phone_number (str)): phone number provided by the customer

    Returns:
        formated phone number (str): phone number starting with 254 formatted as text
    """
	if len(phone_number) < 9:
		return 'Phone number too short'
	else:
		return '254' + phone_number[-9:]


def generate_access_token(consumer_key, consumer_secret):
    
    """This will generate the autorization token we need to make the daraja request for a stk push
    Args:
			consumer_key (str): -- consumer_key (above)
            consumer_secret (str): -- consumer_secret (above)
    Returns:
        token (str): We have indexed the token string from the response json containing a token and the expiry. 
    """
    url = api_base_url() + 'oauth/v1/generate?grant_type=client_credentials'
    
    try:
        r = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret)).json()
        token = r['access_token']
    except Exception as ex:
        print("Could not generate access code")
        return ex
    return token


def register_mpesa_url():
    
    """You will need to register an endpoint for valiating the payments and another for receiving the confirmations 
    from daraja API

    Returns:
        json: confirmation for a successiful registration 
    """
	mpesa_endpoint = api_base_url() + 'mpesa/c2b/v1/registerurl'            #endpoint we need to call to register our urls
	headers = {
		'Authorization': 'Bearer ' + generate_access_token(consumer_key, consumer_secret),
		'Content-Type': 'application/json'
	}
	req_body = {
		'ShortCode': business_short_code,
		'ResponseType': 'Completed',
		'ConfirmationURL': base_url + '/confirm',
		'ValidationURL': base_url + '/validate'}
	
	response_data = requests.post(mpesa_endpoint,json=req_body,headers=headers)
	return response_data.json()


#stk push for incoming payments. Credit to https://github.com/martinmogusu/django-daraja
def stk_push(phone_number, amount, account_reference, transaction_desc):
	"""
	Attempt to send an STK prompt to customer phone
		Args:
			phone_number (str): -- The Mobile Number to receive the STK Pin Prompt.
			amount (int) -- This is the Amount transacted normaly a numeric value. Money that customer pays to the Shorcode. Only whole numbers are supported.
			account_reference (str) -- This is an Alpha-Numeric parameter that is defined by your system as an Identifier of the transaction for CustomerPayBillOnline transaction type. Along with the business name, this value is also displayed to the customer in the STK Pin Prompt message. Maximum of 12 characters.
			transaction_desc (str) -- This is any additional information/comment that can be sent along with the request from your system. Maximum of 13 Characters.
			call_back_url (str) -- This s a valid secure URL that is used to receive notifications from M-Pesa API. It is the endpoint to which the results will be sent by M-Pesa API.
		Returns:
			MpesaResponse: MpesaResponse object containing the details of the API response
		
		Raises:
			MpesaInvalidParameterException: Invalid parameter passed
			MpesaConnectionError: Connection error
	"""

	if str(account_reference).strip() == '':
		raise MpesaInvalidParameterException('Account reference cannot be blank')
	if str(transaction_desc).strip() == '':
		raise MpesaInvalidParameterException('Transaction description cannot be blank')
	if not isinstance(amount, int):
		raise MpesaInvalidParameterException('Amount must be an integer')

	callback_url = base_url + '/confirm'                   #This is the endpoint you have created in your app to receive the notifications from mpesa
	phone_number = format_phone_number(phone_number)                #validate the phone number of the customer
	url = api_base_url() + 'mpesa/stkpush/v1/processrequest'        #this is the daraja API endpoint we need to send our request to 
	passkey = os.environ.get('MPESA_PASSKEY')                       #safaricom will send you this passkey on go-live

	timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
	password = base64.b64encode((business_short_code + passkey + timestamp).encode('ascii')).decode('utf-8')   #base64 encoded string made up of your shortcode(paybill), passkey and timestamp
	transaction_type = 'CustomerPayBillOnline'
	party_a = phone_number
	party_b = business_short_code

	data = {
		'BusinessShortCode': business_short_code,
		'Password': password,
		'Timestamp': timestamp,
		'TransactionType': transaction_type,
		'Amount': amount,
		'PartyA': party_a,
		'PartyB': party_b,
		'PhoneNumber': phone_number,
		'CallBackURL': callback_url,
		'AccountReference': account_reference,
		'TransactionDesc': transaction_desc
	}

	headers = {
		'Authorization': 'Bearer ' + generate_access_token(consumer_key, consumer_secret),
		'Content-Type': 'application/json'
	}

	try:
		r = requests.post(url, json=data, headers=headers)
		response = r.json()
		return response
	except requests.exceptions.ConnectionError:
		raise MpesaConnectionError('Connection failed')
	except Exception as ex:
		raise MpesaConnectionError(str(ex))
