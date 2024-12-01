import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# APIに要求する権限を指定
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def create_event(service, summary, location, description, start_time, end_time):
    """
    Google Calendarに新しいイベントを作成する。
    """
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Tokyo',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'イベントが作成されました: {event["htmlLink"]}')

def main():
    """
    ユーザーのカレンダーに新しいイベントを作成する。
    """
    creds = None
    # ユーザーのアクセスとリフレッシュトークンを格納するtoken.jsonファイルが存在する場合、token.jsonを使用して認証する。
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # 有効な資格情報がない場合、ユーザーにログインさせます。
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # 次回実行のために資格情報を保存する。※二回目以降の実行では認証がスキップされる。
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # イベントの詳細を指定します。
        summary = '新しいイベント'
        location = '東京'
        description = 'これはテストイベントです。'
        start_time = '2024-08-16T12:00:00'
        end_time = '2024-08-16T18:00:00'

        # イベントを作成します。
        create_event(service, summary, location, description, start_time, end_time)

    except HttpError as error:
        print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
    main()