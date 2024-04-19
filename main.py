import re
import requests
from bs4 import BeautifulSoup


class ExperienceExtractor:
	def __init__(self):
		self.start_keyword = ""
		self.end_keyword = ""
		self.experience_keywords = []

	def extract(self, all_text):
		relevant_text = self.get_relevant_part(all_text)
		number = self.find_experience_keyword(relevant_text)
		return number

	def get_relevant_part(self, all_text):
		after_start = all_text.split(self.start_keyword)
		if len(after_start) < 2:
			self.errors.append("No start keyword")
			return after_start[0]
		before_end = after_start[1].split(self.end_keyword)
		if len(before_end) < 2:
			self.errors.append("No end keyword")
		return before_end[0]

	def find_experience_keyword(self, relevant_text):
		no_keywords = True
		sentences = relevant_text.split(self.delimiter)

		for keyword in self.experience_keywords:
			for sentence in sentences:
				position = sentence.find(keyword)
				if position != -1:
					no_keywords = False
					years = self.get_years(sentence, position)
					if years != "-1":
						return years

		if no_keywords:
			self.errors.append("No experience keywords")
			return "-1"

		return "0"

	def get_years(self, sentence, experience_position):
		return "-1"


class GoogleExperienceExtractor(ExperienceExtractor):
	def __init__(self):
		self.start_keyword = "minimum qualifications"
		self.end_keyword = "preferred qualifications"
		self.experience_keywords = ["experience"]
		self.delimiter = "\n"
		self.errors = []

	def get_years(self, sentence, experience_position):
		start_position = sentence.find("years")
		if start_position == -1:
			matches = re.findall("year[ .,;]", sentence)
			if len(matches) > 0:
				return "1"
			else:
				start_position = experience_position

		number = "-1"
		for match in re.finditer("[0-9] *-*/* *[0-9]?", sentence):
			if match.start() < start_position:
				number = match.group()
		return number


class AppleExperienceExtractor(ExperienceExtractor):
	def __init__(self):
		self.experience_keywords = ["experience"]
		self.delimiter = "\n"
		self.errors = []

	def extract(self, all_text):
		number = self.find_experience_keyword(all_text)
		return number

	def get_years(self, sentence, experience_position):
		start_position = sentence.find("years")
		if start_position == -1:
			matches = re.findall("year[ .,;]", sentence)
			if len(matches) > 0:
				return "1"
			else:
				start_position = experience_position

		number = "-1"
		for match in re.finditer("[0-9] *-*/* *[0-9]?", sentence):
			if match.start() < start_position:
				number = match.group()
		return number


class WebScraper:
	def scrape_extract(self):
		# add looking through other pages
		main_page_url = self.main_page_base + self.keyword + "&location=" + self.location
		main_page_soup = BeautifulSoup(requests.get(main_page_url).content, 'html5lib')
		job_links = []

		for link in main_page_soup.find_all('a'):
			href = str(link.get('href'))
			if self.pattern.match(href):
				job_links.append(href)

		for link in job_links:
			job_page_url = self.job_page_base + link
			print(job_page_url)
			job_page_soup = BeautifulSoup(requests.get(job_page_url).content, 'html5lib')
			text = str(job_page_soup.find_all("div", {self.field: self.field_name})[0])

			number = self.extractor.extract(text)
			print(number)


class GoogleWebScraper(WebScraper):
	def __init__(self, keyword, location):
		self.keyword = keyword
		self.location = location
		self.main_page_base = "https://www.google.com/about/careers/applications/jobs/results/?q="
		self.pattern = re.compile("jobs/results/.+")
		self.job_page_base = "https://www.google.com/about/careers/applications/"
		self.field = "class"
		self.field_name = "KwJkGe"
		self.extractor = GoogleExperienceExtractor()


class AppleWebScraper(WebScraper):
	def __init__(self, keyword, location):
		self.keyword = keyword
		self.location = location
		self.main_page_base = "https://jobs.apple.com/en-ca/search?search="
		self.pattern = re.compile("/en-ca/details/.+")
		self.job_page_base = "https://jobs.apple.com"
		self.field = "id"
		self.field_name = "accordion_keyqualifications"
		self.extractor = AppleExperienceExtractor()

gws = GoogleWebScraper("software", "Canada").scrape_extract()
print()
aws = AppleWebScraper("software", "canada-CANC").scrape_extract()
