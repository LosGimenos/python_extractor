from bs4 import BeautifulSoup

import os
import re
import requests
from .models import Project, Product, Review, ProductPageUrl
import html
import datetime
import pytz
import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

from .helpers import *

logger = logging.getLogger(__name__)

def get_walmart_reviews(headers_list, product_page_url, project, product, start_date, cutoff_date, brand_website_name):

    headers = headers_list[0]

    try:
        page_source = requests.get(product_page_url, headers=headers).text
    except:
        logger.warn('No valid URL')
        return

    chromedriver = "/usr/local/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    # setup driver

    driver = webdriver.Chrome(chromedriver)
    driver.set_window_size(1120, 550)
    driver.set_window_position(-10000, 0)

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
            time.sleep(random.randint(2, 3))

    time.sleep(5)

    # Attempt to sort according to most recent

    sorted_by_most_recent = False

    try:
        actions = ActionChains(driver)
        selector = driver.find_element_by_xpath("//div[@class=' chooser ']")
        actions.move_to_element(selector).perform()
        selector.click()
    except:
        logger.warn('Couldnt get selector')

    try:
        select = Select(driver.find_element_by_xpath("//select[@class='visuallyhidden']"))
        select.select_by_value('submission-desc')
        driver.find_element_by_xpath("//div[text()='Newest to oldest']").click()
        sorted_by_most_recent = True
    except:
        logger.warn("Couldn't select dropdown filter")

    error_message = 'Could not get average rating element'
    try:
        average_rating_element = get_element(driver, '//*[@id="CustomerReviews-container"]/div[1]/div[1]/div[1]/span[1]', error_message)
        average_rating = average_rating_element.split(' ')[0]
    except:
        logger.warn('Could not get average rating')

    error_message = 'Could not get Total Reviews element'
    try:
        total_reviews_element = get_element(driver, '//*[@id="CustomerReviews-container"]/div[1]/div[1]/div[1]/span[2]', error_message)
        total_reviews = total_reviews_element.split(' ')[1]
    except:
        logger.warn('Could not get Total Reviews')

    within_cutoff_date = True
    end_of_pages = False
    current_page = 1

    while within_cutoff_date and not end_of_pages:

        error_message = 'Could not get Reviews Elements'
        try:
            review_elements = get_elements(driver, '//div[@class="CustomerReviews-list"]//div[@class="Grid ReviewList-content"]//div[@class="Grid-col u-size-8-12-m customer-review-body"]', error_message)
        except:
            logger.warn('Could not get reviews')


        for review in review_elements:
            try:
                date = review.find_element_by_class_name('review-submissionTime').text
            except:
                logger.warn('No review')
                end_of_pages = True
                break

            review_date = datetime.datetime.strptime(date, '%m/%d/%Y').replace(tzinfo=pytz.UTC)

            if review_date > start_date:
                continue

            review_title = review.find_element_by_class_name('review-title').text
            review_text = review.find_element_by_class_name('zeus-collapsable').text
            username_originpost_list = review.find_elements_by_class_name('font-semibold')
            username = username_originpost_list[0].text
            rating = len(review.find_elements_by_class_name('star-rated'))

            try:
                is_from_brand = username_originpost_list[1].text

                if is_from_brand != 'Read more':
                    is_from_brand = is_from_brand + '.com'
                else:
                    is_from_brand = None
            except:
                is_from_brand = None
                logger.warn('No original post')

            if sorted_by_most_recent and review_date < cutoff_date:
                within_cutoff_date = False
                break
            elif not sorted_by_most_recent and review_date < cutoff_date:
                continue
            else:
                review = Review(project=project, product=product, date=review_date, title=review_title,
                                username=username, review_text=review_text,
                                rating=float(rating), is_from_brand_website=is_from_brand)

                review.save()

        current_page = current_page + 1
        xpath_for_page_selector = "//button[text()='%s']" % current_page
        try:
            pagination_element = driver.find_element_by_xpath(xpath_for_page_selector)
        except:
            logger.warn('End of Pages list')
            end_of_pages = True
            break

        time.sleep(3)
        pagination_element.click()

    calculate_review_stats(project, product)
    driver.quit()


