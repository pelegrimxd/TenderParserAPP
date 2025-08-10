import argparse
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from urllib.parse import urljoin
import time


def parse_tender_title(title_text):
    """Извлекает тип тендера"""
    title_text = title_text.replace('\n', ' ').strip()

    markers = ['№']

    for marker in markers:
        if marker in title_text:
            marker_pos = title_text.find(marker)
            tender_type = title_text[:marker_pos].strip()
            return tender_type

def parse_tenders(max_tenders, output_file, static_url):
    """парсер"""
    base_url = "https://www.b2b-center.ru/market/"
    tenders = []
    page = 1
    delay = 2

    while len(tenders) < max_tenders:
        try:
            url = f"{base_url}?page={page}" if page > 1 else base_url
            print(f"Парсинг страницы {page}...")

            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('tbody')

            if not table:
                print("Тендеры не найдены")
                break

            rows = table.find_all('tr')
            if not rows:
                print("Больше нет тендеров")
                break

            for row in rows:
                if len(tenders) >= max_tenders:
                    break

                try:
                    cells = row.find_all('td')
                    if len(cells) < 5:
                        continue

                    title_block = cells[0].find('a', class_='search-results-title')
                    title_text = title_block.text.strip()
                    tender_type = parse_tender_title(title_text)
                    number = re.search(r'\d+', title_block.text).group()
                    title = title_block.find('div', class_='search-results-title-desc').text.strip()
                    link = urljoin(base_url, title_block['href'])
                    customer = cells[1].find('a').text.strip()
                    published_date = cells[2].text.strip()
                    end_date = cells[3].text.strip()

                    tenders.append({
                        'tender_type': tender_type,
                        'tender_id': number,
                        'title': title,
                        'link': link,
                        'customer': customer,
                        'published_date': published_date,
                        'end_date': end_date,
                        'parsed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception as e:
                    print(f"Ошибка при парсинге строки: {e}")
                    continue

            page += 1
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе страницы {page}: {e}")
            break

    if tenders:
        save_to_csv(tenders, output_file, static_url)
        print(f"Успешно сохранено {len(tenders)} тендеров в {output_file}")
    else:
        print("Не удалось получить ни одного тендера")


def save_to_csv(tenders, filename, static_url):
    """Сохраняет данные в csv формате"""
    with open(static_url + filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['tender_type', 'tender_id', 'title', 'link', 'customer', 'published_date', 'end_date', 'parsed_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for tender in tenders:
            writer.writerow(tender)


def main():
    """main"""
    parser = argparse.ArgumentParser(description='Парсер тендеров с B2B-Center')
    parser.add_argument('--max', type=int, default=100, help='Максимальное количество тендеров')
    parser.add_argument('--output', required=True, help='Имя выходного файла')

    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    static_url = str(base_dir) + '/static/'

    parse_tenders(args.max, args.output, static_url)


if __name__ == "__main__":
    main()