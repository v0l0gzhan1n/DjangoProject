from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from news.models import Article, Source, Category


class Command(BaseCommand):
    help = 'Fetch news from various sources'

    def handle(self, *args, **options):
        # Пример парсинга новостей (нужно адаптировать под реальные источники)
        sources = [
            {
                'name': 'Пример источника',
                'url': 'https://example.com/news',
                'category': 'general'
            }
        ]

        for source_data in sources:
            source, created = Source.objects.get_or_create(
                name=source_data['name'],
                defaults={'url': source_data['url']}
            )

            category, created = Category.objects.get_or_create(
                name=source_data['category'],
                defaults={'slug': source_data['category']}
            )

            try:
                response = requests.get(source_data['url'])
                soup = BeautifulSoup(response.text, 'html.parser')

                # Здесь нужно добавить логику парсинга конкретного сайта
                # Это пример - нужно адаптировать под реальную структуру сайта
                for news_item in soup.select('.news-item'):
                    title = news_item.select_one('h2').text.strip()
                    url = news_item.find('a')['href']
                    content = news_item.select_one('.description').text.strip()
                    published_at = datetime.strptime(
                        news_item.select_one('.date').text.strip(),
                        '%d.%m.%Y'
                    )
                    image_url = news_item.select_one('img')['src'] if news_item.select_one('img') else None

                    article, created = Article.objects.get_or_create(
                        title=title,
                        defaults={
                            'content': content,
                            'url': url,
                            'source': source,
                            'published_at': published_at,
                            'image_url': image_url
                        }
                    )

                    if created:
                        article.categories.add(category)
                        self.stdout.write(self.style.SUCCESS(f'Added: {title}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fetching {source_data["name"]}: {str(e)}'))