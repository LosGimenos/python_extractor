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

def get_makeup_alley_reviews_js(product_page_url, project, product, start_date, cutoff_date, brand_website_name, driver):
    logger.warn('In scraper')

    if not isinstance(product_page_url, str):
        return

    # setup xpath dict
    xpaths = {
        "average_rating": '//*[@id="product-details"]/div/div[1]/div[2]/div/div[1]/h3',
        "last_page_number_element": '//li[@class="next"]/a',
        "active_page_element": '//a[@class="active"]',
        "last_date_element": '//*[@id="reviews-wrapper"]/div[last()]/div[1]/div[1]/div[3]/p',
        "all_date_elements": '//*[@id="reviews-wrapper"]/div/div[1]/div[1]/div[3]/p',
        "all_username_elements": '//*[@id="reviews-wrapper"]/div/div[1]/div[1]/div[2]/p/a',
        "all_rating_elements": '//*[@id="reviews-wrapper"]/div/div[1]/div[1]/div[1]/span[1]',
        "all_review_text_elements": '//*[@id="reviews-wrapper"]/div/div[2]/div/p',
    }

    # setup regex dict
    regex = {
        "rating": 'l-([0-9]+?)-',
        "core_url": '(https://www.makeupalley.com/product/showreview.asp/ItemId=[0-9]+/?)',
        "last_page": '\/page=([0-9]+?)\/',
        "date": ' ([0-9]+\/[0-9]+\/[0-9][0-9][0-9][0-9]?)'
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
            print("Succeeded connecting to review url post login")
        except:
            print("Error")
            time.sleep(random.randint(2,3))

    time.sleep(2)

    # get average rating text

    error_message = "error getting average rating text"
    result = get_element(driver,xpaths['average_rating'],error_message)

    if result == "Error":
        logger.warn('Did not get average rating.')
        product.delete()
        return
    else:
        try:
            product.average_rating = float(result.strip())
            product.save()
        except:
            logger.warn("Couldn't convert string to float")
            logger.warn(result.strip())
            product.delete()
            # driver.quit()
            return

    # get core url

    core_url_matches = re.findall(regex['core_url'], product_page_url)

    if len(core_url_matches) == 0:
        logger.warn("Error extracting core url")
    else:
        core_url = core_url_matches[0]

    # get last page number

    error_message = "error getting last page number"
    try:
        result = driver.find_element_by_xpath(xpath)
    except:
        result = "Error"

    if result == "Error":
        last_page_number = 1
        logger.warn("Last page = 1")
    else:
        link_href = result.get_attribute("href")
        last_page_matches = re.findall(regex['last_page'], link_href)

        if len(last_page_matches) == 0:
            product.delete()
            logger.warn("Error extracting last page number")
            # driver.quit()
            return
        else:
            last_page_number = int(last_page_matches[0])
            logger.warn("Last page = " + str(last_page_number))

    # loop through pages and get data

    date_matches = []
    username_matches = []
    rating_matches = []
    review_text_matches = []
    # skin_matches = []

    while True:

        time.sleep(2)

        # get active page number

        error_message = "error getting active page number"
        result = get_element(driver,xpaths['active_page_element'],error_message)

        if result == "Error":
            active_page_number = last_page_number
        else:
            active_page_number = int(result)

        # get dates
        error_message = "error getting dates"
        results = get_elements(driver,xpaths['all_date_elements'],error_message)

        for date in results:

            raw_date_text = date.text

            date_regex_matches = re.findall(regex['date'], raw_date_text)

            if len(date_regex_matches) == 0:
                logger.warn("No matches - date")
            else:
                date_text = date_regex_matches[0]
                date_matches.append(date_text)

        # get usernames

        error_message = "error getting usernames"
        username_results = get_elements(driver,xpaths['all_username_elements'],error_message)

        for username in username_results:

            username_matches.append(username.text.strip())

        # get ratings

        error_message = "error getting ratings"
        results = driver.find_elements_by_xpath(xpaths['all_rating_elements'])

        for rating in results:

            raw_rating_text = rating.get_attribute("class")

            rating_regex_matches = re.findall(regex['rating'], raw_rating_text)

            if len(rating_regex_matches) == 0:
                logger.warn("No matches - rating")
            else:
                rating_text = rating_regex_matches[0]
                rating_matches.append(rating_text)

        # get review texts

        error_message = "error getting review texts"
        results = get_elements(driver,xpaths['all_review_text_elements'],error_message)

        for review_text in results:

            review_text_matches.append(review_text.text.replace("<br>",""))

        logger.warn("Step 3")

        # check if last date on page is greater than cutoff

        error_message = "error getting last date"
        results = get_elements(driver,xpaths['last_date_element'],error_message)

        if results == "Error":
            last_date_text = datetime.datetime.now().strftime("%m/%d/%Y")
        else:

            raw_last_date_text = results[0].text

            last_date_regex_matches = re.findall(regex['date'], raw_last_date_text)

            if len(last_date_regex_matches) == 0:
                logger.warn("No matches - last date")
            else:
                last_date_text = last_date_regex_matches[0]

        # Convert date

        review_date = datetime.datetime.strptime(last_date_text, "%m/%d/%Y").replace(tzinfo=pytz.UTC)

        if review_date < cutoff_date or review_date > start_date:
            break
        else:

            # click next

            if active_page_number < last_page_number:

                next_page_number = active_page_number + 1

                new_product_page_url = core_url + "page=" + str(next_page_number) + "/"

                succeeded = False
                num_attempts = 0
                max_num_attempts = 20
                while succeeded == False:
                    num_attempts += 1
                    if num_attempts > max_num_attempts:
                        break
                    try:
                        print("Trying")
                        driver.get(new_product_page_url)
                        succeeded = True
                        print("Succeeded")
                    except:
                        print("Error")
                        time.sleep(random.randint(3,4))

            else:
                break

    # quit driver

    # driver.quit()

    # Create individual reviews

    index = 0

    logger.warn("Step 4")

    for individual_review_date in date_matches:

        review_text = html.unescape(review_text_matches[index])
        review_text = review_text.replace("<br />","")

        review_date = datetime.datetime.strptime(individual_review_date, "%m/%d/%Y").replace(tzinfo=pytz.UTC)

        review = Review(project=project,product=product,date=review_date,
                        username=str(username_matches[index]).replace(' ','').replace('-',''),review_text=review_text,
                        rating=float(rating_matches[index]),
                        is_from_brand_website="")

        review.save()

        index += 1

    logger.warn("Step 5")

    all_reviews = [r for r in Review.objects.filter(project = project, product=product)]

    for review in all_reviews:

        check_date_against_cutoff_date(review, cutoff_date, start_date)

    logger.warn("Step 6")

    calculate_review_stats(project, product)
