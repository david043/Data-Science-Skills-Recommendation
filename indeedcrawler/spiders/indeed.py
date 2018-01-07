# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import requests

DOMAIN = 'https://www.indeed.com/jobs?q=data%20scientist&l=United%20States'


# ok, je veux faire un crawler qui, d'abord parse selon toutes les pages
# puis, après, dans chaque page je fais ça.

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']
    start_urls = [DOMAIN + '&vjk=76832337e0f02aea']

    def __init__(self):
        dl2 = "/usr/local/bin/chromedriver"
        self.driver = webdriver.Chrome(dl2)
        self.links = self.get_all_jd()

    def parse_item(self, response):
        print(response.url)

    def input_in_indeed_string(self, x):
        return 'https://www.indeed.com/jobs?q=data%20scientist&l=United%20States&vjk=' + x

    def get_all_jd(self):

        my_links = []

        for i in range(50):
            page_url = DOMAIN + '&start=' + str(i * 10)
            r = requests.get(page_url)
            my_links += list(map(lambda x: self.input_in_indeed_string(x), re.findall("jk:'(\w+)'", r.text)))
        return my_links

    #def parse(self, response):
    #    print("LINKS !!!!!!!")
    #    for link in self.links:
    #        yield scrapy.Request(link, callback=self.parse_jd(link))

    def parse_jd(self, response):
        self.driver.get(response)

        job_title = self.driver.find_element_by_class_name("jobtitle").text
        company_name = self.driver.find_element_by_class_name("company").text
        summary = self.driver.find_element_by_class_name("summary").text

        with open('job_summaries/jd1.txt', 'w') as file:
            file.write(job_title + "\n")
            file.write(company_name + "\n")
            file.write(summary)
        print("FILE WAS WRITTEN")

        self.driver.close()
