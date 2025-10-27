import discord
from discord.ext import commands
from discord.ui import View, Select
from flask import Flask
from threading import Thread
import logging
from dotenv import load_dotenv
import os

# ====== SETUP FLASK KEEP ALIVE ======
app = Flask('')

@app.route('/')
def home():
    return "✅ Discord bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ====== DISCORD BOT SETUP ======
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== ROLE NAMES SESUAI SERVER =====
ROLE_MEMBER = "꧁⎝ 𓆩༺𝙈𝙚𝙢𝙗𝙚𝙧༻𓆪 ⎠꧂"
GENDER_ROLES = ["♂️ Boys", "♀️ Girls"]
DEVICE_ROLES = ["📱 Mobile", "💻 PC"]
GAME_ROLES = ["🎭 Roblox", "⚜️ Honor of Kings", "🔫 Blood Strike", "⚔️ Mobile Legends"]

# ===== EVENT =====
@bot.event
async def on_ready():
    print(f"✅ Bot aktif sebagai {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Selamat datang di server, {member.name}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention}, jangan gunakan kata itu!")
    await bot.process_commands(message)

# ===== COMMAND DASAR =====
@bot.command()
async def hello(ctx):
    await ctx.send(f"Halo {ctx.author.mention}!")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="📊 Polling Baru", description=question, color=0x00ffcc)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
@commands.has_role(ROLE_MEMBER)
async def secret(ctx):
    await ctx.send("Selamat datang di Realm rahasia!")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Kamu tidak punya izin untuk melakukan itu!")

# ===== SISTEM ROLE BERTAHAP =====
@bot.command()
async def startrole(ctx):
    """Mulai sistem role bertahap"""
    member_role = discord.utils.get(ctx.guild.roles, name=ROLE_MEMBER)
    if not member_role:
        await ctx.send("❌ Role Member belum ditemukan di server.")
        return

    await ctx.author.add_roles(member_role)
    await ctx.send(f"✅ Kamu sudah mendapat role {ROLE_MEMBER}.")

    embed = discord.Embed(
        title="Langkah 1️⃣: Pilih Jenis Kelamin",
        description="Pilih salah satu jenis kelamin kamu.",
        color=0x3498db,
    )
    await ctx.send(embed=embed, view=GenderView(ctx.author))

# ===== GENDER =====
class GenderView(View):
    def __init__(self, user):
        super().__init__(timeout=120)
        self.user = user
        self.add_item(GenderSelect())

class GenderSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="♂️ Boys", emoji="👦"),
            discord.SelectOption(label="♀️ Girls", emoji="👧"),
        ]
        super().__init__(
            placeholder="Pilih gender kamu",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role_name = self.values[0]
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            await user.add_roles(role)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Langkah 2️⃣: Pilih Device",
                description="Kamu bisa pilih satu atau lebih device yang kamu gunakan.",
                color=0x2ecc71,
            ),
            view=DeviceView(user)
        )

# ===== DEVICE =====
class DeviceView(View):
    def __init__(self, user):
        super().__init__(timeout=120)
        self.user = user
        self.add_item(DeviceSelect())

class DeviceSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="📱 Mobile", emoji="📱"),
            discord.SelectOption(label="💻 PC", emoji="💻"),
        ]
        super().__init__(
            placeholder="Pilih device kamu",
            options=options,
            min_values=1,
            max_values=len(options)
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        added_roles = []
        for val in self.values:
            role = discord.utils.get(interaction.guild.roles, name=val)
            if role:
                await user.add_roles(role)
                added_roles.append(val)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Langkah 3️⃣: Pilih Game Favorit",
                description="Kamu bisa pilih semua game yang kamu mainkan.",
                color=0xf1c40f,
            ),
            view=GameView(user)
        )

# ===== GAME =====
class GameView(View):
    def __init__(self, user):
        super().__init__(timeout=120)
        self.user = user
        self.add_item(GameSelect())

class GameSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🎭 Roblox", emoji="🎭"),
            discord.SelectOption(label="⚜️ Honor of Kings", emoji="⚜️"),
            discord.SelectOption(label="🔫 Blood Strike", emoji="🔫"),
            discord.SelectOption(label="⚔️ Mobile Legends", emoji="⚔️"),
        ]
        super().__init__(
            placeholder="Pilih game favoritmu",
            options=options,
            min_values=1,
            max_values=len(options)
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        added_roles = []
        for val in self.values:
            role = discord.utils.get(interaction.guild.roles, name=val)
            if role:
                await user.add_roles(role)
                added_roles.append(val)

        log_channel = discord.utils.get(interaction.guild.text_channels, name="role-log")
        if log_channel:
            await log_channel.send(
                f"📝 **{user.name}** telah memilih:\n"
                f"• Gender: {', '.join([r for r in GENDER_ROLES if discord.utils.get(interaction.guild.roles, name=r) in user.roles])}\n"
                f"• Device: {', '.join([r for r in DEVICE_ROLES if discord.utils.get(interaction.guild.roles, name=r) in user.roles])}\n"
                f"• Game: {', '.join(added_roles)}"
            )

        embed = discord.Embed(
            title="🎉 Selesai!",
            description=f"Role yang kamu dapatkan:\n"
                        f"✅ Member\n"
                        f"✅ Gender\n"
                        f"✅ Device\n"
                        f"✅ Game: {', '.join(added_roles)}",
            color=0x9b59b6,
        )
        await interaction.response.edit_message(embed=embed, view=None)

# ===== JALANKAN BOT =====
keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
