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

def get_ulta_reviews_js(product_page_url, project, product, start_date, cutoff_date, brand_website_name):

    if not isinstance(product_page_url, str):
        return

    chromedriver = "/usr/local/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    # setup driver

    driver = webdriver.Chrome(chromedriver)
    driver.set_window_size(1120, 550)
    driver.set_window_position(-10000,0)

    # setup xpath dict
    xpaths = {
        "all_reviews_button": '//div[@class="pr-snippet-read-reviews"]//a[@class="pr-snippet-link"]',
        "average_rating": '//div[@class="pr-header"]//span[@class="pr-rating pr-rounded average"]',
        "next_page_element": '//a[@data-pr-event="header-page-next-link"]',
        "last_date_element": '//div[@class="pr-contents"]/div/div[@class="pr-review-wrap"][last()]/div[1]/div[1]',
        "all_date_elements": '//div[@class="pr-contents"]/div/div[@class="pr-review-wrap"]/div[1]/div[1]',
        "all_username_elements": '//div[@class="pr-contents"]/div/div[@class="pr-review-wrap"]//div[@class="pr-review-author"]/div[1]/p[1]/span',
        'all_title_elements': '//div[@class="pr-contents"]/div/div[@class="pr-review-wrap"]//div[@class="pr-review-rating-wrapper"]//div[@class="pr-review-rating"]/p',
        "all_rating_elements": '//div[@class="pr-contents"]/div/div[@class="pr-review-wrap"]//div[@class="pr-review-rating-wrapper"]//div[@class="pr-review-rating"]/span',
        "all_review_text_elements": '//div[@class="pr-contents"]/div/div[@class="pr-review-wrap"]/div[@class="pr-review-main-wrapper"]/div[@class="pr-review-text"]/p[@class="pr-comments"]',
        "all_recommendation_elements": '//div[@class="pr-contents"]/div/div[@class="pr-review-wrap"]/div[@class="pr-review-main-wrapper"]/div[@class="pr-review-footer"]',
    }

    # setup regex dict
    regex = {
        "rating": '(.*?) out of 5 stars',
        "date_with_dash": '— ([0-9]+.*?) ago',
        "date_no_dash": '([0-9]+.*?) ago',
        "day": '(.*?) day(?:.*)',
        "month": '(.*?) month(?:.*)',
        "year": '(.*?) year(?:.*)',
        "username": ' (.*?) — (?:[0-9]+?)(?:.*?)ago',
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
            time.sleep(random.randint(2,3))

    # click on all reviews link

    result = click_element(driver,xpaths['all_reviews_button'])
    if result == "Error":
        logger.warn("Did not get all reviews button")
        # product.delete()
        # driver.quit()
        # return

    time.sleep(3)

    # get average rating text

    error_message = "error getting average rating text"
    result = get_element(driver,xpaths['average_rating'],error_message)

    if result == "Error":
        logger.warn('Did not get average rating')
        product.delete()
        driver.quit()
        return
    else:
        try:
            product.average_rating = float(result.strip())
            product.save()
        except:
            logger.warn("Couldn't convert string to float")
            product.delete()
            driver.quit()
            return

    # loop through pages and get data

    date_matches = []
    username_matches = []
    title_matches = []
    rating_matches = []
    review_text_matches = []
    recommend_matches = []

    while True:

        time.sleep(3)

        # get dates
        error_message = "error getting dates"
        results = get_elements(driver,xpaths['all_date_elements'],error_message)

        for date in results:

            date_text = date.text
            date_matches.append(date_text)

        # get usernames

        error_message = "error getting usernames"
        username_results = get_elements(driver,xpaths['all_username_elements'],error_message)

        for username in username_results:

            username_matches.append(username.text)

        # get titles

        error_message = "error getting titles"
        results = get_elements(driver,xpaths['all_title_elements'],error_message)

        if results == "Error" or (len(results) < len(username_results)):
            for username in username_results:
                title_matches.append("Title")
        else:
            for title in results:
                title_matches.append(title.text.strip())

        # get ratings

        error_message = "error getting ratings"
        results = get_elements(driver,xpaths['all_rating_elements'],error_message)

        for rating in results:

            rating_matches.append(rating.text)

        # get review texts

        error_message = "error getting review texts"
        results = get_elements(driver,xpaths['all_review_text_elements'],error_message)

        for review_text in results:

            review_text_matches.append(review_text.text)

        # get recommendation tags

        error_message = "error getting recommendation texts"
        results = get_elements(driver,xpaths['all_recommendation_elements'],error_message)

        logger.warn("Step 1")

        for recommendation_text in results:

            search_text = recommendation_text.text

            would_recommend_text = 'Yes, I would recommend'
            would_not_recommend_text = 'No, I would not recommend'

            if would_recommend_text in search_text:
                recommend_matches.append("would recommend")
            elif would_not_recommend_text in search_text:
                recommend_matches.append("would not recommend")
            else:
                recommend_matches.append("")

        logger.warn("Step 3")

        # check if last date on page is greater than cutoff

        error_message = "error getting dates"
        results = get_elements(driver,xpaths['last_date_element'],error_message)

        if results == "Error":
            last_date_text = datetime.datetime.now().strftime("%m/%d/%Y")
        else:
            last_date_text = results[0].text

        # Convert date

        review_date = datetime.datetime.strptime(last_date_text, "%m/%d/%Y").replace(tzinfo=pytz.UTC)

        if review_date < cutoff_date:
            break
        else:

            # click next

            click_result = click_element_by_hitting_enter(driver,xpaths['next_page_element'])
            if click_result == "Error":
                break

    # quit driver

    driver.quit()

    # Create individual reviews

    index = 0

    logger.warn("Step 4")

    for individual_review_date in date_matches:

        review_text = html.unescape(review_text_matches[index])
        review_text = review_text.replace("<br />","")

        review_date = datetime.datetime.strptime(individual_review_date, "%m/%d/%Y").replace(tzinfo=pytz.UTC)

        review = Review(project=project,product=product,date=review_date,title=title_matches[index],
                        username=str(username_matches[index]).replace(' ','').replace('-',''),review_text=review_text,
                        rating=float(rating_matches[index]),would_recommend=recommend_matches[index],
                        is_from_brand_website="")

        review.save()

        index += 1

    logger.warn("Step 5")

    # Tag recommendation and from brand website fields

    all_reviews = [r for r in Review.objects.filter(project = project, product=product)]

    for review in all_reviews:

        check_date_against_cutoff_date(review, cutoff_date, start_date)

    logger.warn("Step 6")

    calculate_review_stats(project, product)
