import discord
from discord.ext import commands
import random
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

users_xp = {}
user_balances = {}

# Küfürler ve her birine özel ayrı uyarı mesajları sözlüğü
BAD_WORD_RESPONSES = {
    "küfür1": "Hey {author}, bu sunucuda bu tarz argo/küfür kelimeler kullanmak kesinlikle yasaktır!",
    "küfür2": "Lütfen kelimelerine dikkat et {author}, burada bu tür ifadelere tolerans gösterilmiyor.",
    "amk": "Ağzını bozma {author}! Bu sunucuda bu tarz küfürler etmek yasak.",
    "aq": "Bu sunucuda argo ve küfür kullanımı yasaktır dostum, dikkatli ol {author}.",
    "orospu": "Hey {author}! Bu tarz ağır hakaretler ve küfürler ban sebebidir, bir daha olmasın.",
    "oç": "Sunucumuzda bu tür küfürlerin kullanılmasına izin vermiyoruz {author}.",
    "sik": "Daha nezaketli bir dil kullanmalısın {author}, bu kelime burada yasak.",
    "anan": "Ailevi değerlere yönelik küfürler kesinlikle yasaktır {author}!",
    "piç": "Bu tarz argo ve hakaret içeren sözler sarf etmek yasaktır {author}.",
    "discord.gg": "İzinsiz sunucu davet linki veya reklam paylaşmak yasaktır {author}!",
    "http://": "Bu sunucuda izinsiz link paylaşımı yapmak yasaktır {author}!",
    "https://": "Bu sunucuda izinsiz link paylaşımı yapmak yasaktır {author}!"
}

@bot.event
async def on_ready():
    print(f"{bot.user.name} aktif, genişletilmiş küfür koruma sistemiyle devrede!")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash komut senkronize edildi.")
    except Exception as e:
        print(e)
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # "arda kim" yazıldığında vereceği yanıt
    if "arda kim" in message.content.lower():
        await message.channel.send("Salak bi obez")
        return

    content_lower = message.content.lower()
    
    # Küfür koruması
    for word, response_template in BAD_WORD_RESPONSES.items():
        if word in content_lower:
            try:
                await message.delete()
                custom_message = response_template.format(author=message.author.mention)
                await message.channel.send(custom_message, delete_after=6)
            except:
                pass
            return

    # XP Sistemi
    author_id = message.author.id
    if author_id not in users_xp:
        users_xp[author_id] = {"xp": 0, "level": 1}
    
    users_xp[author_id]["xp"] += random.randint(5, 15)
    if users_xp[author_id]["xp"] >= users_xp[author_id]["level"] * 100:
        users_xp[author_id]["level"] += 1
        users_xp[author_id]["xp"] = 0
        await message.channel.send(f"Tebrikler {message.author.mention}! **Seviye {users_xp[author_id]['level']}** oldun! 🎉")

    await bot.process_commands(message)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    
    # Küfür ve yasaklı kelime kontrolü (Her kelimeye özel ayrı yanıt)
    for word, response_template in BAD_WORD_RESPONSES.items():
        if word in content_lower:
            try:
                await message.delete()
                custom_message = response_template.format(author=message.author.mention)
                await message.channel.send(custom_message, delete_after=6)
                break
            except:
                pass
            return

    # XP Sistemi
    author_id = message.author.id
    if author_id not in users_xp:
        users_xp[author_id] = {"xp": 0, "level": 1}
    
    users_xp[author_id]["xp"] += random.randint(5, 15)
    if users_xp[author_id]["xp"] >= users_xp[author_id]["level"] * 100:
        users_xp[author_id]["level"] += 1
        users_xp[author_id]["xp"] = 0
        await message.channel.send(f"Tebrikler {message.author.mention}! **Seviye {users_xp[author_id]['level']}** oldun! 🎉")

    await bot.process_commands(message)

# --- 1. TEMEL SİSTEMLER & YARDIM ---
@bot.tree.command(name="help", description="Botun tüm komut listesini gösterir.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 x77 BOT - Eksiksiz Komut Listesi", color=discord.Color.dark_theme())
    embed.add_field(name="🤖 Temel Sistemler", value="`/help`, `/ping`, `/userinfo`, `/serverinfo`, `/avatar`, `/botinfo`", inline=False)
    embed.add_field(name="🛡️ Moderasyon", value="`/ban`, `/kick`, `/mute`, `/unmute`, `/warn`, `/warnings`, `/clear`, `/lock`, `/unlock`", inline=False)
    embed.add_field(name="🔊 Ses İşlemleri", value="`/ses-olustur`, `/play`, `/stop`", inline=False)
    embed.add_field(name="🎮 Eğlence & Ekonomi", value="`/8ball`, `/yazitura`, `/dice`, `/ship`, `/rank`, `/gunluk`, `/bakiye`", inline=False)
    embed.add_field(name="🏆 x77 Arena", value="`/arena-kayit`, `/mac-gir`", inline=False)
    embed.set_footer(text="x77 Bot - Güvenlik ve E-Spor Altyapısı")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Botun gecikme süresini gösterir.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! 🏓 {latency}ms")

@bot.tree.command(name="userinfo", description="Kullanıcı bilgilerini gösterir.")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"👤 Kullanıcı Bilgisi: {member.name}", color=member.color)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Katılım Tarihi", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Sunucu bilgileri.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"🏡 {guild.name} Sunucu Bilgileri", color=discord.Color.blue())
    embed.add_field(name="Üye Sayısı", value=guild.member_count, inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Avatarını gösterir.")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"🖼️ {member.name} - Avatar", color=discord.Color.purple())
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="botinfo", description="Bot hakkında.")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 x77 Bot Bilgi", description="Railway üzerinde aktif ve kararlı çalışmaktadır.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)


# --- 2. MODERASYON SİSTEMLERİ ---
@bot.tree.command(name="ban", description="Kullanıcıyı banlar.")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, *, sebep: str = "Belirtilmemiş"):
    await member.ban(reason=sebep)
    await interaction.response.send_message(f"🔨 {member.mention} banlandı! Sebep: {sebep}")

@bot.tree.command(name="kick", description="Kullanıcıyı atar.")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, *, sebep: str = "Belirtilmemiş"):
    await member.kick(reason=sebep)
    await interaction.response.send_message(f"👢 {member.mention} atıldı! Sebep: {sebep}")

@bot.tree.command(name="clear", description="Mesaj siler.")
@commands.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, miktar: int):
    await interaction.channel.purge(limit=miktar)
    await interaction.response.send_message(f"🧹 {miktar} adet mesaj silindi!", ephemeral=True)

@bot.tree.command(name="lock", description="Kanalı kilitler.")
@commands.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Kanal kilitlendi.")

@bot.tree.command(name="unlock", description="Kanal kilidini açar.")
@commands.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Kanal kilidi açıldı.")

@bot.tree.command(name="mute", description="Susturur.")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, dakika: int):
    from datetime import timedelta
    await member.timeout(timedelta(minutes=dakika))
    await interaction.response.send_message(f"🔇 {member.mention} {dakika} dakika susturuldu.")

@bot.tree.command(name="unmute", description="Susturmayı kaldırır.")
@commands.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f"🔊 {member.mention} susturması kaldırıldı.")

@bot.tree.command(name="warn", description="Uyarır.")
@commands.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, *, sebep: str):
    await interaction.response.send_message(f"⚠️ {member.mention} uyarısı alındı! Sebep: {sebep}")


# --- 3. SES KANALI OLUŞTURMA & MÜZİK ---
@bot.tree.command(name="ses-olustur", description="Sunucuda yeni bir ses kanalı oluşturur.")
@commands.has_permissions(manage_channels=True)
async def ses_olustur(interaction: discord.Interaction, kanal_adi: str):
    guild = interaction.guild
    new_channel = await guild.create_voice_channel(name=kanal_adi)
    await interaction.response.send_message(f"🔊 Başarıyla **{kanal_adi}** adında yeni bir ses kanalı oluşturuldu! (ID: `{new_channel.id}`)")

@bot.tree.command(name="play", description="Mevcut ses kanalına katılır.")
async def play(interaction: discord.Interaction, sarkiasadi: str = "Ses kanalına giriş yapıldı"):
    if not interaction.user.voice:
        await interaction.response.send_message("Önce bir ses kanalına girmelisin kanka!", ephemeral=True)
        return
    
    voice_channel = interaction.user.voice.channel
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.move_to(voice_channel)
    else:
        await voice_channel.connect()
        
    await interaction.response.send_message(f"🎵 Ses kanalına bağlandım! İstek: **{sarkiasadi}**")

@bot.tree.command(name="stop", description="Ses kanalından ayrılır.")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Ses kanalından ayrıldım.")
    else:
        await interaction.response.send_message("Zaten bir ses kanalında değilim!", ephemeral=True)


# --- 4. EĞLENCE & EKONOMİ ---
@bot.tree.command(name="8ball", description="Sihirli 8ball.")
async def eightball(interaction: discord.Interaction, soru: str):
    cevaplar = ["Kesinlikle öyle", "Büyük ihtimalle", "Kesinlikle hayır", "Bunu söylemesem daha iyi", "Tekrar sor"]
    await interaction.response.send_message(f"❓ Soru: {soru}\n🔮 Cevap: {random.choice(cevaplar)}")

@bot.tree.command(name="dice", description="Zar atar.")
async def dice(interaction: discord.Interaction):
    await interaction.response.send_message(f"🎲 Attığın zar: **{random.randint(1, 6)}**")

@bot.tree.command(name="ship", description="Uyum ölçer.")
async def ship(interaction: discord.Interaction, karsi_kullanici: discord.Member):
    yuzde = random.randint(0, 100)
    await interaction.response.send_message(f"💖 {interaction.user.mention} ile {karsi_kullanici.mention} uyumu: **%{yuzde}**")

@bot.tree.command(name="bakiye", description="Cüzdanı gösterir.")
async def bakiye(interaction: discord.Interaction):
    bal = user_balances.get(interaction.user.id, 100)
    await interaction.response.send_message(f"Cüzdanında **{bal} Coin** var 🪙")

@bot.tree.command(name="gunluk", description="Günlük ödül.")
async def gunluk(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_balances[user_id] = user_balances.get(user_id, 100) + 100
    await interaction.response.send_message("Günlük **100 Coin** eklendi! 💰")

@bot.tree.command(name="yazitura", description="Yazı tura bahsi.")
async def yazitura(interaction: discord.Interaction, secim: str, miktar: int):
    secim = secim.lower()
    if secim not in ["yazı", "tura"]:
        await interaction.response.send_message("Seçim 'yazı' veya 'tura' olmalı!", ephemeral=True)
        return
    user_id = interaction.user.id
    bal = user_balances.get(user_id, 100)
    if bal < miktar or miktar <= 0:
        await interaction.response.send_message("Yetersiz bakiye!", ephemeral=True)
        return
    sonuc = random.choice(["yazı", "tura"])
    if secim == sonuc:
        user_balances[user_id] = bal + miktar
        await interaction.response.send_message(f"Para **{sonuc.upper()}** geldi! Kazandın 🎉 +{miktar} Coin")
    else:
        user_balances[user_id] = bal - miktar
        await interaction.response.send_message(f"Para **{sonuc.upper()}** geldi, kaybettin 😢 -{miktar} Coin")

@bot.tree.command(name="rank", description="Seviye durumun.")
async def rank(interaction: discord.Interaction):
    data = users_xp.get(interaction.user.id, {"xp": 0, "level": 1})
    await interaction.response.send_message(f"📊 Seviye: {data['level']} | XP: {data['xp']}")


# --- 5. x77 ARENA ---
@bot.tree.command(name="arena-kayit", description="Takım kaydı.")
async def arena_kayit(interaction: discord.Interaction, takim_adi: str):
    await interaction.response.send_message(f"🏆 **{takim_adi}** takımı e-spor arena turnuvasına kaydedildi! ⚔️")

@bot.tree.command(name="mac-gir", description="Maç arama.")
async def mac_gir(interaction: discord.Interaction):
    await interaction.response.send_message("⚔️ Maç odaları hazırlanıyor...")

bot.run(os.getenv("DISCORD_TOKEN"))
