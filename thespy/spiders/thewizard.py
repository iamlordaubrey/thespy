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


class OzSpy(Spider):
    name = 'ozonecinemas'
    allowed_domains = ['ozonecinemas.com',]
    start_urls = ['http://ozonecinemas.com/now_showing.htm',]

    def parse(self, response):
        raw_data = response.xpath("//td[@id='content-area']/table//table//td")

        # Extract and assign relevant data to the movies list
        movies_tuples = zip(raw_data[2:-2:3], raw_data[3:-2:3])
        movies = list(chain(*movies_tuples))
        base_url = 'http://ozonecinemas.com/'

        for movie in movies:
            item = ThespyItem()

            # Movie Image
            rel = movie.xpath('img/@src').extract()
            if rel:
                image_url = [base_url + ' '.join(str(rel[0]).split())]
                item['image_urls'] = image_url

            # Movie Title
            raw_title = movie.xpath('p/strong/text()').extract()
            if raw_title:
                m_title = ' '.join(str(raw_title[0]).split())
                item['title'] = m_title

            # Movie Starring
            l_starring = movie.xpath('p/strong/text()').extract()
            print('l_starring', l_starring, 'l_starring')
            r_starring = movie.xpath('p/strong[2]/following-sibling::text()[1]').extract()

            if l_starring and r_starring:
                l = [x.strip() for x in r_starring[0].split(',')]

                actors = []
                for j in l:
                    j = ''.join([k if ord(k) < 128 else '' for k in j])
                    actors.append(' '.join(str(j).split()))

                actors = ', '.join(actors)
                item['starring'] = actors

            # Movie Show times
            show_times = movie.xpath("p[text()][contains(., 'Mon:') or "
                                     "contains(., 'Tue:') or"
                                     "contains(., 'Wed:') or "
                                     "contains(., 'Thur:') or "
                                     "contains(., 'Fri:') or "
                                     "contains(., 'Sat:') or "
                                     "contains(., 'Sun:')]").extract()

            if show_times:
                lst_times = []
                for i in show_times:
                    lst_times.append(
                        ' '.join(str(i).replace('&amp;', '&').strip('</p>').translate(
                            None, '\t\n'
                        ).split())
                    )

                item['show_times'] = ''.join(lst_times)

            # Movie Synopsis
            movie_synopsis = []

            # Loop through paragraphs 6-10 searching for movie synopsis
            for i in range(6, 10):
                formatted_synopsis = extract_synopsis(movie, i)
                if formatted_synopsis:
                    movie_synopsis.append(formatted_synopsis)
                    break

            if movie_synopsis:
                item['synopsis'] = ''.join(movie_synopsis)

            yield item
