# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import requests
from scrapy.http.request import Request
import time

PAGE_NUMBER_TO_CRAWL = 1

BASE_URL = 'https://www.indeed.com/jobs?q=data%20scientist&l=United%20States'
CHROMEDRIVER_LOC = "/usr/local/bin/chromedriver"


# ok, je veux faire un crawler qui, d'abord parse selon toutes les pages
# puis, après, dans chaque page je fais ça.

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']

    def __init__(self):
        self.job_token_ids = self.get_job_token_ids()
        self.start_urls = [self.full_job_url(job_token_id) for
                           job_token_id in
                           self.job_token_ids]
        self.driver = webdriver.Chrome(CHROMEDRIVER_LOC)
        self.start_requests()

    def start_requests(self):
        for url in self.start_urls:
            print("Fetching url: " + url)
            yield Request(url, callback=self.parse_job_description)

    def full_job_url(self, job_token_id):
        return BASE_URL + '&vjk=' + job_token_id

    def get_job_token_ids(self):
        job_token_ids = []

        for page_number in range(PAGE_NUMBER_TO_CRAWL):
            if page_number % 10 == 0:
                print("Page number: " + str(page_number))
            starting_job_count = str(page_number * 10)
            page_url = BASE_URL + '&start=' + starting_job_count
            r = requests.get(page_url)
            job_token_ids += re.findall("jk:'(\w+)'", r.text)
        return job_token_ids

    def parse_job_description(self, response):
        self.driver.get(response.url)

        job_title = self.driver.find_element_by_class_name("jobtitle").text
        company_name = self.driver.find_element_by_class_name("company").text
        summary = self.driver.find_element_by_class_name("summary").text

        yield {
            'job_title': job_title,
            'company_name': company_name,
            'summary': summary.encode('ascii', 'ignore').decode('utf-8')
        }
