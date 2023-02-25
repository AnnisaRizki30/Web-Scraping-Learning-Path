import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from lxml import etree
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
DRIVER_PATH = r"C:\Users\Annisa Rizki\Desktop\Annisa Lianda\Github Source\Web Scraping\Driver\chromedriver.exe"
chrome_service = Service(DRIVER_PATH)
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument(f'user-agent={USER_AGENT}')
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

browser.get("https://www.techinasia.com/jobs/search?country_name[]=Indonesia&experience[]=0-1")

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

techinasia_urls = []
soup = BeautifulSoup(browser.page_source, "html.parser")

for parent in soup.find_all(class_="jsx-1749311545 details"):
    a_tag = parent.find("a")
    site = "https://www.techinasia.com/jobs/search?country_name[]=Indonesia&experience[]=0-1"
    link = a_tag.attrs['href']
    url = urljoin(site, link)
    techinasia_urls.append(url)

job_info = pd.DataFrame()

for link in techinasia_urls:
    try:
        browser.get(link)
        time.sleep(5)
        html_source = browser.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        dom = etree.HTML(str(soup))

        temp_dict = {}

        try:  
            jobType = dom.xpath('//*[@id="app"]/div/div[4]/div/header/div/div/div/div/div/div[2]/div[2]/b')[0].text.strip().replace('\n', '')
            try:
                temp_dict['Job Type'] = jobType
                print('Job Type = ' +  str(jobType))
            except ValueError:
                jobType = ''
        except IndexError:
                pass

        try:
            jobExp = dom.xpath('//*[@id="app"]/div/div[4]/div/header/div/div/div/div/div/div[2]/div[3]/b')[0].text.strip().replace('\n', '')
            try:
                temp_dict['Job Experience'] = jobExp
                print('Job Experience = ' +  str(jobExp))
            except ValueError:
                jobExp = ''
        except IndexError:
                pass
        
        try:
            position = dom.xpath('//*[@id="app"]/div/div[4]/div/header/div/div/div/div/div/div[2]/div[1]/b')[0].text.strip().replace('\n', '')
            try:
                temp_dict['Position'] = position
                print('Position = ' +  str(position))
            except ValueError:
                position = ''
        except IndexError:
                pass

        try:
            vacancyCount = dom.xpath('//*[@id="app"]/div/div[4]/div/header/div/div/div/div/div/div[2]/div[4]/b')[0].text.strip().replace('\n', '')
            try:
                temp_dict['Vacancy Count'] = int(vacancyCount)
                print('Vacancy Count = ' +  str(vacancyCount))
            except ValueError:
                vacancyCount = ''
        except IndexError:
                pass

        try:
            company = dom.xpath('//*[@id="app"]/div/div[4]/div/header/div/div/div/div/div/div[1]/div[1]/a')[0].text
            try:
                temp_dict['Company'] = company
                print('Company = ' +  str(company))
            except ValueError:
                company = ''
        except IndexError:
                pass
        
        try:
            location = dom.xpath('//*[@id="app"]/div/div[4]/div/header/div/div/div/div/div/div[1]/div[2]')[0].text
            try:
                temp_dict['Location'] = location
                print('Location = ' +  str(location))
            except ValueError:
                location = ''
        except IndexError:
                pass

        try:
            industry = dom.xpath('//*[@id="app"]/div/div[4]/div/div[4]/div/div[2]/div/section[1]/dl/dd[2]')[0].text
            try:
                temp_dict['Industry'] = industry
                print('Industry = ' +  str(industry))
            except ValueError:
                industry = ''
        except IndexError:
                pass

        try:
            jobTitle = soup.find('h1', class_="jsx-3446601365").text.strip()
            temp_dict['Job Title'] = jobTitle
            print('Job Title = ' +  str(jobTitle))
        except AttributeError:
            jobTitle = ''
        
        try:
            jobDescription = soup.find('div', {'class': 'jsx-3475296548'}).text.strip()
            temp_dict['Job Desc'] = jobDescription
            print('Job Desc = ' +  str(jobDescription))
        except AttributeError:
            jobDescription = ''

        try:
            jobSalary = soup.find('div', class_="jsx-3446601365 compensation").text.strip()
            temp_dict['Job Salary'] = jobSalary
            print('Job Salary = ' +  str(jobSalary))
        except AttributeError:
            jobSalary = ''
        
        try:
            skills = soup.find_all('span', attrs={'data-cy': 'tag', 'class': 'jsx-3713767817 '})
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