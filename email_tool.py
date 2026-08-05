from __future__ import annotations

import os
import base64
import mimetypes

from typing import List, Optional

from email.message import EmailMessage

from langchain_core.tools import tool

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


def get_gmail_service():

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

    return build(
        "gmail",
        "v1",
        credentials=creds
    )



def Send_email(
    recipients: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    html: bool = False,
    reply_to: Optional[str] = None,
    priority: str = "normal"
) -> str:
    
    try:

        service = get_gmail_service()

        message = EmailMessage()

        message["To"] = ", ".join(recipients)

        if cc:
            message["Cc"] = ", ".join(cc)

        if bcc:
            message["Bcc"] = ", ".join(bcc)

        message["Subject"] = subject

        if reply_to:
            message["Reply-To"] = reply_to

        if priority.lower() == "high":
            message["X-Priority"] = "1"

        elif priority.lower() == "low":
            message["X-Priority"] = "5"

        if html:
            message.add_alternative(
                body,
                subtype="html"
            )
        else:
            message.set_content(body)

        if attachments:

            for filepath in attachments:

                if not os.path.exists(filepath):
                    continue

                mime_type, _ = mimetypes.guess_type(filepath)

                if mime_type is None:
                    mime_type = "application/octet-stream"

                maintype, subtype = mime_type.split("/", 1)

                with open(filepath, "rb") as f:

                    message.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(filepath)
                    )

        raw = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        service.users().messages().send(
            userId="me",
            body={
                "raw": raw
            }
        ).execute()

        return (
            f"Successfully sent email to "
            f"{', '.join(recipients)}."
        )

    except Exception as e:

        return f"Email sending failed.\n\n{str(e)}"