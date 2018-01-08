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

DOMAIN = 'https://www.indeed.com/jobs?q=data%20scientist&l=United%20States'


# ok, je veux faire un crawler qui, d'abord parse selon toutes les pages
# puis, après, dans chaque page je fais ça.

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']

    def __init__(self):
        dl2 = "/usr/local/bin/chromedriver"
        self.links = self.get_all_jd()
        self.start_urls = list(map(lambda x: self.input_in_indeed_string(x), self.links))
        self.driver = webdriver.Chrome(dl2)
        self.start_requests()

    def start_requests(self):
        for url in self.start_urls:
            print(url)
            yield Request(url, callback=self.parse_jd)

    def input_in_indeed_string(self, x):
        return 'https://www.indeed.com/jobs?q=data%20scientist&l=United%20States&vjk=' + x

    def get_all_jd(self):

        my_links = []

        for i in range(1):
            if i % 10 == 0:
                print(i)
            page_url = DOMAIN + '&start=' + str(i * 10)
            r = requests.get(page_url)
            my_links += re.findall("jk:'(\w+)'", r.text)
        return my_links

    def parse_jd(self, response):

        self.driver.get(response.url)

        job_title = self.driver.find_element_by_class_name("jobtitle").text
        company_name = self.driver.find_element_by_class_name("company").text
        summary = self.driver.find_element_by_class_name("summary").text
        print(job_title + ' , ' + company_name)
        # with open('job_summaries/jd1.txt', 'w') as file:
        #     file.write(job_title + "\n")
        #     file.write(company_name + "\n")
        #     file.write(summary.encode('ascii', 'ignore').decode('utf-8'))
        yield {
            job_title: job_title,
            company_name: company_name,
            summary: summary.encode('ascii', 'ignore').decode('utf-8')
        }
        print("FILE WAS WRITTEN")



