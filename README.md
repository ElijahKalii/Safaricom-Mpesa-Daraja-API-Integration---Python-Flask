# **Safaricom Daraja API for C2B Express Mpesa payments** 

# Welcome the the Safaricom Mpesa Daraja API integration with Python and Flask micro-framework

## This is a powerful way to enable your customers to quickly remit payments using Express Mpesa STK push when they visit your website/App.<br><br> 

## We make the HTTP request to Daraja API, receive the response, and send the payment details to a MYSQL database <br><br>

* The App should work AS-IS. 
You only need to plug in your creds into the environment variables, and ensure you have a public domain or a public IP Address to commmunicate with the Daraja API

* Navigate to generate /mpesa_token to get the access token, /register_mpesa_url to register your validation and confirmation urls

* You may name your validation and confirmation urls anyhow you want. In this APP I have named them /validate and /confirm respectively. The validation url wil enable you to validate the transaction before it is completed. If you leave it blank (like in this case), its assumed you have accepted the payment and Daraja will proceed confirm the payment. <br><br>

## Read more here:

* [Daraja API documentation](https://developer.safaricom.co.ke)**
* [Martin Mogusu GitHub Repo]( https://github.com/martinmogusu/django-daraja)
* [Ben Njunge Repo for a detailed tutorial incuding sandbosimulations](https://github.com/bnjunge/MPESA-API-Tutorial)

---
<br><br>
### _If you have any feedback or questions, reach out to me on elijahkalii@gmail.com_
