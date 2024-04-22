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
```
pip3 install requests
pip3 install htlm5lib
pip3 install beautifulsoup4
pip3 install webdriver-manager
pip3 install selenium
```

## How to add a new scraper / extractor?
