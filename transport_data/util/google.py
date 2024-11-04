from typing import TYPE_CHECKING

from platformdirs import user_data_path

if TYPE_CHECKING:
    import googleapiclient.discovery


def get_service(
    *args, scopes: list[str], **kwargs
) -> "googleapiclient.discovery.Resource":
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    udp = user_data_path("transport-data")
    credentials_path = udp.joinpath("google-cloud-credentials.json")
    token_path = udp.joinpath("google-cloud-token.json")

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is created
    # automatically when the authorization flow completes for the first time.
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, scopes
                )
            except FileNotFoundError:
                raise RuntimeError(f"No Google API credentials at {credentials_path}")
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        token_path.write_text(creds.to_json())

    kwargs.update(credentials=creds)
    return build(*args, **kwargs)
