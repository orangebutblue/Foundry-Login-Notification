import atexit
import json
import signal
import sys
import time

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

notification_message = "User logged in: "
settings_filename = "settingsme.json"


def send_discord_notification(message, user):
    text = message + user
    data = {
        "content": text
    }
    response = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    if response.text:  # Check if the response contains any data
        try:
            print(response.json())
            return response.json()
        except json.JSONDecodeError:
            print("The response does not contain valid JSON data.")
            return None
    else:
        return None


def send_telegram_notification(message, user):
    text = message + user
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={text}'
    response = requests.get(send_text)
    return response.json()


def send_notification(message, user):
    if user not in ignore_list:
        if notification_service == 'telegram':
            send_telegram_notification(message, user)
        elif notification_service == 'discord':
            send_discord_notification(message, user)
    else:
        print(f"Ignore list User logged in: {user}. Not sending notification.")


class LogFileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_read_position = {}

    def on_modified(self, event):
        try:
            if event.src_path == log_path + log_filename:
                self.process(event)
        except Exception as e:
            print(f"An error occurred: {e}")

    def process(self, event):
        with open(event.src_path, "r") as file:
            if event.src_path not in self.last_read_position:
                # If this is the first time we're opening the file, seek to the end
                file.seek(0, 2)
            else:
                # If we've opened the file before, seek to the last read position
                file.seek(self.last_read_position[event.src_path])
            lines = file.readlines()
            self.last_read_position[event.src_path] = file.tell()
            for line in lines:
                log_entry = json.loads(line)
                message = log_entry.get('message', '')
                if "User authentication successful for user" in message:
                    user = message.split("User authentication successful for user")[-1].strip()
                    send_notification(notification_message, user)


def shutdown_notification():
    send_notification("Script is now shutting down", "")


def signal_handler(sig, frame):
    shutdown_notification()
    sys.exit(0)


if __name__ == "__main__":
    with open(settings_filename, 'r') as f:
        settings = json.load(f)
    log_path = settings['log_path']
    log_filename = settings['log_filename']
    notification_service = settings['notification_service']
    if notification_service == 'telegram':
        bot_token = settings['telegram']['bot_token']
        chat_id = settings['telegram']['chat_id']
    elif notification_service == 'discord':
        webhook_url = settings['discord']['webhook_url']
    else:
        raise ValueError("Invalid notification_service. Please use 'telegram' or 'discord'")
    if settings['ignore_users']:
        ignore_list = settings['ignore_users']
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(shutdown_notification)
    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=log_path, recursive=False)
    observer.start()
    send_notification("Script has started", "")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        send_notification(f"Script has crashed with error: {str(e)}")
        observer.stop()
    observer.join()
