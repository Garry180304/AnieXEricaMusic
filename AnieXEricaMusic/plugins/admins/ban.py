from pyrogram import filters, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    UserAdminInvalid,
    BadRequest
)
import sqlite3
import datetime
from AnieXEricaMusic import app

# Connect to SQLite database
conn = sqlite3.connect('ban_counts.db')
c = conn.cursor()

# Create table to store ban counts if not exists
c.execute('''CREATE TABLE IF NOT EXISTS ban_counts
             (admin_id INTEGER PRIMARY KEY, bans INTEGER)''')
conn.commit()

# Class to manage admin ban counts
class AdminManager:
    def __init__(self):
        self.ban_counts = {}

    def load_from_database(self):
        c.execute('SELECT * FROM ban_counts')
        rows = c.fetchall()
        for row in rows:
            self.ban_counts[row[0]] = row[1]

    def get_ban_count(self, admin_id):
        return self.ban_counts.get(admin_id, 0)

    def increment_ban_count(self, admin_id):
        self.ban_counts[admin_id] = self.get_ban_count(admin_id) + 1
        c.execute('REPLACE INTO ban_counts (admin_id, bans) VALUES (?, ?)', (admin_id, self.ban_counts[admin_id]))
        conn.commit()

# Initialize AdminManager instance
admin_manager = AdminManager()
admin_manager.load_from_database()

# Function to format user mention
def mention(user_id, name, mention=True):
    if mention:
        if name:
            link = f"{name}"
        else:
            username = message.from_user.username
            link = f"@{username}" if username else f"@{user_id}"
    else:
        link = f"{name if name else 'User'}"
    return link

# Function to get user ID from username
async def get_userid_from_username(username):
    try:
        user = await app.get_users(username)
    except:
        return None
    
    user_obj = [user.id, user.first_name]
    return user_obj

# Function to ban a user from the chat
async def ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason, time=None):
    msg_text = ""  # Initialize msg_text here

    try:
        await app.ban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        msg_text = "Sorry, I don't have permission to ban users. Please grant me ban rights."
        return msg_text, False
    except UserAdminInvalid:
        msg_text = "I can't ban administrators."
        return msg_text, False
    except Exception as e:
        msg_text = f"Oops! An error occurred: {e}"
        return msg_text, False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)

    msg_text += f"{user_mention} was banned by {admin_mention}\n"
    admin_manager.increment_ban_count(admin_id)  # Increment ban count for admin
    
    if reason:
        msg_text += f"Reason: `{reason}`\n"
    if time:
        msg_text += f"Time: `{time}`\n"

    return msg_text, True

# Function to unban a user from the chat
async def unban_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.unban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "Sorry, I don't have permission to unban users. Please grant me unban rights."
    except Exception as e:
        return f"Oops! An error occurred: {e}"

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    
    msg_text = f"{user_mention} was unbanned by {admin_mention}"
    return msg_text

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    
    msg_text = f"{user_mention} was unbanned by {admin_mention}"
    return msg_text



async def mute_user(user_id, first_name, admin_id, admin_name, chat_id, reason, time=None):
    try:
        msg_text = ""  # Initialize msg_text here

        if time:
            mute_end_time = datetime.datetime.now() + time
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions(), mute_end_time)
        else:
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
    except ChatAdminRequired:
        msg_text = "Mute rights? Nah, I'm just here for the digital high-fives 🙌\nGive me mute rights! 😡🥺"
        return msg_text, False
    except UserAdminInvalid:
        msg_text = "I wont mute an admin bruh!!"
        return msg_text, False
    except Exception as e:
        if user_id == 6664582540:
                msg_text = "why should i mute myself? sorry but I'm not stupid like you"
                return msg_text, False
        
        msg_text = f"opps!!\n{e}"
        return msg_text, False

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)

    msg_text += f"{user_mention} was muted by {admin_mention}\n"
    
    if reason:
        msg_text += f"Reason: `{reason}`\n"
    if time:
        msg_text += f"Time: `{time}`\n"

    return msg_text, True


async def unmute_user(user_id, first_name, admin_id, admin_name, chat_id):
    try:
        await app.restrict_chat_member(
            chat_id,
            user_id,
            ChatPermissions(
                can_send_media_messages=True,
                can_send_messages=True,
                can_send_other_messages=True,
                can_send_polls=True,
                can_add_web_page_previews=True,
                can_invite_users=True
            )
        )
    except ChatAdminRequired:
        msg_text = "Mute rights? Nah, I'm just here for the digital high-fives 🙌\nGive me unmute rights! 😡🥺"
        return msg_text
    except Exception as e:
        msg_text = f"opps!!\n{e}"
        return msg_text

    user_mention = mention(user_id, first_name)
    admin_mention = mention(admin_id, admin_name)
    
    msg_text = f"{user_mention} was unmuted by {admin_mention}"
    return msg_text


@app.on_message(filters.command(["ban"]))
async def ban_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status == enums.ChatMemberStatus.ADMINISTRATOR or member.status == enums.ChatMemberStatus.OWNER:
        if member.privileges.can_restrict_members:
            pass
        else:
            msg_text = "You dont have permission to ban someone"
            return await message.reply_text(msg_text)
    else:
        msg_text = "You dont have permission to ban someone"
        return await message.reply_text(msg_text)

    # Extract the user ID from the command or reply
    if len(message.command) > 1:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            first_name = message.reply_to_message.from_user.first_name
            reason = message.text.split(None, 1)[1]
        else:
            try:
                user_id = int(message.command[1])
                first_name = "User"
            except:
                user_obj = await get_userid_from_username(message.command[1])
                if user_obj == None:
                    return await message.reply_text("I can't find that user")
                user_id = user_obj[0]
                first_name = user_obj[1]

            try:
                reason = message.text.partition(message.command[1])[2]
            except:
                reason = None

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
        reason = None
    else:
        await message.reply_text("Please specify a valid user or reply to that user's message")
        return
        
    msg_text, result = await ban_user(user_id, first_name, admin_id, admin_name, chat_id, reason)
    if result == True:
        await message.reply_text(msg_text)
    if result == False:
        await message.reply_text(msg_text)


@app.on_message(filters.command(["unban"]))
async def unban_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status == enums.ChatMemberStatus.ADMINISTRATOR or member.status == enums.ChatMemberStatus.OWNER:
        if member.privileges.can_restrict_members:
            pass
        else:
            msg_text = "You dont have permission to unban someone"
            return await message.reply_text(msg_text)
    else:
        msg_text = "You dont have permission to unban someone"
        return await message.reply_text(msg_text)

    # Extract the user ID from the command or reply
    if len(message.command) > 1:
        try:
            user_id = int(message.command[1])
            first_name = "User"
        except:
            user_obj = await get_userid_from_username(message.command[1])
            if user_obj == None:
                    return await message.reply_text("I can't find that user")
            user_id = user_obj[0]
            first_name = user_obj[1]

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
    else:
        await message.reply_text("Please specify a valid user or reply to that user's message")
        return
        

@app.on_message(filters.command(["unmute"]))
async def unmute_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status == enums.ChatMemberStatus.ADMINISTRATOR or member.status == enums.ChatMemberStatus.OWNER:
        if member.privileges.can_restrict_members:
            pass
        else:
            msg_text = "You dont have permission to unmute someone"
            return await message.reply_text(msg_text)
    else:
        msg_text = "You dont have permission to unmute someone"
        return await message.reply_text(msg_text)

    # Extract the user ID from the command or reply
    if len(message.command) > 1:
        try:
            user_id = int(message.command[1])
            first_name = "User"
        except:
            user_obj = await get_userid_from_username(message.command[1])
            if user_obj == None:
                    return await message.reply_text("I can't find that user")
            user_id = user_obj[0]
            first_name = user_obj[1]

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
    else:
        await message.reply_text("Please specify a valid user or reply to that user's message")
        return
        
    msg_text = await unmute_user(user_id, first_name, admin_id, admin_name, chat_id)
    await message.reply_text(msg_text)

@app.on_message(filters.command(["banlist"]))
async def banlist_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    admin_name = message.from_user.first_name
    member = await chat.get_member(admin_id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await message.reply_text("You don't have permission to access the ban list.")

    try:
        banned_users = await app.get_chat_banned_members(chat_id)
    except BadRequest as e:
        return await message.reply_text(f"Failed to fetch ban list: {e}")

    if not banned_users:
        return await message.reply_text("There are no banned users in this chat.")

    msg_text = "List of banned users:\n\n"
    for user in banned_users:
        msg_text += f"- {user.user.first_name} ({user.user.id})\n"

    await message.reply_text(msg_text)
