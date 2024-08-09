import time
import imapclient
import pyzmail
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


# Email account credentials
EMAIL_ACCOUNT = os.getenv("EMAIL_ID")
EMAIL_PASSWORD = os.getenv("APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"
AUDIO_PATH = 'assets/audio/alarm.mp3'
ALERT_SENDERS = ["noreply@e.fiverr.com","surajairi04@gmail.com"]

def alertFiverrMessage():
    print("Fiverr message received")
    # play sound
    os.system("afplay " + AUDIO_PATH)




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
        print('Messages length',len(messages))

        for uid in messages:
            raw_message = server.fetch([uid], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(raw_message[uid][b'BODY[]'])
            sender = message.get_address('from')[1]

            if sender in ALERT_SENDERS :
                subject = message.get_subject()
                print(subject)
                alertFiverrMessage()


        # Log out
        server.logout()

if __name__ == "__main__":
    delay = 600
    while True:
        print("Iteration Started...")
        check_for_new_emails()
        print("Completed!!!\n")
        print(f"\nWaiting for {delay} seconds...")
        time.sleep(delay)  # Check every  10 minutes
