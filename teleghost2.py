from telethon import TelegramClient, events, Button
from pymongo import MongoClient
from bson import ObjectId
import asyncio
import math
import certifi
import urllib

# Bot API credentials
API_ID = '23948999'
API_HASH = '76b1080f07e14bb3f51ba84ff2474319'
BOT_TOKEN = '7721773520:AAEsP9I2DFvR0LIaY6b-GB-Y3BQlTWM2rvQ'

username = 'Kingewor9'
password = 'Padlock2122@'

# Encode username and password
encoded_username = urllib.parse.quote_plus(username)
encoded_password = urllib.parse.quote_plus(password)

# Correctly formatted URI
uri = f"mongodb+srv://{encoded_username}:{encoded_password}@teleghost1.pibh7bm.mongodb.net/?retryWrites=true&w=majority"


# MongoDB Connection
mongo_client = MongoClient(uri, tlsCAFile=certifi.where())
db = mongo_client['telegram_bot']
categories_collection = db["categories"]

categories = [
    {"name": "Marketing"},
    {"name": "Crypto"},
    {"name": "Forex"},
    {"name": "Theme Pages"},
    {"name": "Sports"},
    {"name": "Travel"},
    {"name": "Science & Art"},
    {"name": "Pet & Animals"},
    {"name": "Self Development"},
    {"name": "Movies"},
    {"name": "Gospel"},
    {"name": "Games"},
    {"name": "Health"},
    {"name": "Music & Artists"},
    {"name": "Cars & Automobiles"},
    {"name": "Tech & Gadgets"},
    {"name": "Fitness"},
    {"name": "Book & Reviews"},
    {"name": "Food & Cooking"},
    {"name": "Business & Startup"},
    {"name": "Celebrities"},
    {"name": "Memes"},
    {"name": "Relationship"},
    {"name": "Parenting & Family"},
    {"name": "History"},
    {"name": "Foreign Languages"},
    {"name": "Men Fashion"},
    {"name": "Women Fashion"},
    {"name": "News & Blog"},
    {"name": "Adults"}
]

# Insert categories into MongoDB (if not already added)
category_ids = {}
for category in categories:
    existing_category = categories_collection.find_one({"name": category["name"]})
   
    if not existing_category:
        inserted = categories_collection.insert_one(category)
        category_ids[category["name"]] = inserted.inserted_id
    else:
        category_ids[category["name"]] = existing_category["_id"]
    

print("Categories inserted successfully!") 


category_name = "Marketing"  # Change this dynamically based on user input
category = categories_collection.find_one({"name": "Marketing"})
if category:
    print(f"Category: {category['name']}, Category ID: {category['_id']}")
else:
    print("Category not found!")

    
category_messages_collection = db['category_messages']
category_messages = [
   {
        "categories": "Marketing_category",
        "message": """Here are some top marketing channels you can explore:
        
1. [Academy of Closing](https://t.me/teleghost_ads/5/48)
2. [Tiktok Leads Generation](https://t.me/teleghost_ads/5/49)
3. [Digital Nomad Academy](https://t.me/teleghost_ads/5/50)
4. [Faithman | Sales & Marketing](https://t.me/teleghost_ads/5/52)
5. [Digital Cash Printing Formular](https://t.me/teleghost_ads/32/51)

Tap any name above to visit the Telegram group or channel."""
    },
   { "categories": "Theme Pages_category",
        "message": """Here are some top theme pages channels you can explore:
        
1. [Quotation](https://t.me/teleghost_ads/45/46)
2. [Aesthetic Vibes](https://t.me/teleghost_ads/45/53)
3. [Love is Life](https://t.me/teleghost_ads/45/54)
4. [English Quotes](https://t.me/teleghost_ads/45/55)
5. [Random Facts](https://t.me/teleghost_ads/45/56)

Tap any name above to visit the Telegram group or channel."""
}
]

category_messages_collection.insert_many(category_messages)

print("Category messages inserted successfully!")


bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Commands
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Welcome! Use /advertise to view ad channels, /earn to add your channel, /tutorial for guidance, /announcement for updates, or /support for help.")

# Advertise command shows categories
@bot.on(events.NewMessage(pattern='/advertise'))
async def advertise(event, page=0):
    categories = list(categories_collection.find())
    total_pages = math.ceil(len(categories) / 5)

    buttons = [
        [Button.inline(category['name'], f'cat_{category["_id"]}')]
        for category in categories[page*5:(page+1)*5]
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(Button.inline("⬅️ Previous", f'adv_page_{page-1}'))
    if page < total_pages - 1:
        nav_buttons.append(Button.inline("Next ➡️", f'adv_page_{page+1}'))

    if nav_buttons:
        buttons.append(nav_buttons)

    await event.respond("Select a category:", buttons=buttons)

# Pagination
@bot.on(events.CallbackQuery(pattern=r'adv_page_(\d+)'))
async def paginate_categories(event):
    page = int(event.pattern_match.group(1))
    await advertise(event, page)
    
   # Handle category selection and display message from category_messages collection
@bot.on(events.CallbackQuery(pattern=r'cat_(.*)'))
async def category_selected(event):
    category_id_raw = event.pattern_match.group(1)

    # Ensure it's a string and not bytes
    if isinstance(category_id_raw, bytes):
        category_id_raw = category_id_raw.decode('utf-8')

    try:
        category = categories_collection.find_one({"_id": ObjectId(category_id_raw)})
    except Exception as e:
        print(f"DEBUG: Invalid category ID: {e}")
        await event.answer("Invalid category ID.", alert=True)
        return

    if category:
        category_messages_collection = db["category_messages"]
        message_doc = category_messages_collection.find_one({"categories": f"{category['name']}_category"})

        if message_doc and "message" in message_doc:
            await event.edit(message_doc["message"], link_preview=False)
        else:
            await event.edit("No message found for this category.")
    else:
        await event.edit("Category not found.")


@bot.on(events.NewMessage(pattern='/earn'))
async def earn(event):
    await event.respond("Want to earn? Submit your channel for paid promotions here: https://forms.gle/Hgj1jvehxc8R7U4E6")

@bot.on(events.NewMessage(pattern='/tutorial'))
async def tutorial(event):
    await event.respond("Watch this tutorial to understand how to use the bot: https://youtu.be/cREkAk6I10w?si=WoCDFePTtoaxxF6E")

@bot.on(events.NewMessage(pattern='/announcement'))
async def announcement(event):
    await event.respond("Join this channel to stay updated with important announcement: https://t.me/Tele_Ghost")

@bot.on(events.NewMessage(pattern='/support'))
async def support(event):
    await event.respond("Need help? Contact: @mike4ads")

print("Bot is running...")
bot.run_until_disconnected()
