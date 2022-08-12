from pathlib import Path

import scrapy
from scrapy.crawler import CrawlerProcess

settings = {
    "LOG_LEVEL": "INFO",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"
}


class HindistorySpider(scrapy.Spider):
    name = 'hindistory'
    main_url = "http://hindistory.net"
    allowed_domains = ['hindistory.net']
    start_urls = ['http://hindistory.net/']
    custom_settings = settings

    def parse(self, response, **kwargs):
        for item in response.css("a.list-group-item"):
            link = item.css("::attr(href)").get()
            name = item.css("::text").get().strip()
            tag = "li" if name == "Whatsapp Status" else "p"
            url = self.main_url + link
            yield scrapy.Request(url,
                                 callback=self.parse_category,
                                 cb_kwargs={
                                     "name": name,
                                     "tag": tag
                                 })

    def parse_category(self, response, name, tag):
        self.create_folder(name)

        for url in response.css("table.table a::attr(href)").getall():
            url = self.main_url + url

            yield scrapy.Request(url,
                                 callback=self.parse_story,
                                 cb_kwargs={
                                     "name": name,
                                     "tag": tag
                                 })

    def parse_story(self, response, name, tag):
        print(response.url)
        head = response.css("h1.story-head::text").get()

        body = "\n".join(
            [
                item.strip()
                for item in response.css(f"div.col-md-9.col-md-push-3 {tag}::text").getall()
                if item.strip()
            ]
        )

        self.write_file(name, response.url, head, body)

    def create_folder(self, name):
        Path(f"stories/{name}").mkdir(parents=True, exist_ok=True)

    def write_file(self, name, url, head, body):
        number = url.split("/")[-1]
        with open(f"stories/{name}/{number}.txt", "w", encoding="utf-8") as file:
            text = f"{head}\n\n{body}\n\n{url}"
            file.write(text)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(HindistorySpider)
    process.start()
