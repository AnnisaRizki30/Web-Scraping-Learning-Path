import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from lxml import etree
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
DRIVER_PATH = r"C:\Users\Annisa Rizki\Desktop\Annisa Lianda\Github Source\Web Scraping\Driver\chromedriver.exe"
chrome_service = Service(DRIVER_PATH)
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument(f'user-agent={USER_AGENT}')
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

browser.get("https://glints.com/id/opportunities/jobs/explore?country=ID&locationName=Indonesia&lastUpdated=PAST_MONTH&sortBy=LATEST")

time.sleep(5) 
scroll_pause_time = 1 
screen_height = browser.execute_script("return window.screen.height;") 
i = 1

while True:
    browser.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
    i += 1
    time.sleep(scroll_pause_time)
    scroll_height = browser.execute_script("return document.body.scrollHeight;")  
    if (screen_height) * i > scroll_height:
        break 

glint_urls = []
soup = BeautifulSoup(browser.page_source, "html.parser")

for parent in soup.select('div[class="JobCardsc__JobCardWrapper-sc-1f9hdu8-1 dPPDau"]>a'):
    site = "https://glints.com/id/opportunities/jobs/explore?country=ID&locationName=Indonesia&lastUpdated=PAST_MONTH&sortBy=LATEST"
    link = parent['href']
    url = urljoin(site, link)
    glint_urls.append(url)

job_info = pd.DataFrame()

for link in glint_urls:
    try:
        browser.get(link)
        time.sleep(5)
        html_source = browser.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        dom = etree.HTML(str(soup))

        temp_dict = {}

        job_info_json = json.loads(soup.select_one('script[type="application/ld+json"]').text)

        try:
            jobType = job_info_json['employmentType']
            try:
                temp_dict['Job Type'] = jobType
                print('Job Type = ' +  str(jobType))
            except ValueError:
                jobType = ''
        except KeyError:
            pass

        try:
            jobExp = dom.xpath('//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div/main/div[3]/div[4]/text()')[0]
            try:
                temp_dict['Job Experience'] = jobExp
                print('Job Experience = ' +  str(jobExp))
            except ValueError:
                jobExp = ''
        except IndexError:
                pass
        
        try:
            position = dom.xpath('//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div/main/div[3]/div[2]/a')[0].text
            try:
                temp_dict['Position'] = position
                print('Position = ' +  str(position))
            except ValueError:
                position = ''
        except IndexError:
                pass

        try:
            company = job_info_json['hiringOrganization']['name']
            try:
                temp_dict['Company'] = company
                print('Company = ' +  str(company))
            except ValueError:
                company = ''
        except KeyError:
                pass

        try:
            streetAddress = dom.xpath('//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div/main/div[8]/div/div[4]/text()')[0]
            try:
                temp_dict['Street Address'] = streetAddress
                print('Street Address = ' +  str(streetAddress))
            except ValueError:
                streetAddress = ''
        except IndexError:
                pass

        try:
            industry = dom.xpath('//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div/main/div[8]/div/div[2]/div[2]/div[2]/span[1]')[0].text
            try:
                temp_dict['Industry'] = industry
                print('Industry = ' +  str(industry))
            except ValueError:
                industry = ''
        except IndexError:
                pass

        try:
            jobTitle = dom.xpath('//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div/main/div[1]/div[2]/div/div[1]/h1')[0].text
            try:
                temp_dict['Job Title'] = jobTitle
                print('Job Title = ' +  str(jobTitle))
            except ValueError:
                jobTitle = ''
        except IndexError:
            jobTitle = ''
        
        try:
            jobRequirement = job_info_json['description']
            temp_dict['Job Requirement'] = jobRequirement
            print('Job Requirement = ' +  str(jobRequirement))
        except KeyError:
            jobRequirement = ''

        try:
            jobSalaryMin = dom.xpath('//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div/main/div[3]/div[1]/span/text()[1]')[0]
            try:
                temp_dict['Salary Min'] = jobSalaryMin
                print('Salary Min = ' +  str(jobSalaryMin))
            except ValueError:
                jobSalaryMin = ''
        except IndexError:
            jobSalaryMin = ''

        try:
            jobSalaryMax = dom.xpath('//*[@id="__next"]/div/div[3]/div[2]/div[2]/div[2]/div/main/div[3]/div[1]/span/text()[3]')[0]
            try:
                temp_dict['Salary Max'] = jobSalaryMax
                print('Salary Max = ' +  str(jobSalaryMax))
            except ValueError:
                jobSalaryMax = ''
        except IndexError:
            jobSalaryMax = ''
        
        try:
            skills = soup.find_all(class_='TagStyle__TagContent-sc-66xi2f-0 bxpfKm tag-content')
            skills_str = ''
            for i in range(len(skills)):
                if i == (len(skills) -1 ):
                    sub = skills[i].text
                else:
                    sub = skills[i].text + ', '
                skills_str = skills_str + sub
            temp_dict['Skills'] = skills_str
            print('Skills = ' +  str(skills_str))
        except AttributeError:
            skill = ''
        
        print('\n')

        temp_dict['Job Posting Link'] = link

        job_info = job_info.append(temp_dict, ignore_index=True)

    except:
        pass

print(job_info)
browser.close()