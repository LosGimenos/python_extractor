import re
import requests
from .models import Project, Product, Review, ProductPageUrl
import html
import datetime
import pytz
import logging
from selenium import webdriver
import time
import random
import os

from .helpers import *

logger = logging.getLogger(__name__)

def get_target_reviews_api(headers_list, product_page_url, project, product, start_date, cutoff_date, brand_website_name):
    if not isinstance(product_page_url, str):
        return

    chromedriver = "/usr/local/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    # setup driver

    driver = webdriver.Chrome(chromedriver)
    driver.set_window_size(1120, 550)
    driver.set_window_position(-10000, 0)

    # setup xpath dict
    xpaths = {
        "average_rating": '//*[@id="bvTag-reviewsSummary"]//span[@class="h-sr-only h-inlineWrap"]',
    }

    # setup regex dict
    regex = {
        "rating": '(.*?) out of 5 stars',
    }

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
            driver.get(product_page_url)
            succeeded = True
            print("Succeeded")
        except:
            print("Error")
            time.sleep(random.randint(2, 5))

    error_message = "error getting average rating text"
    time.sleep(10)
    result = get_elements(driver, xpaths["average_rating"], error_message)

    time.sleep(2)

    if result == 'Error':
        product.average_rating = float(0)
        product.save()

    else:
        try:
            rating_result = result.pop(0).text
        except:
            logger.warn('No average rating')
            product.average_rating = float(0)
            product.save()

        matches = re.findall(regex['rating'], rating_result)

        if len(matches) == 0:
            logger.warn("No matches - Product - average rating")
        else:
            product.average_rating = float(matches[0])
            product.save()
            logger.warn(matches[0])

    driver.quit()

    time.sleep(3)
    url_item = product_page_url.split('-/A-')[-1]
    url = 'https://redsky.target.com/groot-domain-api/v1/reviews/' + url_item + '?sort=time_desc&filter=&limit=1000&offset=0'
    page_source = requests.get(url, headers=random.choice(headers_list)).json()
    try:
        product.total_number_reviews = page_source['totalResults']
        product.save()
        reviews = page_source['result']
    except:
        logger.warn(page_source)

    for item in reviews:
        review_date = item['SubmissionTime']
        review_date = review_date.split("T")[0]
        review_date = datetime.datetime.strptime(review_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)

        if review_date > start_date:
            continue

        if review_date < cutoff_date:
            return

        review_text = item['ReviewText']
        title = item['Title']

        if item['IsSyndicated']:
            is_from_brand_website = item['SyndicationSource']['Name']
        else:
            is_from_brand_website = ''

        if item['IsRecommended']:
            would_recommend = 'would recommend'
        else:
            would_recommend = 'would not recommend'

        rating = item['Rating']
        username = item['UserNickname']

        review = Review(project=project, product=product, date=review_date, title=title,
                        username=username, review_text=review_text,
                        rating=float(rating), is_from_brand_website=is_from_brand_website,
                        would_recommend=would_recommend)

        review.save()
        calculate_review_stats(project, product)
