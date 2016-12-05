import scrapy

from scrapy import Spider
from itertools import chain


def extract_synopsis(current_movie, paragraph_num):
    """
    Check paragraph for synopsis
    :param current_movie: The current movie
    :param paragraph_num: The current paragraph
    :return: The movie synopsis if present or None
    """
    raw_synopsis_list = current_movie.xpath(
        'p[' + str(paragraph_num) + ']/text()'
    ).extract()

    # Format synopsis if synopsis is present else return None
    return format_synopsis(raw_synopsis_list) if raw_synopsis_list else None


def format_synopsis(synopsis_list):
    """
    Makes sure synopsis is actual movie synopsis and not movie Show Times
    :param synopsis_list: Supposed synopsis. Content found within the paragraph
    :return: Formatted synopsis, striped of non-characters or break out of the function
    """
    raw_synopsis = ''.join(synopsis_list)
    days = ['Mon:', 'Tue:', 'Wed:', 'Thur:', 'Fri:', 'Sat:', 'Sun:',]

    if any(day in raw_synopsis for day in days):

        # Paragraph contains movie Show Time... wrong paragraph! Exit function
        return

    # Remove unicode characters from movie synopsis...
    new_synopsis = ''.join(
        [elem if ord(elem) < 128 else '' for elem in raw_synopsis]
    )

    # Remove whitespace characters (try import string; translate(None, string.whitespace))
    return ' '.join(
        str(new_synopsis).translate(None, '\t\n').split()
    )


