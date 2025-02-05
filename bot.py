import asyncio
import aiohttp
import telebot
import logging
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# Telegram Bot Setup
TOKEN = '7843096547:AAHzkh6gwbeYzUrwQmNlskzft6ZayCRKgNU'
CHANNEL_ID = '-1002440398569'  # Replace with your actual channel/group

bot = telebot.TeleBot(TOKEN)

posted_movies = set()
movie_list = []
real_dict = {}

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Flask healthcheck app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

async def tamilmv():
    logger.info("Starting TamilMV scraping...")

    main_url = 'https://www.1tamilmv.pm/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    movie_list.clear()
    real_dict.clear()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(main_url, headers=headers) as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'lxml')
        posts = soup.find_all('div', {'class': 'ipsType_break ipsContained'})

        if not posts:
            logger.warning("No posts found.")
            return

        for post in posts:
            title = post.find('a').text.strip()
            link = post.find('a')['href']
            logger.info(f"Found movie: {title}")

            if title not in posted_movies:
                movie_list.append(title)
                movie_details = await get_movie_details(link)
                real_dict[title] = movie_details

    except Exception as e:
        logger.error(f"Error during TamilMV scraping: {e}")

async def get_movie_details(url):
    logger.info(f"Fetching details for {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, 'lxml')
    magnets = [a['href'] for a in soup.find_all('a', href=True) if 'magnet:' in a['href']]

    if not magnets:
        logger.warning(f"No magnet links found for {url}")

    details = []
    for magnet in magnets:
        msg = f"/qbleech {magnet}\n<b>Tag:</b> <code>@Mr_official_300</code> <code>2142536515</code>"
        details.append(msg)

    return details

async def post_movies():
    logger.info("Starting movie posting process...")

    while True:
        await tamilmv()

        if movie_list:
            new_movies = [m for m in movie_list if m not in posted_movies]
            all_movies = new_movies + [m for m in movie_list if m in posted_movies]

            for movie in all_movies:
                if movie in real_dict:
                    for detail in real_dict[movie]:
                        try:
                            logger.info(f"Posting movie: {movie}")
                            bot.send_message(CHANNEL_ID, detail, parse_mode="HTML")
                            await asyncio.sleep(300)  # Delay 5 minutes between posts
                        except Exception as e:
                            logger.error(f"Failed to send message for {movie}: {e}")
                    posted_movies.add(movie)

        await asyncio.sleep(600)  # Check for new posts every 10 minutes

def run_healthcheck():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    # Start health check in a separate thread
    health_thread = Thread(target=run_healthcheck)
    health_thread.start()

    # Start movie posting in the main event loop
    loop = asyncio.get_event_loop()
    loop.create_task(post_movies())
    loop.run_forever()
