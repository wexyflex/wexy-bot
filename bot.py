import discord
from discord.ext import commands
import google.generativeai as genai
import os
import asyncio
import yt_dlp

# Botun niyetleri (intents) ayarlıyoruz
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Gemini API yapılandırması
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# yt-dlp ve ses ayarları
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url if url.startswith("http") else f"ytsearch:{url}", download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'{bot.user.name} aktif! x77 Arena ve Tüm Sistemler Devrede.')
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash komut senkronize edildi.")
    except Exception as e:
        print(e)

# ----------------------------------------------------
# 🤖 TEMEL SİSTEMLER & BİLGİ KOMUTLARI
# ----------------------------------------------------
@bot.tree.command(name="help", description="Tüm komutları ve sistemleri gösterir.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 x77 BOT - Eksiksiz Komut Listesi", color=discord.Color.blue())
    embed.add_field(name="🤖 Temel Sistemler", value="`/help`, `/ping`, `/userinfo`, `/serverinfo`, `/avatar`, `/botinfo`, `/sor`", inline=False)
    embed.add_field(name="🛡️ Moderasyon", value="`/ban`, `/kick`, `/mute`, `/unmute`, `/warn`, `/warnings`, `/clear`, `/lock`, `/unlock`", inline=False)
    embed.add_field(name="🎵 Müzik", value="`/play [şarkı]`, `/stop`", inline=False)
    embed.add_field(name="🎮 Eğlence & Ekonomi", value="`/8ball`, `/coinflip`, `/dice`, `/meme`, `/ship`, `/level`, `/gunluk`, Leaderboard", inline=False)
    embed.add_field(name="🏆 x77 Arena", value="`/arena-kayit`, `/mac-gir`, Takım & Turnuva sistemleri", inline=False)
    embed.set_footer(text="x77 Bot - Güvenlik ve E-Spor Altyapısı")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Botun gecikme süresini gösterir.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Gecikme süresi: **{latency}ms** 🏓")

@bot.tree.command(name="userinfo", description="Kullanıcı hakkında bilgi verir.")
async def userinfo(interaction: discord.Interaction, uye: discord.Member = None):
    target = uye or interaction.user
    embed = discord.Embed(title=f"Kullanıcı Bilgisi: {target.name}", color=discord.Color.gold())
    embed.add_field(name="ID", value=target.id, inline=True)
    embed.add_field(name="Sunucuya Katılım", value=target.joined_at.strftime("%d-%m-%Y") if target.joined_at else "Bilinmiyor", inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Sunucu hakkında bilgi verir.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Sunucu Bilgisi: {guild.name}", color=discord.Color.purple())
    embed.add_field(name="Üye Sayısı", value=guild.member_count, inline=True)
    embed.add_field(name="Kurucu", value=guild.owner, inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Kullanıcının profil fotoğrafını gösterir.")
async def avatar(interaction: discord.Interaction, uye: discord.Member = None):
    target = uye or interaction.user
    embed = discord.Embed(title=f"{target.name} adlı kullanıcının avatarı", color=discord.Color.blurple())
    embed.set_image(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="botinfo", description="Bot hakkında bilgi verir.")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="x77 Bot Bilgileri", description="Gemini yapay zeka destekli, e-spor ve müzik özellikli bot.", color=discord.Color.green())
    embed.add_field(name="Geliştirici / Sahip", value="WEXY", inline=True)
    embed.add_field(name="Sunucu Sayısı", value=f"{len(bot.guilds)}", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sor", description="Yapay zekaya soru sor.")
@discord.app_commands.describe(soru="Yapay zekaya yöneltmek istediğin soru")
async def sor(interaction: discord.Interaction, soru: str):
    await interaction.response.defer(thinking=True)
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="Sen x77 e-spor ve oyun sunucusunda takılan, WEXY ve OMG gibi takımların havasını bilen, biraz agresif, lafı gediğine oturtan, samimi ve Türkçe konuşan zeki bir yapay zeka botusun."
        )
        response = model.generate_content(soru)
        await interaction.followup.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"Kanka şu an yapay zeka beynim biraz yandı, sonra dene. Hata: {e}")

# ----------------------------------------------------
# 🎵 MÜZİK SİSTEMİ (/play & /stop) - ZAMAN AŞIMI GİDERİLDİ
# ----------------------------------------------------
@bot.tree.command(name="play", description="Ses kanalına gelip yazdığın şarkıyı bulur ve çalar.")
@discord.app_commands.describe(sarki="Çalmak istediğin şarkının adı veya linki")
async def play(interaction: discord.Interaction, sarki: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Kanka önce bir ses kanalına girmen lazım!", ephemeral=True)
        return

    # Zaman aşımını (10062 Unknown Interaction) önlemek için thinking=True ekledik
    await interaction.response.defer(thinking=True)
    channel = interaction.user.voice.channel
    
    try:
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()

        voice_client = interaction.guild.voice_client

        player = await YTDLSource.from_url(sarki, loop=bot.loop, stream=True)
        if voice_client.is_playing():
            voice_client.stop()
        
        voice_client.play(player, after=lambda e: print(f'Müzik bitti veya hata: {e}') if e else None)
        await interaction.followup.send(f"🎶 Şimdi çalınıyor: **{player.title}**")
    except Exception as e:
        await interaction.followup.send(f"Kanka şarkıyı açarken bi aksilik çıktı: {e}")

@bot.tree.command(name="stop", description="Botu ses kanalından çıkarır ve müziği durdurur.")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("🔇 Kanaldan ayrıldım, müzik bitti.")
    else:
        await interaction.response.send_message("Zaten bir ses kanalında değilim kanka.", ephemeral=True)

# ----------------------------------------------------
# 🏆 x77 ARENA VE E-SPOR SİSTEMİ
# ----------------------------------------------------
@bot.tree.command(name="arena-kayit", description="x77 Arena sistemine oyuncu kaydını yapar.")
async def arena_kayit(interaction: discord.Interaction, oyun_adi: str):
    await interaction.response.send_message(f"✅ Başarıyla x77 Arena'ya kayıt oldun! Oyun İçi Adın: **{oyun_adi}** (Elo: 1000)", ephemeral=True)

@bot.tree.command(name="mac-gir", description="Oynanan maçın sonucunu sisteme kaydeder.")
async def mac_gir(interaction: discord.Interaction, rakip_takim: str, sonuc: str):
    await interaction.response.send_message(f"🏆 Maç Sonucu Kaydedildi! Rakip: **{rakip_takim}** | Durum: **{sonuc}**")

# ----------------------------------------------------
# 🛡️ GELİŞMİŞ MODERASYON & KORUMA SİSTEMİ
# ----------------------------------------------------
@bot.tree.command(name="clear", description="Belirtilen miktarda mesajı siler.")
@commands.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, miktar: int):
    await interaction.channel.purge(limit=miktar)
    await interaction.response.send_message(f"🧹 **{miktar}** adet mesaj silindi!", ephemeral=True)

@bot.tree.command(name="ban", description="Kullanıcıyı sunucudan yasaklar.")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, uye: discord.Member, sebep: str = "Belirtilmedi"):
    await uye.ban(reason=sebep)
    await interaction.response.send_message(f"🔨 {uye.mention} sunucudan banlandı! Sebep: {sebep}")

@bot.tree.command(name="kick", description="Kullanıcıyı sunucudan atar.")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, uye: discord.Member, sebep: str = "Belirtilmedi"):
    await uye.kick(reason=sebep)
    await interaction.response.send_message(f"👢 {uye.mention} sunucudan atıldı! Sebep: {sebep}")

@bot.tree.command(name="mute", description="Kullanıcıyı susturur.")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, uye: discord.Member, dakika: int, sebep: str = "Belirtilmedi"):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=dakika)
    await uye.timeout(duration, reason=sebep)
    await interaction.response.send_message(f"🔇 {uye.mention} {dakika} dakika süreyle susturuldu! Sebep: {sebep}")

@bot.tree.command(name="unmute", description="Kullanıcının susturmasını kaldırır.")
@commands.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, uye: discord.Member):
    await uye.timeout(None)
    await interaction.response.send_message(f"🔊 {uye.mention} kullanıcısının susturması kaldırıldı.")

@bot.tree.command(name="warn", description="Kullanıcıya uyarı verir.")
@commands.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, uye: discord.Member, sebep: str):
    await interaction.response.send_message(f"⚠️ {uye.mention} uyarıldı! Sebep: **{sebep}**")

@bot.tree.command(name="lock", description="Kanalı mesaj gönderimine kapatır.")
@commands.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Kanal yazışmaya kapatıldı!")

@bot.tree.command(name="unlock", description="Kanalı mesaj gönderimine açar.")
@commands.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Kanal yeniden yazışmaya açıldı!")

# ----------------------------------------------------
# 🎮 EĞLENCE KOMUTLARI
# ----------------------------------------------------
@bot.tree.command(name="8ball", description="Sihirli 8-ball sorularını yanıtlar.")
@discord.app_commands.describe(soru="Yazacağın soru")
async def eight_ball(interaction: discord.Interaction, soru: str):
    import random
    cevaplar = ["Kesinlikle öyle.", "Büyük ihtimalle.", "Kesinlikle hayır.", "Bunu asla bilemezsin.", "Tekrar dene koçum."]
    await interaction.response.send_message(f"❓ Soru: {soru}\n🎱 Cevap: **{random.choice(cevaplar)}**")

@bot.tree.command(name="coinflip", description="Yazı tura atar.")
async def coinflip(interaction: discord.Interaction):
    import random
    sonuc = random.choice(["Yazı", "Tura"])
    await interaction.response.send_message(f"🪙 Para atıldı: **{sonuc}**!")

# ----------------------------------------------------
# 💬 OTO-CEVAP, KÜFÜR VE GÜVENLİK FİLTRESİ (`on_message`)
# ----------------------------------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    mesaj = message.content.lower()
    
    if "yarram" in mesaj:
        await message.channel.send("O kadar küçük değilim malesef.")
        return

    if "discord.gg/" in mesaj or "https://" in mesaj:
        if not message.author.guild_permissions.manage_messages:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda link/reklam paylaşmak yasak!")
            except:
                pass
            return

    agir_kufurler = ["amk", "aq", "amina", "amına", "orospu", "o.ç.", "oc", "sik", "anan", "yarrak", "pezevenk", "piç", "kahpe"]
    hafif_sozler = ["mal", "salak", "gerizekalı", "aptal", "ahmak", "enayi"]

    if any(kufur in mesaj for kufur in agir_kufurler):
        await message.channel.send("Hayırdır üstad, klavye delikanlılığına mi başladın? Ağzını toplasana biraz.")
        return
    elif any(kelime in mesaj for kelime in hafif_sozler):
        await message.channel.send("Aynaya baktın herhalde koçum, kendine gel.")
        return

    if bot.user.mentioned_in(message):
        prompt = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        if prompt:
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction="Sen e-spor kültürüne sahip, lafını esirgemeyen, sert ve agresif ama bir o kadar da zeki bir yapay zeka botusun. Sana küfür edene veya sataşana asla alttan alma, lafı gediğine oturt."
                )
                response = model.generate_content(prompt)
                await message.channel.send(response.text)
            except Exception as e:
                await message.channel.send(f"Kanka şu an yapay zeka beynim biraz yandı, sonra dene. Hata: {e}")
                return

    await bot.process_commands(message)

# Botu başlat
bot.run(os.environ.get("DISCORD_TOKEN"))
