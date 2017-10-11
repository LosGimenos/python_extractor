import eventlet
import datetime
import pytz
import os
from selenium import webdriver
import logging
from .amazon import get_amazon_reviews
from .walmart import get_walmart_reviews
from .target import get_target_reviews_js
from .walgreens import get_walgreens_reviews_js
from .ulta import get_ulta_reviews_js
from .makeupalley import get_makeup_alley_reviews_js
from .models import ProductPageUrl, Product, Review, Project
from .helpers import *

logger = logging.getLogger(__name__)

pool = eventlet.GreenPool()

urls = [
    ['Walmart', 'December 1, 2016', None],
    ['Ulta' , 'December 15, 2016', None]
]

def run_review_scraping(arg_list):
    source = arg_list[0]
    cutoff_date_text = arg_list[1]
    start_date_text = arg_list[2]

    if start_date_text == None:
        start_date = datetime.datetime.today().replace(tzinfo=pytz.UTC)
    else:
        start_date = datetime.datetime.strptime(start_date_text, "%B %d, %Y").replace(tzinfo=pytz.UTC)

    if cutoff_date_text == None:
        cutoff_date_text = "July 1, 2016"
    cutoff_date = datetime.datetime.strptime(cutoff_date_text, "%B %d, %Y").replace(tzinfo=pytz.UTC)

    brand_name = 'Neutrogena'
    project_name = 'Neutrogena Beauty'
    brand_website_name = 'Neutrogena'

    # 2 instance of block
    if Project.objects.filter(project_id=project_name).exists():
        project = Project.objects.get(project_id=project_name)
    else:
        project = Project(project_id = project_name)
        project.save()

    # source = 'MakeupAlley'
    # product_name_inclusions = ["Men's Rogaine"]
    # product_name_exclusions = ["Men's Rogaine"]

    if source == "MakeupAlley":

        chromedriver = "/usr/local/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver

        # setup driver

        driver = webdriver.Chrome(chromedriver)
        driver.set_window_size(1120, 550)
        driver.set_window_position(-10000,0)

        # connect to original review url

        succeeded = False
        num_attempts = 0
        max_num_attempts = 20
        while succeeded == False:
            num_attempts += 1
            if num_attempts > max_num_attempts:
                break
            try:
                print("Trying")
                driver.get("https://www.makeupalley.com/")
                succeeded = True
                print("Succeeded")
            except:
                print("Error")
                time.sleep(random.randint(2,3))

        # login

        xpath = '//li[@class="login"]/a'
        click_result = click_element_by_hitting_enter(driver,xpath)
        if click_result == "Error":
            print("Error clicking login link")

        time.sleep(2)
        username = driver.find_element_by_id("UserName")
        password = driver.find_element_by_id("Password")
        username.send_keys("asfbapp")
        password.send_keys("1asfbapp1")
        login_attempt = driver.find_element_by_xpath('//input[@id="login"]')
        login_attempt.submit()
        time.sleep(2)
        logger.warn("Logged in")

    else:

        driver = None

    for ppu in ProductPageUrl.objects.filter(project=project,source=source):
    # for ppu in ProductPageUrl.objects.filter(project=project,source=source,product_name__in=product_name_inclusions):
    # for ppu in ProductPageUrl.objects.filter(project=project,source=source).exclude(product_name__in=product_name_exclusions):

        #this entry?
        # if ppu.id < 4496:
        #     continue

        brand = ppu.brand
        group = ppu.group
        product_line = ppu.product_line
        product = ppu.product

        product = Product(project=project,brand=brand,group=group,product_line=product_line,
                          product=product,source=source)
        product.save()

        product_page_url = ppu.url
        source_data_path = ''
        # if source == 'Amazon' or source == 'Walmart':
        #     source_data_path = ''
        # else:
        #     source_data_path = 'files/Reviews/' + brand_name + '/' + project_name + '/' + source + '/Source Data/' + ppu.source_data_path + '.txt'

        # source_data_path = 'files/Reviews/Makeup Alley/Source Data/Tanda Zap.txt'

        get_reviews(project,product,product_page_url,source_data_path,source,start_date,cutoff_date,brand_website_name,driver)

        if source == "MakeupAlley":

            xpath = '//a[@class="dropdown-toggle"]'
            click_result = click_element_by_hitting_enter(driver,xpath)
            if click_result == "Error":
                print("Error clicking username dropdown")

            xpath = '//a[@href="/account/logout.asp"]'
            click_result = click_element_by_hitting_enter(driver,xpath)
            if click_result == "Error":
                print("Error clicking logout")

            time.sleep(2)

            driver.quit()

def get_reviews(project,product,product_page_url,source_data_path,source,start_date,cutoff_date,brand_website_name,driver):

    # Define source list

    # source_list = []
    # source_list.append(source)

    source_list = [source]

    # Get reviews

    headers_list = []
    headers_list.append({
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
    headers_list.append({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
    headers_list.append({
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25'})
    headers_list.append({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2'})
    headers_list.append({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10'})

    if source == 'Target':
        get_target_reviews_js(headers_list,product_page_url,project,product,start_date,cutoff_date,brand_website_name)
    elif source == 'Walgreens':
        get_walgreens_reviews_js(product_page_url,project,product,start_date,cutoff_date,brand_website_name)
    elif source == 'Ulta':
        get_ulta_reviews_js(product_page_url,project,product,start_date,cutoff_date,brand_website_name)
    elif source == 'MakeupAlley':
        get_makeup_alley_reviews_js(product_page_url,project,product,start_date,cutoff_date,brand_website_name,driver)
    elif source == 'Amazon':
        get_amazon_reviews(headers_list,product_page_url,project,product,start_date,cutoff_date,brand_website_name)
    elif source == 'Walmart':
        get_walmart_reviews(headers_list,product_page_url,project,product,start_date,cutoff_date,brand_website_name)


for item in pool.imap(run_review_scraping, urls):
    print ('Trying it out!')
