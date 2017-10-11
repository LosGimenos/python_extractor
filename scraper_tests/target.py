import re
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

def get_target_reviews_js(headers_list, product_page_url, project, product, start_date, cutoff_date, brand_website_name):

    chromedriver = "/usr/local/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    # setup driver

    driver = webdriver.Chrome(chromedriver)
    driver.set_window_size(1120, 550)
    driver.set_window_position(-10000,0)

    # setup xpath dict
    xpaths = {
        "all_reviews_button": '//*[@class="link-grayDark link-underline guestRating--total js-reviews-showAllReviews"]',
        "home_more_reviews_button": '//*[@id="bvTag-reviewsSummary"]/div/div/div[3]/div/div/button[1]',
        "home_all_rating_elements": '//*[@id="bvTag-reviewsSummary"]//span[@class="h-sr-only h-inlineWrap"]',
        "home_total_reviews_count": '//*[@id="bvTag-reviewsSummary"]/div/div/div[1]/div/div/div/div[1]/span[1]',
        "home_all_date_elements": '//*[@id="bvTag-reviewsSummary"]//div[@class="h-display-inline-block h-text-grayDark h-text-sm"]',
        "home_all_title_elements": '//*[@id="bvTag-reviewsSummary"]//div[@class="js-reviews-reviewRow"]',
        "home_expand_review_button": '//*[@id="bvTag-reviewsSummary"]//div[@class="js-reviews-reviewRow"]//span[@class="h-inlineWrap"]',
        "home_all_review_text_elements": '//div[@class="js-reviews-reviewRow"]//div[@class="h-display-inline js-reviews-reviewText"]',
        "home_all_is_from_brand_elements": '//*[@id="bvTag-reviewsSummary"]//div[contains(@class,"h-standardSpacingBottom js-reviews-review")]',
        "average_rating": '//*[@id="bvTag-allReviews"]/div[3]/div/div[2]/div/div/div/div/div/span',
        "total_reviews_count": '//*[@id="bvTag-allReviews"]/div[3]/div/div[1]/div[1]/div/span',
        "dropdown_menu_element": '//*[@id="sortAndFilterReviewsRow"]/div[1]/div/div/button',
        "dropdown_value_element": '//*[@id="sortAndFilterReviewsRow"]/div[1]/div/div/ul/li[2]/a',
        "last_date_element": '//div[@class="reviews--reviewList js-reviews-reviewList"]/div[last()]//div[@class="h-display-inline-block h-text-grayDark h-text-sm"]',
        "hidden_load_more_reviews_button": '//button[@class="btn btn-default btn-block js-reviews-loadMoreReviews is-hidden"]',
        "shown_load_more_reviews_button": '//button[@class="btn btn-default btn-block js-reviews-loadMoreReviews"]',
        "all_date_elements": '//div[@class="reviews--reviewList js-reviews-reviewList"]//div[@class="h-display-inline-block h-text-grayDark h-text-sm"]',
        'all_title_elements': '//div[contains(@class, "reviews--reviewList js-reviews-reviewList")]//div[@class="js-reviews-reviewRow"]',
        "all_rating_elements": '//div[contains(@class, "js-reviews-reviewList")]//div[@class="ratings-score"]//span[@class="h-sr-only h-inlineWrap"]',
        "expand_review_button": '//div[@class="reviews--reviewList js-reviews-reviewList"]//div[@class="js-reviews-reviewRow"]//a[@class="link-underline xh-inlineWrap js-reviews-showExpandedReview"]',
        "all_review_text_elements": '//div[contains(@class, "reviews--reviewList js-reviews-reviewList")]//div[@class="js-reviews-reviewRow"]//div[@class="h-display-inline js-reviews-reviewText"]',
        "all_is_from_brand_elements": '//div[contains(@class, "reviews--reviewList js-reviews-reviewList")]//div[contains(@class,"h-standardSpacingBottom js-reviews-review")]',
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
            time.sleep(random.randint(2,5))

    # click on all reviews link

    result = click_element(driver,xpaths["all_reviews_button"])

    if result == "Error":
        print("Couldn't click all reviews link")

        no_visible_reviews = False
        click_element(driver, xpaths["home_more_reviews_button"])

        try:
            error_message = "error getting average rating text"
            ratings_result = get_elements(driver, xpaths["home_all_rating_elements"], error_message)

            if len(ratings_result) < 2:
                no_visible_reviews = True

            average_rating_result = ratings_result.pop(0)
        except:
            logger.warn('No reviews exist')
            calculate_review_stats(project, product)
            driver.quit()
            return

        matches = re.findall(regex["rating"], average_rating_result.text)

        if len(matches) == 0:
            logger.warn("No matches - Product - average rating")
        else:
            product.average_rating = float(matches[0])
            product.save()
            logger.warn(matches[0])

        error_message = "error getting total review count"
        result = get_element(driver, xpaths["home_total_reviews_count"], error_message)

        if result == 'Error':
            number_attempts = 0
            while num_attempts < 10 and result == 'Error':
                result = get_element(driver, xpaths["home_total_reviews_count"], error_message)
                number_attempts += 1

        logger.warn(result + ' reviews')
        product.total_number_reviews = int(result)
        product.save()

        if no_visible_reviews:
            logger.warn('No reviews exist')
            calculate_review_stats(project, product)
            driver.quit()
            return

        error_message = "error getting dates"
        results = get_elements(driver, xpaths["home_all_date_elements"], error_message)

        date_matches = []
        username_matches = []

        for date in results:
            date_regex_matches = re.findall(regex['date_with_dash'], date.text)

            if len(date_regex_matches) == 0:
                date_regex_matches = re.findall(regex['date_no_dash'], date.text)
                if len(date_regex_matches) == 0:
                    logger.warn("No matches - Reviews - dates")
                else:
                    date_matches.append(date_regex_matches[0])
            else:
                date_matches.append(date_regex_matches[0])

            username_regex_matches = re.findall(regex["username"], date.text)

            if len(username_regex_matches) == 0:
                logger.warn("No matches - Reviews - usernames")
                username_matches.append("")
            else:
                username_matches.append(username_regex_matches[0])

        # get titles

        error_message = "error getting titles"
        results = get_elements(driver, xpaths["home_all_title_elements"], error_message)

        title_matches = []

        for title_container in results:
            title = title_container.find_elements_by_tag_name("h4")
            if len(title) > 0:
                title_matches.append(title[0].text)
            else:
                title_matches.append("")

        # get ratings

        error_message = "error getting ratings"

        rating_matches = []

        for rating in ratings_result:
            rating_regex_matches = re.findall(regex["rating"], rating.text)

            if len(rating_regex_matches) == 0:
                logger.warn("No matches - Reviews - ratings")
            else:
                rating_matches.append(rating_regex_matches[0])

        # expand and get review texts

        click_elements(driver, xpaths["home_expand_review_button"])

        error_message = "error getting review texts"
        results = get_elements(driver, xpaths["home_all_review_text_elements"], error_message)

        review_text_matches = []

        for review_text in results:
            review_text_matches.append(review_text.text)

        # get is from brand texts

        error_message = "error getting is from brand texts"
        results = get_elements(driver, xpaths["home_all_is_from_brand_elements"], error_message)

        is_from_brand_matches = []

        for is_from_brand_text in results:
            syndicated_tag = 'originally posted on '
            if syndicated_tag in is_from_brand_text.text:
                is_from_brand_matches.append(brand_website_name)
            else:
                is_from_brand_matches.append("")

        # quit driver

        driver.quit()

    else:
        # get average rating text

        error_message = "error getting average rating text"
        result = get_element(driver,xpaths["average_rating"],error_message)

        if result == 'Error':
            number_attempts = 0
            while num_attempts < 10 and result == 'Error':
                result = get_element(driver, xpaths["total_reviews_count"], error_message)
                number_attempts += 1

        time.sleep(2)

        matches = re.findall(regex['rating'], result)

        if len(matches) == 0:
            logger.warn("No matches - Product - average rating")
        else:
            product.average_rating = float(matches[0])
            product.save()
            logger.warn(matches[0])

        # get total review count

        error_message = "error getting total review count"
        result = get_element(driver,xpaths["total_reviews_count"],error_message)

        if result == 'Error':
            number_attempts = 0
            while num_attempts < 10 and result == 'Error':
                result = get_element(driver, xpaths["total_reviews_count"], error_message)
                number_attempts += 1

        logger.warn(result + ' reviews')
        product.total_number_reviews = int(result)

        # click on sort by dropdown

        click_element(driver,xpaths["dropdown_menu_element"])

        # select most recent dropdown value

        click_element(driver,xpaths["dropdown_value_element"])

        time.sleep(2)

        # expand list

        while True:

            # check if last date on page is greater than cutoff

            error_message = "error getting dates"
            results = get_elements(driver,xpaths["last_date_element"],error_message)

            last_date_text = results[0].text

            date_regex_matches = re.findall(regex['date_with_dash'], last_date_text)

            if len(date_regex_matches) == 0:
                date_regex_matches = re.findall(regex["date_no_dash"], last_date_text)
                if len(date_regex_matches) == 0:
                    logger.warn("No matches - Reviews - last date")

            individual_review_date = date_regex_matches[0]

            # Convert date

            review_date = convert_date_to_datetime(regex["day"], regex["month"], regex["year"], individual_review_date)

            if review_date < cutoff_date:
                break
            else:

                # expand list

                error_message = "error getting hidden load more reviews button"
                result = get_element(driver,xpaths["hidden_load_more_reviews_button"],error_message)
                if result == "Error":
                    click_result = click_element(driver,xpaths["shown_load_more_reviews_button"])
                    if click_result == "Error":
                        break
                else:
                    break

        # get dates

        error_message = "error getting dates"
        results = get_elements(driver,xpaths["all_date_elements"],error_message)

        date_matches = []
        username_matches = []

        for date in results:
            date_regex_matches = re.findall(regex['date_with_dash'], date.text)

            if len(date_regex_matches) == 0:
                date_regex_matches = re.findall(regex['date_no_dash'], date.text)
                if len(date_regex_matches) == 0:
                    logger.warn("No matches - Reviews - dates")
                else:
                    date_matches.append(date_regex_matches[0])
            else:
                date_matches.append(date_regex_matches[0])

            username_regex_matches = re.findall(regex["username"], date.text)

            if len(username_regex_matches) == 0:
                logger.warn("No matches - Reviews - usernames")
                username_matches.append("")
            else:
                username_matches.append(username_regex_matches[0])

        # get titles

        error_message = "error getting titles"
        results = get_elements(driver,xpaths["all_title_elements"],error_message)

        title_matches = []

        for title_container in results:
            title = title_container.find_elements_by_tag_name("h4")
            if len(title) > 0:
                title_matches.append(title[0].text)
            else:
                title_matches.append("")

        # get ratings

        error_message = "error getting ratings"
        results = get_elements(driver,xpaths["all_rating_elements"],error_message)

        rating_matches = []

        for rating in results:
            rating_regex_matches = re.findall(regex["rating"], rating.text)

            if len(rating_regex_matches) == 0:
                logger.warn("No matches - Reviews - ratings")
            else:
                rating_matches.append(rating_regex_matches[0])

        # expand and get review texts

        max_attempts = 0
        while max_attempts <= 5:
            error_message = "error getting see more links"
            result = get_elements(driver,xpaths["expand_review_button"],error_message)
            if result != "Error":
                for link in result:
                    num_attempts = 0
                    while True:
                        num_attempts += 1
                        if link.is_displayed():
                            link.click()
                            print("clicked link")
                            break
                        else:
                            print("link not visible")
                            if num_attempts > 5:
                                break
                print("Clicked see more links")
                break
            else:
                print("Didn't click see more links")
                max_attempts += 1

        error_message = "error getting review texts"
        results = get_elements(driver,xpaths["all_review_text_elements"],error_message)

        review_text_matches = []

        for review_text in results:
            review_text_matches.append(review_text.text)

        # get is from brand texts

        error_message = "error getting is from brand texts"
        results = get_elements(driver,xpaths["all_is_from_brand_elements"],error_message)

        is_from_brand_matches = []

        for is_from_brand_text in results:
            syndicated_tag = 'originally posted on '
            if syndicated_tag in is_from_brand_text.text:
                is_from_brand_matches.append(brand_website_name)
            else:
                is_from_brand_matches.append("")

        # quit driver

        driver.quit()

    # Create individual reviews

    index = 0

    for individual_review_date in date_matches:

        review_text = html.unescape(review_text_matches[index])
        review_text = review_text.replace("<br />","")

        # Convert date

        review_date = convert_date_to_datetime(regex["day"], regex["month"], regex["year"], individual_review_date)

        review = Review(project=project,product=product,date=review_date,title=title_matches[index],
                        username=str(username_matches[index]).replace(' ','').replace('-',''),review_text=review_text,
                        rating=float(rating_matches[index]),is_from_brand_website=is_from_brand_matches[index])

        review.save()

        index += 1

    # Tag recommendation and from brand website fields

    all_reviews = [r for r in Review.objects.filter(project = project, product=product)]

    for review in all_reviews:

        if 'would not recommend' in review.title:
            review.would_recommend = 'would not recommend'
            review.save()
        elif 'would recommend' in review.title:
            review.would_recommend = 'would recommend'
            review.save()

        # Delete reviews that are out of date range
        check_date_against_cutoff_date(review, cutoff_date, start_date)

    # Re-calculate number of reviews

    calculate_review_stats(project, product)
