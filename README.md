# Foundry Watchdog

This is a simple watchdog for Foundry VTT. It will monitor the Foundry VTT log file and send a Telegram notification if a user logs in.

## Installation
### 1. Install requirements:
  * python3 packages:
    * requests
    * watchdog

 ### 2. Modify the settings.json
* Modify log_path and log_filename
* Get your Telegram Chat ID (for example, talk to `@getidsbot`)
* Create a bot and get the bot token (talk to `@BotFather`)
* Talk to your but at least once, so it's able to message you (`/start`)
* Modify the settings.json to include your chat_id and bot_token

### 3. Run the script
Run the script to see if it's working.

### 4. Install script as a service
* Modify the foundry_watchdog.service to point to the correct path
* Copy foundry_watchdog.service to /etc/systemd/system/
* enable and start the service
  ```
  systemctl enable foundry_watchdog.service
  systemctl start foundry_watchdog
  ```
