from fastapi import FastAPI, HTTPException
import imapclient
import pyzmail
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

# Email account credentials
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

@app.get("/check-emails", response_model=List[dict])
async def get_new_emails():
    try:
        emails = check_for_new_emails()
        if not emails:
            raise HTTPException(status_code=404, detail="No new emails from alert senders.")
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run the FastAPI application
# Run this file using `uvicorn` command
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
