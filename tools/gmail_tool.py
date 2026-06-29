import os.path
import base64

from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# =====================================
# GMAIL API SCOPES
# =====================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify"
]


# =====================================
# AUTHENTICATE GMAIL
# =====================================

def authenticate_gmail():

    creds = None

    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:

            token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


# =====================================
# SEND EMAIL
# =====================================

def send_email(to, subject, body):

    service = authenticate_gmail()

    message = MIMEText(body)

    message["to"] = to
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    send_message = (
        service.users()
        .messages()
        .send(
            userId="me",
            body={"raw": raw_message}
        )
        .execute()
    )

    return {
        "status": "SUCCESS",
        "message_id": send_message["id"]
    }


# =====================================
# READ RECENT EMAILS
# =====================================

def read_recent_emails(max_results=3):

    service = authenticate_gmail()

    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results
        )
        .execute()
    )

    messages = results.get("messages", [])

    email_data = []

    for msg in messages:

        txt = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"]
            )
            .execute()
        )

        payload = txt["payload"]

        headers = payload["headers"]

        subject = "No Subject"
        sender = "Unknown"

        for d in headers:

            if d["name"] == "Subject":
                subject = d["value"]

            if d["name"] == "From":
                sender = d["value"]

        email_data.append({
            "subject": subject,
            "from": sender
        })

    return email_data


# =====================================
# READ FULL EMAIL CONTENT
# =====================================

def read_email_content(email_index=1):

    service = authenticate_gmail()

    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=10
        )
        .execute()
    )

    messages = results.get("messages", [])

    if not messages:

        return {
            "from": "Unknown",
            "subject": "No Subject",
            "body": "No emails found."
        }

    if email_index > len(messages):

        return {
            "from": "Unknown",
            "subject": "Invalid",
            "body": "Invalid email index."
        }

    msg_id = messages[email_index - 1]["id"]

    message = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=msg_id,
            format="full"
        )
        .execute()
    )

    payload = message["payload"]

    headers = payload.get("headers", [])

    subject = "No Subject"
    sender = "Unknown"

    for h in headers:

        if h["name"] == "Subject":
            subject = h["value"]

        if h["name"] == "From":
            sender = h["value"]

    body = ""

    parts = payload.get("parts")

    if parts:

        for part in parts:

            mime_type = part.get("mimeType")

            if mime_type == "text/plain":

                data = part["body"].get("data")

                if data:

                    body = base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8")

                    break

    else:

        data = payload["body"].get("data")

        if data:

            body = base64.urlsafe_b64decode(
                data
            ).decode("utf-8")

    return {
        "from": sender,
        "subject": subject,
        "body": body
    }


# =====================================
# CREATE DRAFT
# =====================================

def create_draft(to, subject, body):
    service = authenticate_gmail()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    draft = (
        service.users()
        .drafts()
        .create(
            userId="me",
            body={"message": {"raw": raw_message}}
        )
        .execute()
    )
    return {
        "status": "SUCCESS",
        "draft_id": draft["id"]
    }


# =====================================
# MODIFY LABELS (FLAG / STAR / UNSTAR)
# =====================================

def modify_email_labels(email_index=1, add_labels=None, remove_labels=None):
    service = authenticate_gmail()
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=10
        )
        .execute()
    )
    messages = results.get("messages", [])
    if not messages:
        return {"status": "ERROR", "message": "No emails found."}
    if email_index > len(messages):
        return {"status": "ERROR", "message": "Email index out of range."}
        
    msg_id = messages[email_index - 1]["id"]
    body = {}
    if add_labels:
        body["addLabelIds"] = add_labels
    if remove_labels:
        body["removeLabelIds"] = remove_labels
        
    service.users().messages().batchModify(
        userId="me",
        body={"ids": [msg_id], **body}
    ).execute()
    
    return {
        "status": "SUCCESS",
        "message": f"Labels modified successfully for email index {email_index}."
    }