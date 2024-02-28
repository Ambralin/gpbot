import os
import discord
from discord import option
from dotenv import load_dotenv
import cv2
import numpy as np
import aspose.words as aw
from PIL import Image
from datetime import datetime, timedelta
import re


doc = aw.Document()
builder = aw.DocumentBuilder(doc)

load_dotenv()
DSTOKEN = os.getenv('DISCORD_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())
with open(r'C:\Users\dzelm\Desktop\bots\gpbot\gyrys.txt', 'r') as file:
    date = file.readline().strip()
    gyryscount = int(file.readline().strip())
gyrysmax = 50

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="NOT GANGPLANK, it's (G)eneral (P)urpose BOT"))

@bot.slash_command(name='list_members', help='List all members in the guild')
async def list_members(ctx):
    members = ctx.guild.members
    member_list = '\n'.join([member.name for member in members])

    await ctx.send(f'Members in the guild:\n{member_list}')

@bot.slash_command(name='avatar', help='Show the avatar of a user')
async def avatar(ctx: discord.ApplicationContext, member: discord.Member = None):
    await ctx.defer()
    member = member or ctx.author

    avatar_url = member.display_avatar

    embed = discord.Embed(title=f"Avatar link", url=avatar_url)
    embed.set_author(name=member.display_name, icon_url=avatar_url)
    embed.set_footer(text=("Requested by " + ctx.author.display_name), icon_url=ctx.author.display_avatar)
    embed.set_image(url=avatar_url)

    await ctx.respond(embed=embed)

@bot.event
async def on_message(message):
    #global gyryscount, gyrysmax
    if message.author.id == 0:#558177130157178881:
        if bool(re.search(r'http[s]?://\S+|www\.\S+', message.content)):
            return
        with open(r'C:\Users\dzelm\Desktop\bots\gpbot\gyrys.txt', 'r') as file:
            last_saved_date_str = file.readline().strip()
            last_saved_date = datetime.strptime(last_saved_date_str, '%Y-%m-%d')
            gyryscount = int(file.readline().strip())
        if datetime.now().date() > last_saved_date.date():
            with open(r'C:\Users\dzelm\Desktop\bots\gpbot\gyrys.txt', 'w') as file:
                file.write(datetime.now().strftime('%Y-%m-%d') + '\n')
                file.write(str(0))

        gyryscount += len(message.content)
        if gyryscount >= gyrysmax:
            current_time = datetime.now()

            end_of_day = datetime(current_time.year, current_time.month, current_time.day) + timedelta(days=1)

            delta = end_of_day - current_time
            await message.author.timeout(until=datetime.utcnow() + delta)
            await message.channel.send("<@" + str(message.author.id) + "> dostal timeout do konce dne protože napsal o " + str(gyryscount - gyrysmax) + " více charakterů než povoleno")
            with open(r'C:\Users\dzelm\Desktop\bots\gpbot\gyrys.txt', 'w') as file:
                file.write(datetime.now().strftime('%Y-%m-%d') + '\n')
                file.write(str(gyryscount))
        else:
            await message.channel.send("<@" + str(message.author.id) + "> zbývá " + str(gyrysmax - gyryscount) + " charakterů do konce dne")
            with open(r'C:\Users\dzelm\Desktop\bots\gpbot\gyrys.txt', 'w') as file:
                file.write(datetime.now().strftime('%Y-%m-%d') + '\n')
                file.write(str(gyryscount))

    if message.type == discord.MessageType.reply:
        reply = await message.channel.fetch_message(message.reference.message_id)
        imagearr = []
        print(message.author, reply.content)
        if "resize" in message.content:
            attr = message.content.split(" ")
            if len(attr) < 3:
                return        
            if (reply.content.endswith(".gif") or ("https://tenor.com/view/" in reply.content) or ( len(reply.attachments) == 1 and reply.attachments[0].content_type.endswith("gif"))):
                print("started")
                if reply.content.endswith(".gif"):
                    source = cv2.VideoCapture(reply.content)
                elif ("https://tenor.com/view/" in reply.content):
                    source = cv2.VideoCapture(reply.content + ".gif")
                elif len(reply.attachments) == 1 and reply.attachments[0].content_type.endswith("gif"):
                    source = cv2.VideoCapture(reply.attachments[0].url)
                
                ret, img = source.read()
                fw, fh = img.shape[1], img.shape[0]
                w, h = resizefunc(attr[1], attr[2], fw, fh)
                while True:
                    ret, frame = source.read()
                    if np.shape(frame) == ():
                        break
                    frame = cv2.resize(frame, (w, h))
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                    imagearr.append(Image.fromarray(frame))

                print("saving")
                imagearr[0].save(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif", format='GIF', save_all=True, append_images=imagearr[1:], loop=0, disposal=2, transparency=1)

                print("saved")
                bubblef = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif")
                try:
                    await message.channel.send(file=bubblef)
                except:
                    fat = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\fat.webp")
                    await message.channel.send("ERROR THE RESULT FILE WAS TOO BIG", file=fat)
                print("sent")

            elif len(reply.attachments) == 1 and reply.attachments[0].content_type.startswith("image"):
                print("started")
                arr = np.asarray(bytearray(await reply.attachments[0].read()), dtype=np.uint8)
                img = cv2.imdecode(arr, -1) # 'Load it as it is'
                fw, fh = img.shape[1], img.shape[0]
                w, h = resizefunc(attr[1], attr[2], fw, fh)
                img = cv2.resize(img, (w, h))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

                img = Image.fromarray(img)

                print("saving")
                img.save(r"C:\Users\dzelm\Desktop\bots\gpbot\result.png", format='PNG')
                print("saved")
                bubblef = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\result.png")
                try:
                    await message.channel.send(file=bubblef)
                except:
                    fat = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\fat.webp")
                    await message.channel.send("ERROR THE RESULT FILE WAS TOO BIG", file=fat)
                print("sent")


        if message.content.lower() == "bubble":
            if (reply.content.endswith(".gif") or ("https://tenor.com/view/" in reply.content) or ( len(reply.attachments) == 1 and reply.attachments[0].content_type.endswith("gif"))):
                print("started")
                if reply.content.endswith(".gif"):
                    source = cv2.VideoCapture(reply.content)
                elif ("https://tenor.com/view/" in reply.content):
                    source = cv2.VideoCapture(reply.content + ".gif")
                elif len(reply.attachments) == 1 and reply.attachments[0].content_type.endswith("gif"):
                    source = cv2.VideoCapture(reply.attachments[0].url)
                
                mask = cv2.imread(r"C:\Users\dzelm\Desktop\bots\gpbot\bubble.png", cv2.COLOR_BGR2GRAY)
                while True:
                    ret, frame = source.read()
                    if np.shape(frame) == ():
                        break
                    frame = cv2.resize(frame, (500, 500))
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
                    frame = np.dstack((frame, mask))
                    imagearr.append(Image.fromarray(frame))

                print("saving")
                imagearr[0].save(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif", format='GIF', save_all=True, append_images=imagearr[1:], loop=0, disposal=2, transparency=1)

                print("saved")
                bubblef = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif")
                try:
                    await message.channel.send(file=bubblef)
                except:
                    fat = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\fat.webp")
                    await message.channel.send("ERROR THE RESULT FILE WAS TOO BIG", file=fat)
                print("sent")

            elif len(reply.attachments) == 1 and reply.attachments[0].content_type.startswith("image"):
                print("started")
                arr = np.asarray(bytearray(await reply.attachments[0].read()), dtype=np.uint8)
                mask = cv2.imread(r"C:\Users\dzelm\Desktop\bots\gpbot\bubble.png", cv2.COLOR_BGR2GRAY)
                img = cv2.imdecode(arr, -1) # 'Load it as it is'
                img = cv2.resize(img, (500, 500))
                if img.shape[2] == 4:
                    imga = img[:,:,3]
                    mask = cv2.multiply(imga, mask)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

                img = np.dstack((img, mask))

                img = Image.fromarray(img)

                print("saving")
                img.save(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif", format='GIF')
                print("saved")
                bubblef = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif")
                try:
                    await message.channel.send(file=bubblef)
                except:
                    fat = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\fat.webp")
                    await message.channel.send("ERROR THE RESULT FILE WAS TOO BIG", file=fat)
                print("sent")

        if message.content.lower() == "7days":
            if len(reply.attachments) == 1 and reply.attachments[0].content_type.startswith("image"):
                print("started")
                arr = np.asarray(bytearray(await reply.attachments[0].read()), dtype=np.uint8)
                img = cv2.imdecode(arr, -1) # 'Load it as it is'
                ogimg = cv2.resize(img, (10, 10))
                materials_image_path = r"C:\Users\dzelm\Desktop\code\7dayscoloring\materials2.png"
                material_size = (79, 79)

                # Generate material palette from the big image with specified gaps
                material_palette = generate_material_palette(materials_image_path, material_size, gap_before_first=3, gap_between_materials=3)

                # Convert the pixel art
                converted_image = convert_pixel_art(ogimg, material_palette)

                print("saving")
                converted_image.save(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif", format='GIF')
                print("saved")
                converted_image = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\result.gif")
                try:
                    await message.channel.send(file=bubblef)
                except:
                    fat = discord.File(r"C:\Users\dzelm\Desktop\bots\gpbot\fat.webp")
                    await message.channel.send("ERROR THE RESULT FILE WAS TOO BIG", file=fat)
                print("sent")

                
def get_average_color(img):
    # Calculate the average color of an image
    pixels = list(img.getdata())
    average_color = (
        sum(pixel[0] for pixel in pixels) // len(pixels),
        sum(pixel[1] for pixel in pixels) // len(pixels),
        sum(pixel[2] for pixel in pixels) // len(pixels)
    )
    return average_color

def color_difference(color1, color2):
    # Calculate the squared Euclidean distance between two colors
    return sum((a - b) ** 2 for a, b in zip(color1, color2))

def convert_pixel_art(img, material_palette):
    # Open the original image
    img = img
    
    # Get the size of individual material images
    material_width, material_height = material_palette[0].size

    # Create a new image with the same size and mode
    converted_img = Image.new("RGB", (img.width * material_width, img.height * material_height))

    # Iterate through each pixel
    for y in range(img.height):
        for x in range(img.width):
            # Get the original pixel color
            original_color = img.getpixel((x, y))

            # Find the closest material in the palette
            closest_material = min(material_palette, key=lambda material: color_difference(original_color, get_average_color(material)))

            # Paste the material onto the converted image
            converted_img.paste(closest_material, (x * material_width, y * material_height))

            # Print the current column
            print(f"Converted row {y + 1}, column {x + 1}")

        # Print the current row
        print(f"Converted row {y + 1}")

    # Print the completion message
    print("Conversion completed.")

    return converted_img

def generate_material_palette(materials_image_path, material_size, gap_before_first=3, gap_between_materials=3):
    # Open the big image containing all materials
    materials_image = Image.open(materials_image_path)

    # Get the size of individual material images
    material_width, material_height = material_size

    # Calculate the number of materials in each row and column
    num_materials_x = (materials_image.width + gap_before_first) // (material_width + gap_between_materials)
    num_materials_y = materials_image.height // (material_height + gap_between_materials)

    # Initialize an empty list to store individual material images
    material_palette = []

    # Extract each material image from the big image
    for y in range(num_materials_y):
        for x in range(num_materials_x):
            left = x * (material_width + gap_between_materials) + gap_before_first
            upper = y * (material_height + gap_between_materials)
            right = left + material_width
            lower = upper + material_height

            # Crop the material from the big image
            material = materials_image.crop((left, upper, right, lower))

            # Check if the material has transparency (alpha channel)
            if material.mode == 'RGBA' and 0 in material.getchannel('A').getdata():
                print(f"Skipping material with transparency: Row {y + 1}, Column {x + 1}")
                continue

            # Append the material to the palette
            material_palette.append(material)

            # Print the current row and column
            print(f"Processing row {y + 1}, column {x + 1}")

    return material_palette

def resizefunc(w, h, iw, ih):
    if "%" in w:
        w = iw*(int(w[:-1])/100)
    if "%" in h:
        h = ih*(int(h[:-1])/100)
    if h == "a":
        h = ih/(iw/int(w))
    if w == "a":
        w = iw/(ih/int(h))

    w, h = int(w), int(h)
    return w, h    


bot.run(DSTOKEN)