# experience-extractor

## What does it do?

This code scrapes data from websites with job listings and extracts the minimum number of years of experience needed to qualify for each posted job. Currently it can navigate LinkedIn, Google Careers, and Apple Careers. For each job posting it finds, the code outputs the needed number of years, the excerpt it extracted the number from, and a link to the job posting:

```
PAGE 2
Extracted 5  from "... 5 years of experience as a technical sales engineer in a cloud computing environment or in a customer-facing role (e.g. as a member of a professional services or systems engineering team). ..."
Link:
<link to the job posting>

Extracted 0-2 from "...  b.s./ms/ph.d degree in electrical engineering or computer science with 0-2 yrs of experience. ..."
Link:
<link to the job posting>
```

## How to use it?

First, you need to install the following packages:
```
pip3 install requests
pip3 install htlm5lib
pip3 install beautifulsoup4
pip3 install webdriver-manager
pip3 install selenium
```

Scrapers inherited from the WebScraper class are powered by Beautiful Soup. To use them (or write your own scraper for a similar website), you only need requests, html5lib and beautifulsoup4.

The LinkedIn scraper is a bit more complex and uses Selenium to log in to LinkedIn and browse its pages. To use it, you need to download Chrome.

To start the experience extractor, uncomment one of the following lines in main.py:

```
#gws = GoogleWebScraper("software engineer", "United States").start_scraper()
#aws = AppleWebScraper("design", "united-states-USA").start_scraper()
#lws = LinkedInWebScraper("software", "Toronto", "USERNAME", "PASSWORD").start_scraper()
```

All three scrapers use a keyword and location to filter job listings; the LinkedIn scraper also needs a username-password pair for your account. Now, run the code and enjoy!

```
python3 main.py
```
