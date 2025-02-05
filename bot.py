import asyncio
import aiohttp
import telebot
from bs4 import BeautifulSoup
from flask import Flask

# Telegram Bot Setup
TOKEN = 'YOUR_BOT_TOKEN'
CHANNEL_ID = '@YourChannelOrGroupID'  # Replace with your actual channel/group

bot = telebot.TeleBot(TOKEN)

posted_movies = set()
movie_list = []
real_dict = {}

async def tamilmv():
    main_url = 'https://www.1tamilmv.ac/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    movie_list.clear()
    real_dict.clear()

    async with aiohttp.ClientSession() as session:
        async with session.get(main_url, headers=headers) as response:
            html = await response.text()

    soup = BeautifulSoup(html, 'lxml')
    posts = soup.find_all('div', {'class': 'ipsType_break ipsContained'})

    if not posts:
        return

    for post in posts:
        title = post.find('a').text.strip()
        link = post.find('a')['href']

        if title not in posted_movies:
            movie_list.append(title)
            movie_details = await get_movie_details(link)
            real_dict[title] = movie_details

async def get_movie_details(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, 'lxml')
    magnets = [a['href'] for a in soup.find_all('a', href=True) if 'magnet:' in a['href']]

    details = []
    for magnet in magnets:
        msg = f"/qbleech {magnet}\n<b>Tag:</b> <code>@Mr_official_300</code> <code>2142536515</code>"
        details.append(msg)

    return details

async def post_movies():
    while True:
        await tamilmv()

        if movie_list:
            new_movies = [m for m in movie_list if m not in posted_movies]
            all_movies = new_movies + [m for m in movie_list if m in posted_movies]

            for movie in all_movies:
                if movie in real_dict:
                    for detail in real_dict[movie]:
                        bot.send_message(CHANNEL_ID, detail, parse_mode="HTML")
                        await asyncio.sleep(300)  # Delay 5 minutes between posts
                    posted_movies.add(movie)

        await asyncio.sleep(600)  # Check for new posts every 10 minutes

# Start bot in background
loop = asyncio.get_event_loop()
loop.create_task(post_movies())

# Start health check
from healthcheck import app
app.run(host="0.0.0.0", port=8080)
