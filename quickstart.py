from __future__ import print_function
import os
import os.path
import time
import pandas as pd
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '11Bn1nAwJXT71pZ_MFxN4CBT8nLp2ezppswHnrVqlBnk'
SAMPLE_RANGE_NAME = 'Recieved Responses'
page_id = 112468098455034 
post_url = 'https://graph.facebook.com/{}/feed'.format(page_id)
AccessToken = "EAAZAYsPabWhcBAArEpHYWlmzIq0L4M9SBYDqFrwZCmO9OgQBMYMelDPBZCF6zbSuZAuBBBEBO3Njn61n1NilqOZBzPoiobjpk2IkJIqp5EqxXhhB2mXjwqpLmfJDFxzcqWOIgQnf8v9onYXXn0btLMntOKvpYp2GIRHxG13UqeKxZBd66G3Uui"




def postFB(row,postNumber):
    newRow = []
    i=0
    info = ""
    for x in row:
        if x is not None:
            newRow.append(x.encode('utf-8'))
        else:
            newRow.append( x)
        i+=1
    for j in range(2,7):
        if(row[j] != "None"):
            info = info + row[j] + " "
    msg = "#"+str(postNumber)+ " " + info + "\n" + '"'+ row[1] + ' ' + '"' 
    payload =  {'message' :msg, 'access_token': AccessToken}
    requests.post(post_url,data=payload)

def main():
    print("STARTING...")
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    while True:
        try:

            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])
            df = pd.DataFrame(values)
            df_replace = df.replace([''], ["None"])
            processed_dataset = df_replace.values.tolist()

            Post_Number = 0
            i = 0
            if not values:
                print('No data found.')
                return
            for sent in processed_dataset:
                if (sent[8] == "TRUE" and sent[9] == "TRUE"):
                    if (int(sent[10]) > Post_Number): Post_Number = int(sent[10])
            for row in processed_dataset:
                i += 1

                if (row[8] == "TRUE" and row[9]=="FALSE"):
                    Post_Number += 1
                    range_name = "Recieved Responses!J"+str(i)
                    values= [
                        ['TRUE'],
                        [Post_Number]
                        ]
                    body = {
                        'majorDimension': 'COLUMNS',
                        'values': values
                    }
                    postFB(processed_dataset[i-1],Post_Number)
                    service.spreadsheets().values().update(
                        spreadsheetId = SAMPLE_SPREADSHEET_ID,
                        range = range_name,
                        valueInputOption = 'USER_ENTERED',
                        body=body).execute()
            print("RUNNING...")
            time.sleep(600)
        except HttpError as err:
            print(err)


if __name__ == '__main__':
    main()



