import discord
import openai
import os
from dotenv import load_dotenv

export DISCORD_TOKEN="
MTM0MzYwMTQ2NTEyMTMxMjkwOA.Gvkl48.A3CIn0bbzHm3WHrSUTJHqzlJDi5aUJWGN1G1Ls



"
export OPENAI_API_KEY="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"
python bot.py

# Загружаем токены из .env файла
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настройка OpenAI API
openai.api_key = OPENAI_API_KEY

# Создаем клиент Discord
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Бот {client.user} подключен!')

@client.event
async def on_message(message):
    # Игнорируем сообщения от самого бота
    if message.author == client.user:
        return
    
    # Отправляем запрос в OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message.content}]
    )
    
    reply = response["choices"][0]["message"]["content"]
    await message.channel.send(reply)

# Запуск бота
client.run(DISCORD_TOKEN)
