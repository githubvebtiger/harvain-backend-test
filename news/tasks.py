import celery
import requests
from bs4 import BeautifulSoup

from .models import News


@celery.shared_task(name="task_start_news_import")
def task_start_news_import():
    news = []
    rss_url = "https://www.coindesk.com/arc/outboundfeeds/rss/"

    response = requests.get(rss_url)
    rss_content = response.content

    soup = BeautifulSoup(rss_content, 'xml')

    items = soup.find_all('item')

    for item in items:
        title = item.find('title').text if item.find('title') else None
        link = item.find('link').text if item.find('link') else None
        description = item.find('description').text if item.find('description') else None

        media_content = item.find('media:content')
        image_url = media_content['url'] if media_content else None

        news.append(News(image=image_url, header=title, content=description, link=link))

    News.objects.all().delete()
    News.objects.bulk_create(news)
