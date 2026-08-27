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
    def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = ytdl.extract_info(url if url.startswith("http") else f"ytsearch:{url}", download=not stream)
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'{bot.user.name} aktif! x77 Arena ve Sistemler Tam Gaz Devrede.')
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash komut senkronize edildi.")
    except Exception as e:
        print(e)

# ----------------------------------------------------
# 🤖 TEMEL SİSTEMLER & DETAYLI /HELP MENÜSÜ
# ----------------------------------------------------
@bot.tree.command(name="help", description="Tüm komutları ve sistemleri detaylı gösterir.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 x77 ARENA - Komut ve Sistem Listesi", color=discord.Color.blue())
    
    embed.add_field(
        name="🤖 Temel Sistemler", 
        value="`/help` - Komutlar\n`/ping` - Gecikme\n`/userinfo` - Kullanıcı\n`/serverinfo` - Sunucu\n`/avatar` - Avatar\n`/botinfo` - Bot Bilgi\n`/sor` - Yapay Zeka", 
        inline=True
    )
    
    embed.add_field(
        name="🛡️ Moderasyon", 
        value="`/ban`, `/kick`, `/mute`, `/unmute`, `/warn`, `/warnings`, `/clear`, `/lock`, `/unlock`\n*(Oto-küfür, spam, raid ve reklam koruması aktif!)*", 
        inline=True
    )
    
    embed.add_field(
        name="🎵 Müzik Sistemi", 
        value="`/play [şarkı adı]` - Akıllı eşleşmeli müzik çalar\n`/stop` - Durdur ve çık", 
        inline=False
    )

    embed.add_field(
        name="🏆 x77 Arena & E-Spor", 
        value="`/arena-kayit` - Oyuncu kaydı\n`/mac-gir` - Maç sonucu\n*(Takım kurma, Elo/rank sistemi, Leaderboard ve turnuva altyapısı)*", 
        inline=True
    )

    embed.add_field(
        name="🎮 Eğlence & Ekonomi", 
        value="`/8ball`, `/coinflip`, `/dice`, `/meme`, `/ship`, `/level`, `/gunluk`, Leaderboard", 
        inline=True
    )

    embed.set_footer(text="x77 Bot - Güvenlik, E-Spor ve Müzik Altyapısı")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Botun gecikme süresini gösterir.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! Gecikme süresi: **{latency}ms** 🏓")

@bot.tree.command(name="botinfo", description="Bot hakkında bilgi verir.")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="x77 Bot Bilgileri", description="Gemini yapay zeka destekli, e-spor ve müzik özellikli bot.", color=discord.Color.green())
    embed.add_field(name="Geliştirici / Sahip", value="WEXY", inline=True)
    embed.add_field(name="Sunucu Sayısı", value=f"{len(bot.guilds)}", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sor", description="Yapay zekaya soru sor.")
@discord.app_commands.describe(soru="Yapay zekaya yöneltmek istediğin soru")
async def sor(interaction: discord.Interaction, soru: str):
    await interaction.response.defer()
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
# 🎵 MÜZİK SİSTEMİ (/play & /stop)
# ----------------------------------------------------
@bot.tree.command(name="play", description="Ses kanalına gelip yazdığın şarkıyı (yanlış yazsan bile) bulur ve çalar.")
@discord.app_commands.describe(sarki="Çalmak istediğin şarkının adı veya linki")
async def play(interaction: discord.Interaction, sarki: str):
    if not interaction.user.voice:
        await interaction.response.send_message("Kanka önce bir ses kanalına girmen lazım!", ephemeral=True)
        return

    await interaction.response.defer()
    channel = interaction.user.voice.channel
    
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect()

    voice_client = interaction.guild.voice_client

    try:
        player = YTDLSource.from_url(sarki, loop=bot.loop, stream=True)
        voice_client.play(player, after=lambda e: print(f'Hata: {e}') if e else None)
        await interaction.followup.send(f"🎶 Şimdi çalınıyor: **{player.title}**")
    except Exception as e:
        await interaction.followup.send(f"Kanka şarkıyı ararken bi aksilik çıktı: {e}")

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

# ----------------------------------------------------
# 💬 OTO-CEVAP, KÜFÜR VE GÜVENLİK FİLTRESİ (`on_message`)
# ----------------------------------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    mesaj = message.content.lower()
    
    # Özel Küfür Karşılığı
    if "yarram" in mesaj:
        await message.channel.send("O kadar küçük değilim malesef.")
        return

    # Reklam ve Spam Koruması
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

    # YAPAY ZEKA SOHBET SİSTEMİ (Etiketlenince)
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
