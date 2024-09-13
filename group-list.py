from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Channel, Chat
from colorama import Fore, Style, init
from telethon import TelegramClient
import asyncio

api_id = 28765105
api_hash = '11bdcc4152817d40803108e5d94cd3fd'
phone_number = '+959793473780'
async def list_groups():

     # Initialize the client
    client = TelegramClient('session_name', api_id, api_hash)

    # Connecting to client (retry attempt - 5)
    retries = 5
    delay = 1  # Initial delay in seconds
    for attempt in range(retries):
        try:
            await client.connect()
            break
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff

     # If not authorized (not found in session-file), send code and log in first
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = input('Enter the code you received: ')
        try:
            await client.sign_in(phone_number, code)
        except Exception as e:
            # If a password is required, this exception will be raised
            if 'Two-steps verification' in str(e) or 'password is required' in str(e):
                password = input('Two-step verification is enabled. Enter your password: ')
                try:
                    await client.sign_in(password=password)
                except Exception as password_error:
                    print(f"Failed to log in with password: {password_error}")
                    return
            else:
                print(f"Failed to log in: {e}")
                return

    print("Logged in successfully!")

    dialogs = await client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=200,
        hash=0
    ))
    groups = [d for d in dialogs.chats if isinstance(d, (Channel, Chat))]

    # Sort groups alphabetically by title
    groups.sort(key=lambda g: g.title.lower())

    for i, group in enumerate(groups):
        # Highlight group names with different colors
        color = Fore.GREEN
        print(f"{i + 1}. {color}{group.title} {Style.RESET_ALL}(ID: {group.id})")
    return groups


asyncio.run(list_groups())