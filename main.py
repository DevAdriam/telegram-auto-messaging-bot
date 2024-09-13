import asyncio
import random
from datetime import datetime
from telethon import TelegramClient,functions,types
from telethon.tl.functions.messages import GetDialogsRequest,GetAllStickersRequest,GetSavedGifsRequest
from telethon.tl.types import InputPeerEmpty, Channel, Chat,DocumentAttributeSticker
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

api_id = 28765105
api_hash = '11bdcc4152817d40803108e5d94cd3fd'
phone_number = '+959986377869'

# ------- Message Type ----------
#  1. for message 
#  2. for sticker 
#  3. for gif 
#  4. for message and sticker 
#  5. for message and gif 

message_schedule_list = [
            {
                'group_id':585473540,  
                'message': "Sending schedule message test one",
                'sendTime': "2024-09-02 13:30",
                'message_type' : '1'
            },
            {
                'group_id':4528239513,  
                'message': "Sending schedule message test two",
                'sendTime': "2024-09-02 13:31",
                'message_type' : '2'
            },
             {
                'group_id':4528239513,  
                'message': "Sending schedule message test two",
                'sendTime': "2024-09-02 13:31",
                'message_type' : '3'
            },
        ]

async def send_message(client, group_id, message,message_or_sticker):
    try:
        print(f"Sending message to group {group_id}")
        # Ask the user whether to send a message, sticker, or both

        if message_or_sticker == '1':
            await client.send_message(group_id, message)

        elif message_or_sticker == '2':
            await send_random_sticker(client, group_id)

        elif message_or_sticker == '3':
            await send_random_gif(client, group_id)
           
        elif message_or_sticker == '4':
            await client.send_message(group_id, message)
            await send_random_sticker(client, group_id)
        
        elif message_or_sticker == '5':
            await client.send_message(group_id,message)
            await send_random_gif(client,group_id)

        else :
            print("Invalid input. Please enter '1', '2', '3', '4' or '5'")
            
        print("Sent successfully!")
    except Exception as e:
        print(f"Failed to send message to group {group_id}: {e}")

async def send_scheduled_messages(client, message_schedule):
    for item in message_schedule:
        group_id = item['group_id']
        message = item['message']
        send_time_str = item.get('sendTime')  # 'sendTime' is optional
        send_with_sticker = item.get('message_type')

        try:
            if send_time_str:
                # Convert the scheduled time string to a datetime object
                send_time = datetime.strptime(send_time_str, "%Y-%m-%d %H:%M") 
                # Calculate delay time until the scheduled time
                now = datetime.now()
                delay_seconds = (send_time - now).total_seconds()

                if delay_seconds > 0:
                    print(f"Message to group {group_id} scheduled in {delay_seconds:.2f} seconds.")
                    await asyncio.sleep(delay_seconds)
                else:
                    print(f"Scheduled time for group {group_id} has already passed, sending immediately.")
            else:
                print(f"No scheduling time provided for group {group_id}, sending immediately.")

            await send_message(client, group_id, message,send_with_sticker)

        except ValueError as ve:
            print(f"Invalid date format for group {group_id}: {ve}")

async def get_random_sticker(client):
    try:
        # Fetch all sticker sets
        stickers = await client(GetAllStickersRequest(0))
        all_stickers = []
        
        for sticker_set in stickers.sets:
            sticker_set_id = sticker_set.id
            sticker_set_access_hash =sticker_set.access_hash

            if not sticker_set_id or not sticker_set_access_hash:
                continue
            
            result = await client(functions.messages.GetStickerSetRequest(
            stickerset=types.InputStickerSetID(
            id=sticker_set_id,
            access_hash=sticker_set_access_hash
            ),
                 hash=0
            ))

            all_stickers.extend(result.documents)

        if all_stickers:
            random_sticker = random.choice(all_stickers)
            print(f"Selected Sticker ID: {random_sticker.id}")
            return random_sticker
        else:
            print("No stickers found.")
            return None

    except Exception as e:
        print(f"Failed to retrieve random sticker: {e}")
        return None

async def send_random_sticker(client, group_id):
    random_sticker = await get_random_sticker(client)

    if random_sticker:
        try:
            # Send the selected random sticker to the specified group
            await client.send_file(group_id, random_sticker)
            print("Random sticker sent successfully!")
        except Exception as e:
            print(f"Failed to send sticker: {e}")

async def get_random_gif(client):
    try:
        # Fetch all saved GIFs
        saved_gifs = await client(GetSavedGifsRequest(hash=0))
        all_gifs = saved_gifs.gifs

        # Filter out premium GIFs
        regular_gifs = [
            gif for gif in all_gifs
            if not any(isinstance(attr, DocumentAttributeSticker) and attr.stickerset.access_hash == 0
                       for attr in gif.attributes)
        ]

        if regular_gifs:
            # Choose a random GIF from non-premium GIFs
            random_gif = random.choice(regular_gifs)
            print(f"Selected GIF ID: {random_gif.id}")
            return random_gif
        else:
            print("No regular (non-premium) GIFs found.")
            return None

    except Exception as e:
        print(f"Failed to retrieve GIFs: {e}")
        return None

async def send_random_gif(client, group_id):
    random_gif = await get_random_gif(client)

    if random_gif:
        try:
            # Send the selected random GIF to the specified group
            await client.send_file(group_id, random_gif)
            print("Random GIF sent successfully!")
        except Exception as e:
            print(f"Failed to send GIF: {e}")

async def list_groups(client):
    dialogs = await client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=200,  # adjust your groups size
        hash=0
    ))
    groups = [d for d in dialogs.chats if isinstance(d, (Channel, Chat))]

    # Sort groups alphabetically by title
    groups.sort(key=lambda g: g.title.lower())

    for i, group in enumerate(groups):
        # Highlight group names with different colors
        color = Fore.YELLOW
        print(f"{i + 1}. {color}{group.title} {Style.RESET_ALL}(ID: {group.id})")
    return groups

async def send_messages_at_random_intervals(client, group_ids, message, intervals,message_type):
    count = 0
    while True:
        if count == len(group_ids) :
            count = 0
        
        # Pick a random interval from the provided list
        random_interval = random.choice(intervals)
        print(f"Next message will be sent after {random_interval} minutes.")
        
        # Convert minutes to seconds and wait for the random interval
        await asyncio.sleep(random_interval * 60)
        
        # Send the message
        group_id = group_ids[count]
        await send_message(client, group_id, message,message_type)
        count = count +1

async def main():
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

    send_type = input("Please Enter \n 'direct' to send a message immediately \n 'schedule' to schedule a message \n 'loop' to loop through and send a message \n: ").strip().lower()

    if send_type == 'direct':
        groups = await list_groups(client)

        # Get selected groups from user input
        selected_group_indices = input("Enter the numbers of the groups you want to send a message to (comma-separated): ")
        selected_group_ids = [groups[int(i) - 1].id for i in selected_group_indices.split(",")]

        message_type_direct = input(" 1. for message \n 2. for sticker \n 3. for gif \n 4. for message and sticker \n 5. for message and gif \n :")
        # Get direct message from user input
        message = ""

        if message_type_direct == '1' or message_type_direct == '4' or message_type_direct == '5' : 
            message = input("Enter the message: ")
        
        # Send the message to each selected group
        for group_id in selected_group_ids:
            await send_message(client, group_id, message,message_type_direct)
            
    elif send_type == 'schedule':
        # Example of message schedule list
        message_schedule = message_schedule_list
        await send_scheduled_messages(client, message_schedule)
    
    elif send_type == 'loop':
        groups = await list_groups(client)

        # Get selected group from user input (only one group for simplicity)
        selected_groups_index = input("Enter the number of the group you want to send a message to: ")
        selected_group_ids = [groups[int(i) - 1].id for i in selected_groups_index.split(",")]
        
        message = ""
        print("Please choose your message type")
        message_type_loop = input(" 1. for message \n 2. for sticker \n 3. for gif \n 4. for message and sticker \n 5. for message and gif \n :")
        # Get direct message from user input
        if message_type_loop == '1' or message_type_loop == '4' or message_type_loop == '5' : 
            message = input("Enter the message: ")

        # Define a list of intervals (in minutes) you want to randomize from
        intervals = [0.1,0.2]  
        # intervals =[30,60]

        # Start sending messages at random intervals
        await send_messages_at_random_intervals(client, selected_group_ids, message, intervals,message_type_loop)

    else:
        print("Invalid option. Please enter 'direct' or 'schedule'.")

    # Disconnect the client
    await client.disconnect()

# Run the async main function
if __name__ == '__main__':
    asyncio.run(main())



