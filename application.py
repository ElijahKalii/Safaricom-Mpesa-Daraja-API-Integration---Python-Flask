#import required packages
from flask import Flask, render_template, request,session
from flask_sqlalchemy import SQLAlchemy
from static.mpesa_config import generate_access_token, register_mpesa_url, stk_push
import os
import pymysql

#create a Flask object
application = Flask(__name__)

#establish a connection to our MYSQL server using sqlalchemy ORM. I assume you are saving all creds into environment variables
database = os.environ.get("NAME_OF_YOUR_MYSQL_DB")
db_username = os.environ.get("YOUR_MYSQL_USERNAME")
db_password = os.environ.get("YOUR_MYSQL_PASSWD")
db_host = os.environ.get("YOUR_MYSQL_HOST")         #the uri to the db

#create a database connection
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(db_username, db_password, db_host, database)
application.config['SQLALCHEMY_DATABASE_URI'] = (conn)
db = SQLAlchemy(application)

from static import models

@application.route('/', methods=['GET']) 
def Home():
    return render_template ("home.html")

@application.route('/mpesa_token')
def access_token():
    consumer_key = os.environ.get("MPESA_CONSUMER_KEY")
    consumer_secret = os.environ.get("MPESA_CONSUMER_SECRET")
    return generate_access_token(consumer_key, consumer_secret)


@application.route('/register_mpesa_url')
def register_url():
    return register_mpesa_url()


@application.route('/validate', methods=['POST'])
def validate():
    if request.method == 'POST':
        jsonMpesaResponse = request.get_json()  
        print(jsonMpesaResponse)
        return render_template ("home.html")

@application.route('/confirm', methods=['POST'])
def confirm():
    if request.method == 'POST':
        jsonMpesaResponse = request.get_json()          #receive the json from Daraja API and write it to your MYSQL database
        
        #We shall write every payment details into our MYSQL database by the help of the sqlalchemy ORM session
        try:
            add_pmt = models.client_payments_table(TransactionType=jsonMpesaResponse['TransactionType'], TransID=jsonMpesaResponse['TransID'], \
                                                     TransTime=jsonMpesaResponse['TransTime'], TransAmount=jsonMpesaResponse['TransAmount'], \
                                                     BusinessShortCode=jsonMpesaResponse['BusinessShortCode'], BillRefNumber=jsonMpesaResponse['BillRefNumber'], \
                                                     InvoiceNumber=jsonMpesaResponse['InvoiceNumber'], OrgAccountBalance=jsonMpesaResponse['OrgAccountBalance'], \
                                                     ThirdPartyTransID=jsonMpesaResponse['ThirdPartyTransID'], MSISDN=jsonMpesaResponse['MSISDN'], \
                                                     FirstName=jsonMpesaResponse['FirstName'], MiddleName=jsonMpesaResponse['MiddleName'], LastName=jsonMpesaResponse['LastName'])
            db.session.add(add_pmt)
        except Exception as e:
            print("Could not write payment details to database")
            print(jsonMpesaResponse)
            print(e)
            db.session.rollback()
        else:
            db.session.commit()
        finally:
            db.session.close()
    return render_template ("home.html")


#Our application URL for collecting request data and firing the payment process
@application.route('/mobile_payment')
def mobilePayment():
    phone_number = '254722456789'
    amount = 1000                       #ensure amount is an integer and not a floating point number
    account_reference = 'TEST123'       #This is the reference that will appear as the account number on the paybill payment
    transaction_desc = 'Payment for supplies'   #Any description
    return stk_push(phone_number, amount, account_reference, transaction_desc)      #Invoke the stk-push function with the request data

if __name__== "__main__":
    application.run()