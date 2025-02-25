import discord
from discord.ext import commands, tasks
import random
import openai
import asyncio
import requests
import datetime
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")  
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Устанавливаем префикс команд и активируем расширенные намерения
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Файл памяти бота
MEMORY_FILE = "bot_memory.json"

# Если файла нет, создаём его
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

# Загружаем память
with open(MEMORY_FILE, "r", encoding="utf-8") as f:
    memory = json.load(f)

# Функция сохранения памяти
def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

# Функция запоминания пользователя
async def remember_user(user):
    if str(user.id) not in memory:
        memory[str(user.id)] = {"name": user.name, "favorite_games": [], "chat_history": [], "current_game": None}
        save_memory()

# Функция добавления чата в историю
async def add_chat_to_memory(user, message):
    if str(user.id) in memory:
        memory[str(user.id)]["chat_history"].append(message)
        if len(memory[str(user.id)]["chat_history"]) > 10:
            memory[str(user.id)]["chat_history"].pop(0)
        save_memory()

# Функция проверки времени работы
async def check_runtime():
    while True:
        now = datetime.datetime.now()
        weekday = now.weekday()  # 0 - Пн, 6 - Вс
        current_hour = now.hour

        if (weekday < 5 and (16 <= current_hour or current_hour < 2)) or (weekday >= 5 and (12 <= current_hour or current_hour < 2)):
            print("✅ Бот работает в разрешённое время.")
        else:
            print("🛑 Время отключения бота. Завершаю работу...")
            await bot.close()
            break

        await asyncio.sleep(600)  # Проверка каждые 10 минут

# Индивидуальное приветствие
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await remember_user(message.author)
    await add_chat_to_memory(message.author, message.content)
    
    if "привет" in message.content.lower():
        await message.channel.send(f'Привет, {message.author.name}! Как твои дела? 🎮')
    
    await bot.process_commands(message)  # Обрабатываем команды

# Команда для установки любимой игры
@bot.command()
async def favgame(ctx, *, game: str):
    await remember_user(ctx.author)
    memory[str(ctx.author.id)]["favorite_games"].append(game)
    save_memory()
    await ctx.send(f'🔥 {ctx.author.name}, я запомнил, что тебе нравится {game}!')

# Проверка активности игр у пользователей
@tasks.loop(minutes=10)
async def check_game_activity():
    for guild in bot.guilds:
        for member in guild.members:
            if member.activity and isinstance(member.activity, discord.Game):
                game_name = member.activity.name
                await remember_user(member)
                memory[str(member.id)]["current_game"] = game_name
                save_memory()
                role_name = f'Задрот {game_name}'
                role = discord.utils.get(guild.roles, name=role_name)
                
                if not role:
                    role = await guild.create_role(name=role_name, reason="Автоматическое присвоение ролей геймерам")
                
                if role not in member.roles:
                    await member.add_roles(role)
                    await member.send(f'🏆 Поздравляем! Теперь ты официально "Задрот {game_name}"!')

# Генерация случайных ответов для живости общения
@bot.command()
async def talk(ctx, *, message: str):
    responses = [
        "Ого, интересная мысль! 😃",
        "Ну вот, теперь я задумался... 🤔",
        "Расскажи подробнее! 🧐",
        "Ты всегда так говоришь, {user} 😆",
        "О, это похоже на то, что ты говорил раньше! 🎮"
    ]
    response = random.choice(responses).replace("{user}", ctx.author.name)
    await ctx.send(response)
    await add_chat_to_memory(ctx.author, message)

# Запуск бота и его функций
@bot.event
async def on_ready():
    print(f'🚀 Бот {bot.user} запущен!')
    bot.loop.create_task(check_runtime())
    check_game_activity.start()

bot.run(TOKEN)
