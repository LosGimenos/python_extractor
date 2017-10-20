import re
import requests
from .models import Project, Product, Review, ProductPageUrl
import html
import datetime
import pytz
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import random
import os

from .helpers import *

logger = logging.getLogger(__name__)

def get_walgreens_reviews_js(headers_list,product_page_url, project, product, start_date, cutoff_date, brand_website_name):

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
        "all_reviews_button": '//span[@itemprop="reviewCount"]//a[@class="bv-rating-label bv-text-link bv-focusable"]',
        "average_rating": '//span[@class="bv-secondary-rating-summary-rating"]',
        "last_date_element": '//*[@id="BVRRContainer"]/div/div/div/div/ol/li[last()]/div/div[1]/div/div[1]/div[2]/div[1]/div/div/div/div/span[2]',
        "shown_load_more_reviews_button": '//button[@class="bv-content-btn bv-content-btn-pages bv-content-btn-pages-load-more bv-focusable"]',
        "all_date_elements": '//*[@id="BVRRContainer"]/div/div/div/div/ol/li/div/div[1]/div/div[1]/div[2]/div[1]/div/div/div/div/span[2]',
        "all_username_elements": '//*[@id="BVRRContainer"]/div/div/div/div/ol/li/div/div[1]/div/div[1]/div[2]/div[1]/div/div/div/span',
        'all_title_elements': '//li[@class="bv-content-item bv-content-top-review bv-content-review"]//div[@class="bv-content-title-container"]//h4[@class="bv-content-title"]',
        "all_rating_elements": '//li[@class="bv-content-item bv-content-top-review bv-content-review"]//span[@class="bv-rating-stars-container"]//span[@class="bv-off-screen"]',
        "all_review_text_elements": '//*[@id="BVRRContainer"]/div/div/div/div/ol/li/div/div[1]/div/div[2]/div/div/div[1]',
        "all_is_from_brand_elements": '//*[@id="BVRRContainer"]/div/div/div/div/ol/li/div/div[1]/div/div[2]/div/div/div[2]',
    }

    # setup regex dict
    regex = {
        "rating": '(.*?) out of 5 stars',
        "date_no_dash": '([0-9]+.*?) ago',
        "hours": '(.*?) hour(?:.*)',
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
            time.sleep(random.randint(2,5))

    # click on all reviews link

    result = click_element(driver,xpaths["all_reviews_button"])

    if result == "Error":
        logger.warn("No reviews exist")
        calculate_review_stats(project, product)
        driver.quit()
        return

    time.sleep(3)

    # get average rating text

    error_message = "error getting average rating text"
    result = get_element(driver,xpaths["average_rating"],error_message)

    if result == "Error":
        logger.warn("Did not find average rating")
    else:
        try:
            product.average_rating = float(result.strip())
            product.save()
            logger.warn(result.strip())
        except:
            logger.warn("Couldn't convert string to float")
            logger.warn(result.strip())
            product.delete()
            driver.quit()
            return

    # select filter dropdown value

    time.sleep(random.randint(3, 6))

    try:
        select = Select(driver.find_element_by_id('bv-dropdown-select-1'))
        select.select_by_value('mostRecent')
        logger.warn('selected most recent')
    except:
        logger.warn("Couldn't select dropdown filter")

    # expand list

    visible_more_reviews_button = True
    y_coord_offset = 0

    while visible_more_reviews_button:

        time.sleep(random.randint(3, 6))

        try:
            more_reviews_button = driver.find_element_by_class_name('bv-content-btn-pages-load-more')
            print(more_reviews_button)

            more_reviews_button_location = more_reviews_button.location_once_scrolled_into_view
            print(more_reviews_button_location)
            y_coord = more_reviews_button_location['y'] + (y_coord_offset - 200)
            y_coord_offset = y_coord
            print(y_coord)

            driver.execute_script("window.scrollTo(0," + str(y_coord) + ");")

            more_reviews_button = click_element(driver, xpaths["shown_load_more_reviews_button"])
            logger.warn('Clicked load more')
        except:
            logger.warn('No load more reviews button')
            visible_more_reviews_button = False

    while True:

        time.sleep(3)

        # check if last date on page is greater than cutoff

        error_message = "error getting dates"
        results = get_elements(driver,xpaths["last_date_element"],error_message)

        if results == "Error":
            last_date_text = "1 day ago"
        else:
            last_date_text = results[0].text

        if last_date_text.find('hour') > 0:
            last_date_text = "1 day ago"

        individual_review_date = convert_date_a_to_one(regex['date_no_dash'], last_date_text)

        # check what this date looks like
        logger.warn(individual_review_date)

        # Convert date

        review_date = convert_date_to_datetime(regex['day'], regex['month'], regex['year'], individual_review_date)

        if review_date < cutoff_date:
            break
        else:

            # expand list

            click_result = click_element(driver,xpaths['shown_load_more_reviews_button'])
            if click_result == "Error":
                break


    # get dates
    error_message = "error getting dates"
    results = get_elements(driver,xpaths['all_date_elements'],error_message)

    if results == 'Error':
        logger.warn('No dates. No valid reviews')
        return

    date_matches = []

    for date in results:
        date_text = date.text

        date_regex_matches = re.findall(regex['date_no_dash'], date_text)

        if len(date_regex_matches) == 0:
            regex_date = 'a year ago'
            date_regex_matches = re.findall(regex_date, date_text)
            if len(date_regex_matches) == 0:
                regex_date = 'a month ago'
                date_regex_matches = re.findall(regex_date, date_text)
                if len(date_regex_matches) == 0:
                    regex_date = 'a day ago'
                    date_regex_matches = re.findall(regex_date, date_text)
                    if len(date_regex_matches) == 0:
                        logger.warn("No matches - date")
                    else:
                        date_matches.append("1 day ago")
                else:
                    date_matches.append("1 month ago")
            else:
                date_matches.append("1 year ago")
        else:
            date_matches.append(date_regex_matches[0])

    # get usernames

    error_message = "error getting usernames"
    results = get_elements(driver,xpaths['all_username_elements'],error_message)

    username_matches = []

    for username in results:
        username_matches.append(username.text)

    # get titles

    error_message = "error getting titles"
    results = get_elements(driver,xpaths['all_title_elements'],error_message)

    if results == "Error" or (len(results) < len(username_matches)):
        title_matches = username_matches
    else:
        title_matches = []
        for title in results:
            title_matches.append(title.text.strip())

    # get ratings

    error_message = "error getting ratings"
    results = get_elements(driver,xpaths['all_rating_elements'],error_message)

    rating_matches = []

    for rating in results:
        rating_regex_matches = re.findall(regex['rating'], rating.text)

        if len(rating_regex_matches) == 0:
            logger.warn("No matches - Reviews - ratings")
            rating_matches.append("")
        else:
            rating_matches.append(rating_regex_matches[0])

    # get review texts

    error_message = "error getting review texts"
    results = get_elements(driver,xpaths['all_review_text_elements'],error_message)

    review_text_matches = []

    for review_text in results:
        cleaned_text = review_text.text
        cleaned_text = cleaned_text.replace("<p>","")
        cleaned_text = cleaned_text.replace("</p>","")
        review_text_matches.append(cleaned_text)

    # possibly run brand and get recommendation on the same loop
    # get is from brand texts
    # get recommendation tags

    error_message = "error getting is from brand texts"
    results = get_elements(driver,xpaths['all_is_from_brand_elements'],error_message)

    logger.warn("Step 1")
    logger.warn("Step 2")

    is_from_brand_matches = []
    recommend_matches = []

    for is_from_brand_text in results:

        syndicated_text = 'Originally posted on'
        search_text = is_from_brand_text.text

        if syndicated_text in search_text:
            is_from_brand_matches.append(brand_website_name)
        else:
            logger.warn("No matches - is from brand")
            is_from_brand_matches.append("")

        would_recommend_text = 'I recommend this product'
        would_not_recommend_text = 'I do not recommend this product'

        if would_recommend_text in search_text:
            recommend_matches.append("would recommend")
        elif would_not_recommend_text in search_text:
            recommend_matches.append("would not recommend")
        else:
            recommend_matches.append("")


    # for is_from_brand_text in results:
    #
    #     search_text = is_from_brand_text.text


    logger.warn("Step 3")

    # quit driver

    driver.quit()

    # Create individual reviews

    index = 0

    logger.warn("Step 4")

    for individual_review_date in date_matches:

        review_text = html.unescape(review_text_matches[index])
        review_text = review_text.replace("<br />","")

        # Convert date

        review_date = convert_date_to_datetime(regex['day'], regex['month'], regex['year'], individual_review_date)

        review = Review(project=project,product=product,date=review_date,title=title_matches[index],
                        username=str(username_matches[index]).replace(' ','').replace('-',''),review_text=review_text,
                        rating=float(rating_matches[index]),would_recommend=recommend_matches[index],
                        is_from_brand_website=is_from_brand_matches[index])

        review.save()
        logger.warn(individual_review_date)

        index += 1

    logger.warn("Step 5")

    all_reviews = [r for r in Review.objects.filter(project = project, product=product)]

    for review in all_reviews:

        check_date_against_cutoff_date(review, cutoff_date, start_date)

    logger.warn("Step 6")

    # Re-calculate number of reviews

    calculate_review_stats(project, product)
