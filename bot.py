import discord
from discord.ext import commands
from google import genai
import random

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} adet slash komut senkronize edildi.")
    except Exception as e:
        print(e)
    
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, 
        name="🤖 Created By WEXYx77 | /bilgi"
    ))
    
    print(f'{bot.user} olarak giriş yaptık! Bot tüm özellikleriyle aktif.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    mesaj = message.content.lower()

    # Sert laf iade sistemi (Küfür yakalama)
    if any(kufur in mesaj for kufur in ["amın oğlu", "amin oglu", "amin oğlu", "amın oglu"]):
        await message.channel.send("Asıl senin baban öyle lan!")
        return
    elif any(kufur in mesaj for kufur in ["oç", "oça", "orospu çocuğu"]):
        await message.channel.send("Sensin lan oç!")
        return
    elif "orospu" in mesaj or "orosbu" in mesaj:
        await message.channel.send("Sensin lan orospu!")
        return
    elif any(kufur in mesaj for kufur in ["amk", "aq", "amina", "amına"]):
        await message.channel.send("Senin amk!")
        return
    elif any(kufur in mesaj for kufur in ["siktir", "sikerim", "siktim", "sikik"]):
        await message.channel.send("Asıl sen siktir git lan!")
        return
    elif "yarram" in mesaj or "yarrak" in mesaj:
        await message.channel.send("O kadar küçük değilim canoooooo")
        return
    elif "anan" in mesaj:
        await message.channel.send("Anama laf etme, adabımla konuş!")
        return
    elif any(kelime in mesaj for kelime in ["mal", "salak", "gerizekalı", "aptal", "ahmak"]):
        await message.channel.send("Aynaya baktın herhalde?")
        return
    elif "pezevenk" in mesaj or "gevşek" in mesaj or "piç" in mesaj:
        await message.channel.send("Aynen kendinden biliyorsun.")
        return

    # YAPAY ZEKA SOHBET SİSTEMİ (Etiketlenince)
    if bot.user.mentioned_in(message):
        prompt = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        if prompt:
            try:
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config={
                        'system_instruction': 'Sen Discord sunucusunda takılan, biraz agresif, lafı gediğine oturtan, samimi ve Türkçe konuşan zeki bir yapay zeka botusun.'
                    }
                )
                await message.channel.send(response.text)
            except Exception as e:
                await message.channel.send("Kanka şu an yapay zeka beynim biraz yandı, sonra dene.")
        return

    await bot.process_commands(message)


# ================= PRATİK BOŞLUKLU TURNUVA SİSTEMİ =================

@bot.tree.command(name="turnuva_tablosu", description="Üzerine isim yazabileceğin boş bir turnuva şablonu verir.")
async def turnuva_tablosu(interaction: discord.Interaction):
    sablon_metin = (
        "🏆 **TURNUVA AĞACI ŞABLONU** 🏆\n\n"
        "**Çeyrek Finaller**\n"
        "🔸 [ İsim 1 ] vs [ İsim 2 ] ➡️ ( Kazanan: ______ )\n"
        "🔸 [ İsim 3 ] vs [ İsim 4 ] ➡️ ( Kazanan: ______ )\n"
        "🔸 [ İsim 5 ] vs [ İsim 6 ] ➡️ ( Kazanan: ______ )\n"
        "🔸 [ İsim 7 ] vs [ İsim 8 ] ➡️ ( Kazanan: ______ )\n\n"
        "**Yarı Finaller**\n"
        "🔹 [ 1. Maç Kazananı ] vs [ 2. Maç Kazananı ] ➡️ ( Kazanan: ______ )\n"
        "🔹 [ 3. Maç Kazananı ] vs [ 4. Maç Kazananı ] ➡️ ( Kazanan: ______ )\n\n"
        "👑 **FİNAL**\n"
        "🥇 [ Yarı Final 1 Kazananı ] vs [ Yarı Final 2 Kazananı ] ➡️ **ŞAMPİYON: ______**"
    )
    await interaction.response.send_message(sablon_metin)


@bot.tree.command(name="turnuva_olustur", description="İsimleri araya sadece boşluk koyarak yaz, bot şablona yerleştirsin.")
async def turnuva_olustur(interaction: discord.Interaction, isimler: str):
    liste = [p.strip() for p in isimler.split() if p.strip()]
    
    if len(liste) < 4:
        await interaction.response.send_message("Kanka turnuva kurmak için en az 4 isim yazmalısın! (Örn: Ahmet Mehmet Ali Veli)", ephemeral=True)
        return
    
    random.shuffle(liste)
    
    embed = discord.Embed(
        title="📋 Otomatik Doldurulmuş Turnuva Şablonu",
        description="İsimler boşluklara göre algılandı ve rastgele eşleştirildi:",
        color=discord.Color.dark_purple()
    )
    
    mac_metni = ""
    tur = 1
    for i in range(0, len(liste) - 1, 2):
        mac_metni += f"🔹 **Maç {tur}:** {liste[i]}  **VS**  {liste[i+1]}\n"
        tur += 1
        
    embed.add_field(name="⚔️ 1. Tur Eşleşmeleri", value=mac_metni if mac_metni else "Yetersiz oyuncu", inline=False)
    
    if len(liste) % 2 != 0:
        embed.add_field(name="🚀 Bay Geçen", value=f"✨ {liste[-1]} doğrudan üst tura çıktı!", inline=False)
        
    embed.set_footer(text="Created By WEXYx77")
    await interaction.response.send_message(embed=embed)


# ================= YÖNETİM VE MODERASYON =================

@bot.tree.command(name="clear", description="Sohbeti tertemiz yapar ve sıfırlar.")
@commands.has_permissions(administrator=True)
async def clear(interaction: discord.Interaction, miktar: int = 100):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"{len(deleted)} adet mesaj silindi, sohbet temizlendi!", ephemeral=True)

@clear.error
async def clear_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("Kanka kusura bakma ama bunu sadece yetkililer (sen) yapabilirsin!", ephemeral=True)

@bot.tree.command(name="anket", description="Sunucuda hızlıca bir oylama (anket) başlat.")
@commands.has_permissions(manage_messages=True)
async def anket(interaction: discord.Interaction, soru: str):
    embed = discord.Embed(title="📊 Sunucu Anketi", description=soru, color=discord.Color.blue())
    embed.set_footer(text=f"Anketi başlatan: {interaction.user.name}")
    await interaction.response.send_message("@everyone Yeni Anket Var!", embed=embed)
    mesaj = await interaction.original_response()
    await mesaj.add_reaction("👍")
    await mesaj.add_reaction("👎")


# ================= TİKTOK VE İÇERİK ÜRETİCİ ARAÇLARI =================

@bot.tree.command(name="hook", description="TikTok videoların için yapay zekaya vurucu bir giriş cümlesi (hook) ürettir.")
async def hook(interaction: discord.Interaction, konu: str = "genel"):
    await interaction.response.defer()
    try:
        prompt = f"Bana TikTok veya oyun videoları için izleyicinin ilk 3 saniyede videoda kalmasını sağlayacak, çok vurucu, merak uyandırıcı ve dikkat çekici 1 tane Türkçe hook (giriş cümlesi) yaz. Videonun konusu/bağlamı şu: {konu}. Sadece hook cümlesini ver, ekstra açıklama yapma."
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        await interaction.followup.send(f"🎬 **AI Destekli TikTok Hook'u ({konu}):**\n> {response.text}")
    except Exception as e:
        await interaction.followup.send("Kanka hook üretirken yapay zeka hata verdi, bi daha dene.")

@bot.tree.command(name="fikir", description="TikTok veya içerikler için yapay zekadan özgün video fikirleri al.")
async def fikir(interaction: discord.Interaction, kategori: str = "oyun"):
    await interaction.response.defer()
    try:
        prompt = f"Bana şu kategori/konu için TikTok'ta tutabilecek 3 tane yaratıcı, dikkat çekici video fikri ver: {kategori}. Kısa ve maddeler halinde yaz."
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        await interaction.followup.send(f"💡 **AI Video Fikirleri ({kategori}):**\n{response.text}")
    except Exception as e:
        await interaction.followup.send("Fikir üretirken hata oluştu kanka, sonra tekrar dene.")


# ================= YAPAY ZEKA VE EĞLENCE =================

@bot.tree.command(name="sor", description="Yapay zekaya soru sor")
async def sor(interaction: discord.Interaction, soru: str):
    await interaction.response.defer() # Discord'a "düşünüyorum" der, zaman aşımını engeller
    
    try:
        # Yapay zekaya istek attığın kod bura
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(soru)
        
        # Cevabı gönder
        await interaction.followup.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"Kanka yapay zeka şu an cevap veremiyor. Hata: {e}")
    except Exception as e:
        await interaction.followup.send("Kanka yapay zeka şu an cevap veremiyor.")

@bot.tree.command(name="zar", description="1 ile 6 arasında rastgele bir zar atar.")
async def zar(interaction: discord.Interaction):
    sonuc = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 Zar sonuçlandı: **{sonuc}** kaosu!")

@bot.tree.command(name="yazitura", description="Yazı mı Tura mı atar.")
async def yazitura(interaction: discord.Interaction):
    secim = random.choice(["Yazı", "Tura"])
    await interaction.response.send_message(f"🪙 Para havaya uçtu ve... **{secim}** geldi!")

@bot.tree.command(name="sunucubilgi", description="Bulunduğun sunucu hakkında detaylı bilgi gösterir.")
async def sunucubilgi(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"🏰 {guild.name} Sunucu Bilgileri", color=discord.Color.gold())
    embed.add_field(name="👑 Sunucu Sahibi", value=guild.owner, inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=guild.member_count, inline=True)
    embed.add_field(name="📅 Kuruluş Tarihi", value=guild.created_at.strftime("%d-%m-%Y"), inline=True)
    await interaction.response.send_message(embed=embed)


# ================= YARDIM / BİLGİ PANELİ =================

@bot.tree.command(name="bilgi", description="Botun tüm yeteneklerini ve komutlarını listeler.")
async def bilgi(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Bot Komut ve Özellik Rehberi",
        description="Sunucumuzu geliştirmek, turnuvaları yönetmek ve içerik üretmek için buradayız!\n\n🔗 **Sunucumuza gelebilirsiniz:** https://discord.gg/MpYufxfav",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="🏆 Turnuva Sistemi", value="`/turnuva_tablosu` - Boş turnuva ağacı şablonu verir\n`/turnuva_olustur [isim1 isim2...]` - İsimleri boşlukla yazıp şablona oturtur", inline=False)
    embed.add_field(name="🧹 Moderasyon", value="`/clear [miktar]` - Sohbeti temizler\n`/anket [soru]` - Hızlı oylama başlatır", inline=False)
    embed.add_field(name="🎬 TikTok & İçerik", value="`/hook [konu]` - Vurucu giriş cümleleri üretir\n`/fikir [kategori]` - Yaratıcı video fikirleri verir", inline=False)
    embed.add_field(name="🧠 Yapay Zeka", value="`/sor [soru]` - Yapay zekaya doğrudan soru sorarsın\n`@BotAdı [mesaj]` - Etiketleyerek sohbet edersin", inline=False)
    embed.add_field(name="🎮 Eğlence & Araçlar", value="`/zar` - Zar atarsın\n`/yazitura` - Yazı tura atarsın\n`/sunucubilgi` - Sunucu istatistiklerini görürsün", inline=False)
    embed.add_field(name="🛡️ Güvenlik", value="Ağır küfür ve hakaretlere karşı otomatik laf iade sistemi aktif.", inline=False)
    
    embed.set_footer(text="Created By WEXYx77")
    await interaction.response.send_message(embed=embed, ephemeral=True)

import os

bot.run(os.getenv('DISCORD_TOKEN'))
