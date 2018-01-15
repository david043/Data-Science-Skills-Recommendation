import scrapy
from selenium import webdriver
import re
import requests
from scrapy.http.request import Request
from selenium.common.exceptions import TimeoutException

PAGE_NUMBER_TO_CRAWL = 1
BASE_URL = 'https://www.indeed.com/jobs?q=data%20scientist&l=United%20States'
CHROMEDRIVER_LOC = "/usr/local/bin/chromedriver"


class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']

    def __init__(self, pages_to_crawl=0):

        if pages_to_crawl != 0:
            self.pages_to_crawl = pages_to_crawl
        else:
            self.pages_to_crawl = PAGE_NUMBER_TO_CRAWL

        self.job_token_ids = self.get_job_token_ids()
        self.start_urls = [self.full_job_url(job_token_id) for
                           job_token_id in
                           self.job_token_ids]
        self.driver = webdriver.Chrome(CHROMEDRIVER_LOC)
        self.driver.set_page_load_timeout(30)
        self.start_requests()

    def start_requests(self):
        for index, url in enumerate(self.start_urls):
            print("Fetching url " + str(index) + ": " + url + '\n')
            try:
                yield Request(url, callback=self.parse_job_description)
            except TimeoutException as e:
                print(e)

    def full_job_url(self, job_token_id):
        return BASE_URL + '&vjk=' + job_token_id

    def get_job_token_ids(self):
        job_token_ids = []

        for page_number in range(int(self.pages_to_crawl)):
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
