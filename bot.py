import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

TERABOX_USER = os.getenv("TERABOX_USER")
TERABOX_PASS = os.getenv("TERABOX_PASS")

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

TERABOX_MOUNT_PATH = "./terabox_mount"
RCLONE_CONFIG_PATH = "./rclone.conf"

def write_rclone_config():
    content = f"""
[terabox]
type = webdav
url = https://dav.terabox.com/dav
vendor = other
user = {TERABOX_USER}
pass = {TERABOX_PASS}
"""
    with open(RCLONE_CONFIG_PATH, "w") as f:
        f.write(content)

def mount_terabox():
    os.makedirs(TERABOX_MOUNT_PATH, exist_ok=True)
    # Write rclone.conf with credentials before mounting
    write_rclone_config()
    # Mount with rclone using the config
    subprocess.Popen([
        "rclone", "mount", "terabox:", TERABOX_MOUNT_PATH,
        "--config", RCLONE_CONFIG_PATH,
        "--allow-other",
        "--daemon"
    ])

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("Bot started and connected to TeraBox!")

@app.on_message(filters.command("list"))
async def list_files(client, message: Message):
    try:
        files = os.listdir(TERABOX_MOUNT_PATH)
        if files:
            await message.reply_text("Files in TeraBox:\n" + "\n".join(files))
        else:
            await message.reply_text("No files found!")
    except Exception as e:
        await message.reply_text(f"Error reading files: {e}")

@app.on_message(filters.command("get"))
async def get_file(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /get filename")
        return
    filename = message.command[1]
    filepath = os.path.join(TERABOX_MOUNT_PATH, filename)
    if os.path.exists(filepath):
        await message.reply_document(filepath)
    else:
        await message.reply_text("File not found!")

if __name__ == "__main__":
    mount_terabox()
    app.run()
