import re
import requests
from bs4 import BeautifulSoup

import time

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager


class ExperienceExtractor:
    def __init__(self):
        self.start_keyword = ""
        self.end_keyword = ""
        self.delimiter = "\n"
        self.experience_keywords = ["experience"]
        self.year_keywords = ["years", "yrs", "y-s"]
        self.number_words = ["zero", "one", "two", "three", "four",
                             "five", "six", "seven", "eight", "nine",
                             "ten", "eleven", "twelve"]

    def extract(self, all_text):
        relevant_text = self.get_relevant_part(all_text)
        answer = self.find_experience_keyword(relevant_text)
        return answer

    def get_relevant_part(self, all_text):
        after_start = all_text.split(self.start_keyword)
        if len(after_start) < 2:
            return after_start[0]
        before_end = after_start[1].split(self.end_keyword)
        return before_end[0]

    def find_experience_keyword(self, relevant_text):
        no_keywords = True
        sentences = relevant_text.split(self.delimiter)

        for keyword in self.experience_keywords:
            for sentence in sentences:
                position = sentence.find(keyword)
                if position != -1:
                    no_keywords = False
                    answer = self.get_years(sentence)
                    if answer[0] != "-1":
                        return answer

        if no_keywords:
            return "-1", ""

        # if there is a mention of an experience keyword, but no mention of
        # a number of years, most probably, no experience is needed
        return "0", ""

    def get_years(self, sentence):
        # look for words like "years", "yrs", etc
        end_position = -1
        for year_keyword in self.year_keywords:
            position = sentence.find(year_keyword)
            end_position = max(end_position, position)

        # look for the word "year"
        if end_position == -1:
            matches = re.findall(r"year\b", sentence)
            if len(matches) > 0:
                return "1", sentence

        # if there are no such words, end the search
        if end_position == -1:
            return "-1", ""

        start_position = max(0, end_position - 40)

        # look for years of experience, for example, 1-2 or 3+
        answer = "-1"
        matches = re.findall(r"\b[0-9] *t?o?-*/* *[0-9]?[0-9]?", sentence[start_position : end_position])
        if len(matches) > 0:
            answer = matches[-1]
            return answer, sentence

        # look for words with a similar meaning
        for word in self.number_words:
            matches = re.findall(r"\b" + word + r"\b", sentence[start_position : end_position])
            if len(matches) > 0:
                answer = matches[-1]

        if answer != "-1":
            return answer, sentence
        return "-1", ""


class GoogleExperienceExtractor(ExperienceExtractor):
    def __init__(self):
        super().__init__()
        self.start_keyword = "minimum qualifications"
        self.end_keyword = "preferred qualifications"


class AppleExperienceExtractor(ExperienceExtractor):
    def extract(self, all_text):
        answer = self.find_experience_keyword(all_text)
        return answer


class LinkedInExperienceExtractor(ExperienceExtractor):
    def __init__(self):
        super().__init__()
        self.start_keyword = "about the job"
        self.end_keyword = "set alert for similar jobs"


def print_answer(answers, link):
    for answer in answers:
        if answer[1] != "":
            print("Extracted " + str(answer[0]) + " from \"... " + str(answer[1]) + " ...\"")
        elif answer[0] == "-1":
            print("No mention of experience in the text")
        else:
            print("Experience mentioned without an exact number of years")
    print("Link:\n" + link + "\n")


class WebScraper:
    def start_scraper(self):
        print("Searching by keyword and location")
        main_page_url = self.main_page_base + self.keyword + "&location=" + self.location
        main_page_soup = BeautifulSoup(requests.get(main_page_url).content, "html5lib")

        print("Counting the number of pages with results")
        number_of_pages = self.count_pages(main_page_soup)

        for page in range(1, number_of_pages + 1):
            print("PAGE", page)
            self.job_links = []
            for elem in main_page_soup.find_all("a", href=True):
                if self.pattern.match(elem["href"]):
                    self.job_links.append(elem["href"])
            self.traverse_extract()

            if page == number_of_pages:
                break
            main_page_url = self.main_page_base + self.keyword + "&location=" + self.location + "&page=" + str(page + 1)
            main_page_soup = BeautifulSoup(requests.get(main_page_url).content, "html5lib")

    def traverse_extract(self):
        for link in self.job_links:
            job_page_url = self.job_page_base + link
            job_page_soup = BeautifulSoup(requests.get(job_page_url).content, "html5lib")

            answers = []
            for field in self.fields:
                elems = job_page_soup.find_all("div", {field[0]: field[1]})
                text = ""
                for string in elems[0].strings:
                    text += string + "\n"
                answers.append(self.extractor.extract(text.lower()))
            print_answer(answers, job_page_url)


class GoogleWebScraper(WebScraper):
    def __init__(self, keyword, location):
        self.keyword = keyword
        self.location = location
        self.main_page_base = "https://www.google.com/about/careers/applications/jobs/results/?q="
        self.pattern = re.compile("jobs/results/.+")
        self.job_page_base = "https://www.google.com/about/careers/applications/"
        self.job_links = []
        self.fields = [["class", "KwJkGe"]]
        self.extractor = GoogleExperienceExtractor()

    def count_pages(self, soup):
        for elem in soup.find_all(attrs={"aria-label": True}):
            label = elem["aria-label"]
            if label.find("Showing") != -1:
                numbers = list(map(int, re.findall(r'\d+', label)))
                pages = numbers[2] // numbers[1]
                if numbers[2] % numbers[1]:
                    pages += 1
                return pages
        return 1


class AppleWebScraper(WebScraper):
    def __init__(self, keyword, location):
        self.keyword = keyword
        self.location = location
        self.main_page_base = "https://jobs.apple.com/en-ca/search?search="
        self.pattern = re.compile("/en-ca/details/.+")
        self.job_page_base = "https://jobs.apple.com"
        self.job_links = []
        self.fields = [["id", "accordion_keyqualifications"], 
                      ["id", "accordion_education&experience"]]
        self.extractor = AppleExperienceExtractor()

    def count_pages(self, soup):
        elems = soup.find_all(attrs={"class": "pageNumber"})
        return int(elems[1].string)


class LinkedInWebScraper(WebScraper):
    def __init__(self, keyword, location, username, password):
        self.keyword = keyword
        self.location = location
        self.username = username
        self.password = password
        self.saved_data = "/tmp/extractor"
        self.wait_time = 2
        self.extractor = LinkedInExperienceExtractor()

    def scroll_down(self, driver):
        SCROLL_PAUSE_TIME = 0.5
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            # calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def start_scraper(self):
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=" + self.saved_data)
        options.add_argument("--start-maximized")

        chrome_path = ChromeDriverManager().install() 
        chrome_service = Service(chrome_path)
        driver = Chrome(options=options, service=chrome_service) 

        wait = WebDriverWait(driver, self.wait_time)
        driver.get("https://www.linkedin.com/?trk=public_jobs_nav-header-logo")

        try:
            print("Logging in")
            wait.until(EC.element_to_be_clickable((By.ID, "session_key"))).send_keys(self.username)
            wait.until(EC.element_to_be_clickable((By.ID, "session_password"))).send_keys(self.password)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            print("Already logged in")

        driver.get("https://www.linkedin.com/jobs/collections/recommended/")

        try:
            print("Searching by keyword and location")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Search by title, skill, or company']"))).send_keys(self.keyword)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='City, state, or zip code']"))).send_keys(self.location)
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "jobs-search-box__submit-button"))).click()
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
            print("Couldn't navigate the website")
            return

        current_page = 1
        while (True):
            print("PAGE", current_page)
            current_url = driver.current_url

            elements = driver.find_elements(By.CLASS_NAME, "job-card-container__link")
            job_links = []
            for elem in elements:
                try:
                    job_links.append(elem.get_attribute("href"))
                except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
                    pass

            for link in job_links:
                driver.get(link)
                try:
                    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "jobs-description__footer-button"))).click()
                except (NoSuchElementException, StaleElementReferenceException, TimeoutException):
                    pass
                text = driver.find_elements(By.CLASS_NAME, "mt4")[0].text
                answer = self.extractor.extract(text.lower())
                print_answer([answer], link)

            try:
                driver.get(current_url)
                xpath = "//button[@aria-label='Page " + str(current_page + 1) + "']"
                self.scroll_down(driver)
                wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
                current_page += 1
            except:
                return


#gws = GoogleWebScraper("software engineer", "United States").start_scraper()
#aws = AppleWebScraper("design", "united-states-USA").start_scraper()
lws = LinkedInWebScraper("software", "Toronto", "USERNAME", "PASSWORD").start_scraper()
