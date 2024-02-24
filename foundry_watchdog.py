import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests


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
                    print(f"User authentication successful for user: {user}")
                    self.send_notification(user)

    def send_notification(self, user):
        text = f"User authentication successful for user: {user}"
        send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={text}'
        response = requests.get(send_text)
        return response.json()


if __name__ == "__main__":
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    log_path = settings['log_path']
    log_filename = settings['log_filename']
    bot_token = settings['bot_token']
    chat_id = settings['chat_id']
    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=log_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        event_handler.send_notification(f"Script has crashed with error: {str(e)}")
        observer.stop()
    observer.join()
