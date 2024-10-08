from fastapi import FastAPI, HTTPException
import imapclient
import pyzmail
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import List

import requests

# Load environment variables from .env file
load_dotenv()

# Email account credentials
# Load environment variables
BASE_URL = os.getenv('ALARM_BASE_URL', 'http://localhost:8000')
USER_ID = os.getenv('USER_ID', '1')
JWT_TOKEN = os.getenv('JWT_TOKEN', '')
EMAIL_ACCOUNT = os.getenv("EMAIL_ID")
EMAIL_PASSWORD = os.getenv("APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
ALERT_SENDERS = ["noreply@e.fiverr.com", "surajairi04@gmail.com"]

# Initialize FastAPI app
app = FastAPI()

def check_for_new_emails():
    with imapclient.IMAPClient(IMAP_SERVER) as server:
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.select_folder('INBOX')

        # Get the current date and the date threshold for 2 days ago
        now = datetime.now()
        since_date = (now - timedelta(days=2)).strftime('%d-%b-%Y')

        # Create search criteria list
        search_criteria = ['UNSEEN', 'SINCE', since_date]

        # Search for all unseen (new) emails
        messages = server.search(search_criteria)
        print('Messages length', len(messages))

        email_details = []
        for uid in messages:
            raw_message = server.fetch([uid], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(raw_message[uid][b'BODY[]'])
            sender = message.get_address('from')[1]

            if sender in ALERT_SENDERS:
                subject = message.get_subject()
                email_details.append({
                    "sender": sender,
                    "subject": subject,
                    "date": message.get_decoded_header('date')
                })

        # Log out
        server.logout()

    return email_details

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/mail-alert')
async def get_mail_alert():
    try:
        emails = check_for_new_emails()
        if not emails:
            return {"message": "No new emails from alert senders."}
        send_fcm_alert(emails[0]['subject'])
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check-emails", response_model=List[dict])
async def get_new_emails():
    try:
        emails = check_for_new_emails()
        if not emails:
            raise HTTPException(status_code=404, detail="No new emails from alert senders.")
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# @app.get("/check-emails")
def send_fcm_alert(message="New Fiverr message received"):
    print("Sending FCM alert")
    url = f"{BASE_URL}/api/v1/admin/user/notification/{USER_ID}"

    # Set up the headers with the bearer token
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Define the payload
    payload = {
        "title": "Fiverr Notification",
        "body": message,
        "data": {
            "alert": "u_start"
        }
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Print the response
    print(response.status_code)
    print(response.json())


# To run the FastAPI application
# Run this file using `uvicorn` command
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
