import time
import schedule
from web_scraper_bot import scrape_loop


def main():
    schedule.every().day.at("19:00").do(scrape_loop)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
