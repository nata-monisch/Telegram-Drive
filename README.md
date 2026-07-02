# Telegram Drive
Telegram Drive is an open-source application that turns your Telegram account into an unlimited, secure cloud storage drive. Built with Python.

Telegram Drive leverages the Telegram API to allow you to upload, organize, and manage files directly on Telegram's servers. It treats your "Saved Messages" and created Channels as folders, giving you a familiar file explorer interface for your Telegram cloud.

## Feature
* Virtual File System: Manage files and folders with a hierarchical structure without having to manually upload each file.
* Two-Way Sync: Automatically synchronize messages in Telegram with the app's index. Files deleted in Telegram will automatically disappear in the app, and vice versa.
* Context Menu (Windows Explorer Style): Right-click on a file/folder for quick access to Rename, Delete, Share, Download, and Preview.
* Mass Operations: Supports multi-select to move, delete, or share multiple files at once.
* Recursive Delete & Share: Delete or share a folder and all its files and subfolders with just one click.
* Fast Upload/Download: Uses `cryptg` for optimal encryption and file transfer speeds.
* Previewer: Built-in preview support for text, document, and image files.
## Installation
1. Clone the repository
```bash
git clone https://github.com/nata-monisch/Telegram-Drive.git
cd Telegram-Drive
```
2. Install dependencies
```bash 
python -m pip install PyQt6 telethon qasync cryptg
```

3. Telegram API Credentials
You need your own API ID and API Hash to communicate with Telegram's servers.
- Log into [my.telegram.org](https://my.telegram.org).
- Go to "API development tools" and create a new application to get your `api_id` and `api_hash`.

4. Run
```bash
py main.py
```
## Open Source & License
This project is Free and Open Source Software. You are free to use, modify, and distribute it.
Licensed under the MIT License.

**Disclaimer** : This application is not affiliated with Telegram FZ-LLC. Use responsibly and in accordance with Telegram's Terms of Service.