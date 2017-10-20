import re
import requests
from .models import Project, Product, Review, ProductPageUrl
import html
import datetime
import pytz
import logging
import time
import random

from .helpers import *

logger = logging.getLogger(__name__)

def get_amazon_reviews(headers_list, product_page_url, project, product, start_date, cutoff_date, brand_website_name):

    # setup regex dict
    regex = {
        "average_rating": '<i data-hook="average-star-rating"(?:.*?)a-icon-alt">(.*?) out of 5 stars',
        "total_review_count": 'totalReviewCount">(.*?)<\/span>',
        "rating_level_review_count": '<div class="a-meter 1star" aria-label="([0-9]*?)%"',
        "number_of_pages": '>([0-9]*?)<\/a><\/li><li class="a-last">',
        "url": 'class="a-size-base a-link-normal review-title a-color-base a-text-bold" href="([^\s]*?)"',
        "date": '<span data-hook="review-date" class="a-size-base a-color-secondary review-date">on (.*?)<\/span>',
        "title": '<a data-hook="review-title" class="a-size-base a-link-normal review-title a-color-base a-text-bold" href="(?:.*?)">(.*?)<\/a><\/div>',
        "username": '<div class="a-row"><span data-hook="review-author" class="a-size-base a-color-secondary review-byline"><span class="a-color-secondary">By<\/span><span class="a-letter-space"><\/span><a data-hook="review-author" class="a-size-base a-link-normal author" href="(?:.*?)">(.*?)<\/a>',
        "review_text": 'div class="a-row review-data"><span data-hook="review-body" class="a-size-base review-text">(.*?)<\/span><\/div>',
        "rating": '<i data-hook="review-star-rating"(?:.*?)a-icon-alt">(.*?) out of 5 stars',
        "num_comments": '<span class="review-comment-total aok-hidden">(.*?)<\/span>',
    }

    # Go to main product page

    headers = headers_list[0]

    try:
        page_source = requests.get(product_page_url, headers=headers).text
        logger.warn('Got primary page source')
    except:
        logger.warn('No valid URL')
        return

    # Average rating

    matches = re.findall(regex['average_rating'], page_source)

    if len(matches) == 0:
        logger.warn("No matches - Product - average rating")
    else:
        product.average_rating = float(matches[0])
        product.save()
        logger.warn(matches[0])

    # Total review count

    matches = re.findall(regex['total_review_count'], page_source)

    if len(matches) == 0:
        logger.warn("No matches - Product - total review count")
    else:
        product.total_number_reviews = int(matches[0].replace(',',''))
        product.save()
        logger.warn(matches[0])

    total_number_reviews = product.total_number_reviews


    # Review count by rating level

    for index in range(1, 6):

        rating_to_sub = 'a-meter %sstar' % index
        regex_rating_level_review_count = re.sub(r'a-meter 1star', rating_to_sub, regex['rating_level_review_count'])

        matches = re.findall(regex_rating_level_review_count, page_source)

        if len(matches) == 0:
            logger.warn("No matches - Product - %s star review count" % index)
            continue

        if index == 1:
            product.num_reviews_one_star = int(round((int(matches[0]) / 100) * total_number_reviews))
        elif index == 2:
            product.num_reviews_two_stars = int(round((int(matches[0]) / 100) * total_number_reviews))
        elif index == 3:
            product.num_reviews_three_stars = int(round((int(matches[0]) / 100) * total_number_reviews))
        elif index == 4:
            product.num_reviews_four_stars = int(round((int(matches[0]) / 100) * total_number_reviews))
        elif index == 5:
            product.num_reviews_five_stars = int(round((int(matches[0]) / 100) * total_number_reviews))

        product.save()

    # Number of pages

    matches = re.findall(regex['number_of_pages'], page_source)

    if len(matches) == 0:
        logger.warn("No matches - Product - number of pages")
        number_of_pages = 1
    else:
        number_of_pages = int(matches[0].replace(',',''))
        logger.warn("Number of pages = " + str(number_of_pages))

    # Loop through paginated reviews pages

    for page_number in range(1, (number_of_pages + 1)):

        review_page_url = product_page_url + "&pageNumber=" + str(page_number)

        if ((page_number % 400) == 0):
            logger.warn('Large page volume. In wait...')
            time.sleep(random.randint(300,360))
            logger.warn('...wait over')

        time.sleep(random.randint(20,30))

        # header_index = random.randint(0,0)
        # headers = headers_list[header_index]

        page_source = requests.get(review_page_url, headers=random.choice(headers_list)).text
        print('Getting elements in page number ', page_number, 'out of ', number_of_pages)
        # urls

        matches = re.findall(regex['url'], page_source)

        if len(matches) == 0:
            logger.warn("No matches - Reviews - urls")
            print(page_source)
            break
        else:

            # dates

            date_matches = re.findall(regex['date'], page_source)

            if len(date_matches) == 0:
                logger.warn("No matches - Reviews - dates")
                print(page_source)
                break

            # titles

            title_matches = re.findall(regex['title'], page_source)

            if len(title_matches) == 0:
                logger.warn("No matches - Reviews - titles")
                print(page_source)
                break

            # usernames

            username_matches = re.findall(regex['username'], page_source)

            if len(username_matches) == 0:
                logger.warn("No matches - Reviews - usernames")
                print(page_source)
                break

            # review text

            review_text_matches = re.findall(regex['review_text'], page_source)

            if len(review_text_matches) == 0:
                logger.warn("No matches - Reviews - review text")
                print(page_source)
                break

            # ratings

            rating_matches = re.findall(regex['rating'], page_source)

            if len(rating_matches) == 0:
                logger.warn("No matches - Reviews - ratings")
                print(page_source)
                break

            # num comments

            num_comment_matches = re.findall(regex['num_comments'], page_source)

            if len(num_comment_matches) == 0:
                logger.warn("No matches - Reviews - num comments")
                print(page_source)
                break

            # Create individual reviews

            index = 0

            for individual_review_url in matches:

                review_url = 'https://www.amazon.com' + individual_review_url
                review_text = html.unescape(review_text_matches[index])
                review_text = review_text.replace("<br />","")
                review_date = datetime.datetime.strptime(date_matches[index], "%B %d, %Y").replace(tzinfo=pytz.UTC)

                if review_date > start_date:
                    calculate_review_stats(project, product)
                    index += 1
                    continue

                if review_date < cutoff_date:
                    calculate_review_stats(project, product)
                    logger.warn('less than cutoff')
                    return

                review = Review(project=project,product=product,url=review_url,date=review_date,title=title_matches[index],
                                username=username_matches[index],review_text=review_text,
                                rating=float(rating_matches[index]), num_comments=int(num_comment_matches[index]))

                review.save()

                index += 1
