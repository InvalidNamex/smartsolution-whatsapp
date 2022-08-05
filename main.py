import time

import uvicorn
from fastapi import FastAPI, Response, Request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import requests
import os
from dotenv import load_dotenv
app = FastAPI()
load_dotenv()


@app.post("/")
async def receive_message_from_sandbox(request: Request):
    resp = MessagingResponse()
    response_msg = resp.message()
    form = await request.form()
    message = form["Body"]
    sender_number = form["From"]
    url = "https://www.suezcanal.gov.eg:443/Arabic/_layouts/15/LINKDev.SCA.WaterServices/WaterServicesInfo.aspx/GetWaterServicesInfo"
    if '+' not in message.split():
        welcome_message(sender_number)
    else:
        user_input = message.split('+')
        counter_code = int(user_input[0])
        client_code = int(user_input[1])
        data = {
            "pUrl": "/waterservice_api/Invoices.svc/GetWaterServiceInfo2",
            "meterID": counter_code,
            "code": client_code
        }
        response = requests.post(url, json=data)
        if not response.json()['d']['IsWrongData']:
            citizen = response.json()['d']['Citizen']
            invoices = response.json()['d']['Invoices']
            reply(sender_number,
                  f'''الاسم:{citizen['Name']}\nالعنوان:{citizen['Address']}\nاجمالي الفواتير:{citizen['TotalDues']}\nعدد الفواتير:{len(invoices)}''')
            for i in invoices:
                reply(sender_number,
                      f'''تاريخ الفاتورة:{i['DueInvoiceDate']}\nمبلغ الفاتوة:{i['DueValue']}'''
                      )
                time.sleep(1)
        else:
            response_msg.body('برجاء التأكد من البيانات المدخلة')
        return Response(content=str(resp), media_type="application/xml")


def welcome_message(sender_number):
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    client.messages.create(
        from_='whatsapp:+14155238886',
        body='للاستعلام عن فواتيرك برجاء ادخال رقم العداد + رقم المشترك \n مثال: 12345 + 123456',
        to=sender_number
    )


def reply(sender_number, body):
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    client.messages.create(
        from_='whatsapp:+14155238886',
        body=body,
        to=sender_number
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
