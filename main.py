import discord
import json
import emoji
import requests
import os

config = json.load(open('config.json', 'r'))

bot = discord.Client()

BOT_TOKEN = config.get("BOT_TOKEN")

EMOJI_NAME = ':eyes:'
REACTION_EMOJI = emoji.emojize(EMOJI_NAME)
IMAGES = f'{os.getcwd()}/Images'


@bot.event
async def on_ready():
    if not os.path.exists(IMAGES):
        os.makedirs(IMAGES)
    print('[+] We have logged in as {0.user}'.format(bot))
    print('[+] Bot is ready!')


@bot.event
async def on_raw_reaction_add(payload):
    WAIFU_API_KEY = config.get("WAIFU_API_KEY")
    if payload.user_id == bot.user.id:
        return
    if isinstance(payload.emoji, discord.PartialEmoji):
        if payload.emoji.name == REACTION_EMOJI:
            channel = discord.utils.get(
                bot.guilds[0].channels, id=payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, payload.member)
            image_url = message.attachments[0].url
            r = requests.post(
                "https://api.deepai.org/api/waifu2x",
                data={
                    'image': image_url,
                },
                headers={'api-key': WAIFU_API_KEY}
            )
            rr = requests.get(r.json()['output_url'])
            img = f'{IMAGES}/{payload.message_id}.png'
            image_on_disk = open(img, 'wb')
            image_on_disk.write(rr.content)
            image_on_disk.close()
            await channel.send('Waifu2x Enhanced version.', file=discord.File(open(img, 'rb')))
            os.remove(img)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if len(message.attachments) != 0:
        image_exts = ('png', 'PNG', 'jpg', 'JPG', 'JPEG', 'jpeg')
        for att in message.attachments:
            if att.filename.endswith(image_exts):
                await message.add_reaction(REACTION_EMOJI)

bot.run(BOT_TOKEN)
