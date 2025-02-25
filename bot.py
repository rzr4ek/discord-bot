import discord
import openai
import os
from dotenv import load_dotenv

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
