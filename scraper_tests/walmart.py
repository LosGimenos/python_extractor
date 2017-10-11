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

def get_walmart_reviews(headers_list, product_page_url, project, product, start_date, cutoff_date, brand_website_name):

    # setup regex dict
    regex = {
        "average_rating": '<span class="ReviewsHeader-rating"> ([0-9|\.]*?) out of 5 <\/span>',
        "total_review_count": ' ([0-9]*) review(?:.*?)out of 5<\/span>',
        "rating_level_review_count": '<div class="js-rating-filter rating-filter" data-value="rating:eq:1">(?:[\s\S]*?)<span class="(?:.*?)-val">([0-9]*?)<\/span>',
        "num_of_pages": '<a href="#" role="button" class="js-pagination link " data-page="([0-9]*?)"',
        "date": '<span class="Grid-col u-size-2-12-m customer-review-date js-review-date hide-content display-inline-block-m">(.*?)<\/span>',
        "title": '<div class="Grid-col u-size-10-12-m customer-review-title">(.*?)<\/div>',
        "username": '<span class="customer-name-heavy">(?:\s*)(.*?)<\/span>',
        "review_text": '<p class="js-customer-review-text" data-max-height="110">([\s\S]*?)<\/p>',
        "rating": '<div class="stars customer-stars">(?:[\s\S]*?)<span class="visuallyhidden">(.*?) stars<\/span>',
        "additional_info": '<div class="Grid-col u-size-3-12-m customer-info hide-content display-inline-block-m">([\s\S]*?)(?:<div class="Grid-col u-size-8-12-m js-customer-review-body customer-review-body">|<div class="js-review-pagination-bottom">)',
        "brand_website": '<div class="js-review-media-responsive review-media-responsive hide-content">([\s\S]*?)<div class="Grid-col u-size-3-12-m customer-info hide-content display-inline-block-m">',
        "recommendation": '<div>Would recommend to a friend?(?:[\s\S]*?)<span>(.*?)<\/span>',
        "skin_type": '<div>Skin type:<span>(.*?)<\/span>',
        "gender": '<div>Gender:<span>(.*?)<\/span>',
    }

    # Go to main product page

    headers = headers_list[0]

    try:
        page_source = requests.get(product_page_url, headers=headers).text
    except:
        logger.warn('No valid URL')
        return

    logger.warn(page_source)
    matches = re.findall(regex['average_rating'], page_source)
    logger.warn(matches)

    # Average rating

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

    # Review count by rating level

    total_number_reviews = product.total_number_reviews

    # create a loop to abstract star review counts
    for index in range(1, 6):

        rating_to_sub = 'rating:eq:%s' % index
        regex_rating_level_review_count = re.sub(r'rating:eq:1', rating_to_sub, regex['rating_level_review_count'])

        matches = re.findall(regex_rating_level_review_count, page_source)

        if len(matches) == 0:
            logger.warn("No matches - Product - %s star review count" % index)
            continue

        if index == 1:
            product.num_reviews_one_star = int(matches[0])
        elif index == 2:
            product.num_reviews_two_stars= int(matches[0])
        elif index == 3:
            product.num_reviews_three_stars= int(matches[0])
        elif index == 4:
            product.num_reviews_four_stars= int(matches[0])
        elif index == 5:
            product.num_reviews_two_stars= int(matches[0])

        product.save()

    # Number of pages

    matches = re.findall(regex['num_of_pages'], page_source)

    if len(matches) == 0:
        logger.warn("No matches - Product - number of pages")
        number_of_pages = 1
    else:
        number_of_pages = int(matches[len(matches)-1].replace(',',''))
        logger.warn("Number of pages = " + str(number_of_pages))

    # Loop through paginated reviews pages

    for page_number in range(1, (number_of_pages + 1)):

        review_page_url = product_page_url + "?limit=20" + "&page=" + str(page_number) + "&sort=submission-desc"

        if ((page_number % 400) == 0):
            time.sleep(random.randint(300,360))
        time.sleep(random.randint(20,30))

        # header_index = random.randint(0,0)
        # headers = headers_list[header_index]

        page_source = requests.get(review_page_url, headers=random.choice(headers_list)).text

        # dates

        date_matches = re.findall(regex['date'], page_source)

        if len(date_matches) == 0:
            logger.warn("No matches - Reviews - dates")

        # titles

        title_matches = re.findall(regex['title'], page_source)

        if len(title_matches) == 0:
            logger.warn("No matches - Reviews - titles")
            # print(page_source)
            # break

        # usernames

        username_matches = re.findall(regex['username'], page_source)

        if len(username_matches) == 0:
            logger.warn("No matches - Reviews - usernames")
            # print(page_source)
            # break

        # review text

        review_text_matches = re.findall(regex['review_text'], page_source)

        if len(review_text_matches) == 0:
            logger.warn("No matches - Reviews - review text")
            # print(page_source)
            # break

        # ratings

        rating_matches = re.findall(regex['rating'], page_source)

        if len(rating_matches) == 0:
            logger.warn("No matches - Reviews - ratings")
            # print(page_source)
            # break

        # additional info

        additional_info_matches = re.findall(regex['additional_info'], page_source)

        if len(additional_info_matches) == 0:
            logger.warn("No matches - Reviews - additional info")
            # print(page_source)
            # break

        # brand website

        brand_website_matches = re.findall(regex['brand_website'], page_source)

        if len(brand_website_matches) == 0:
            logger.warn("No matches - Reviews - Brand website")
            # print(page_source)
            # break

        # Create individual reviews

        index = 0

        for individual_review_date in date_matches:

            review_text = html.unescape(review_text_matches[index])
            review_text = review_text.replace("<br />","")
            review_date = datetime.datetime.strptime(individual_review_date, "%m/%d/%Y").replace(tzinfo=pytz.UTC)

            if review_date > start_date:
                calculate_review_stats(project, product)
                continue

            if review_date < cutoff_date:
                calculate_review_stats(project, product)
                return

            review = Review(project=project,product=product,date=review_date,title=title_matches[index],
                            username=username_matches[index],review_text=review_text,
                            rating=float(rating_matches[index]))

            review.save()

            # Tag from brand website

            brand_website_text = '<span class="syndication-text">Written by a customer while visiting <span class="font-bold">' + brand_website_name + '.com' + '</span>'
            if brand_website_text in brand_website_matches[index]:
                review.is_from_brand_website = brand_website_name
                review.save()

            # Tag additional info

            additional_info_html = additional_info_matches[index]

            recommendation_matches = re.findall(regex['recommendation'], additional_info_html)
            if len(recommendation_matches) != 0:
                if recommendation_matches[0] == 'Yes':
                    review.would_recommend = 'would recommend'
                    review.save()
                elif recommendation_matches[0] == 'No':
                    review.would_recommend = 'would not recommend'
                    review.save()

            skin_type_matches = re.findall(regex['skin_type'], additional_info_html)
            if len(skin_type_matches) != 0:
                review.skin_type = skin_type_matches[0]
                review.save()

            gender_matches = re.findall(regex['gender'], additional_info_html)
            if len(gender_matches) != 0:
                review.gender = gender_matches[0]
                review.save()

            index += 1

    # # Delete reviews that are out of date range and re-calculate number of reviews
    # for review in Review.objects.filter(project=project,product=product):
    #     if review.date < cutoff_date:
    #         review.delete()

    calculate_review_stats(project, product)
