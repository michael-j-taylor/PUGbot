cimport cfscrape
import requests
import re
from bs4 import BeautifulSoup

class EseaProfile:

    def __init__(self):
        self.profile_info = None


class EseaScraper:

    def __init__(self):
        self.requests_flare = cfscrape.create_scraper()
        self.info2 = {
            'profileTab': {
                'alias': '',
                'karma': '',
                'rank': '',
                'status': '',
                'views': '',
                'buddies': []
            },
            'recordTab': {
                'moneySpent': '',
                'consecWins': '',
                'highestRank': '',
                'highestADR': '',
                'highestRWS': '',
                'bestMap': '',
                'worstMap': '',
                'PRW': '',
                'CWR': ''
            },
            'statsTab': {

            },
            'historyTab': {

            }
        }
        self.info = {  # TODO: find a better way to store scraped data
            'header': '',
            'profileTab': {
                'profile': {},
                'buddies': {
                    'li': [],
                    'formatted': ''
                },
                'matches': {
                    'current': {},
                    'past': {}
                }
            },
            'statsTab': {},
            'historyTab': {}
        }
        self.single_keys = ('alias', 'rank', 'name', 'personal', 'status', 'karma', 'views', 'buddies')

    def country_conversion(self, country):
        """
        convert esea country to discord country flag emoji
        ex: 'US' -> : ':flag_us:'
        :param country: ESEA country abbrev to convert
        :return:
        """
        pass


    def get_profile_info(self, profile_info_soup, url):

        info = profile_info_soup.find_all('section')[12].get_text()
        # the text here is filled with weird spacing and a ton of tab and newline characters
        # so I ended up doing some formatting things in order to be able to read it easily
        # it's still not perfect but it works for now

        info = re.sub(r'[\n\t\r]', ' ', info)  # remove \n \t and \r characters from the string
        info_li = re.split(r'\s{2,}', info)  # split when there are at least 2 empty strings between words

        self.info['profileTab']['profile'] = dict()

        self.info['profileTab']['profile']['profile_url'] = url
        self.info['profileTab']['profile']['alias'] = info_li[1]
        self.info['profileTab']['profile']['personal_str'] = info_li[6]  # age / sex / location
        self.info['profileTab']['profile']['status'] = info_li[2][2:]
        self.info['profileTab']['profile']['name'] = info_li[4]
        self.info['profileTab']['profile']['karma'] = info_li[5][:-6]
        self.info['profileTab']['profile']['views'] = info_li[13]
        self.info['profileTab']['profile']['rank'] = profile_info_soup.find('div', id='rankGraph').h1.get_text()

        # create 'header' string from data
        self.info['header'] = '**{}**: **{}**\n' \
            '*{}*\n' \
            '-------------------------\n'.format(self.info['profileTab']['profile']['alias'], self.info['profileTab']['profile']['profile_url'], self.info['profileTab']['profile']['status'])

        # create formatted string containing all info from profile tab
        self.info['profileTab']['profile']['formatted'] = '{}\n' \
            '{}\n' \
            '{}\n' \
            '{}\n' \
            '-------------------------\n'.format(
                self.info['profileTab']['profile']['personal_str'],
                '*Rank*: ' + self.info['profileTab']['profile']['rank'],
                '*Name*: ' + self.info['profileTab']['profile']['name'],
                '*Karma*: ' + self.info['profileTab']['profile']['karma'],
                '*Profile views*: ' + self.info['profileTab']['profile']['views'])

        # create dict containing each individual piece of information from profile tab
        self.info['single_request'] = dict()
        for k, v in self.info['profileTab']['profile'].items():
            self.info['single_request'][k] = v


    def get_buddies(self, buddies_script_text):
        # TODO: I'm not getting online buddies

        # There's gotta be a much better way to do this
        id_li = re.findall(r'"id":"(.*?)"', buddies_script_text)
        alias_li = re.findall(r'"alias":"(.*?)"', buddies_script_text)
        country_li = re.findall(r'"country":"(.*?)"', buddies_script_text)

        self.info['profileTab']['buddies']['li'] = []

        for i, item in enumerate(alias_li):
            info_dict = dict()
            info_dict['id'] = id_li[i]
            info_dict['alias'] = alias_li[i]
            info_dict['country'] = country_li[i]
            self.info['profileTab']['buddies']['li'].append(info_dict)

        buddy_str = '***Buddies:***\n'

        for i in self.info['profileTab']['buddies']['li']:
            buddy_str += '{} - **https://play.esea.net/users/{}**\n'.format(i['alias'], i['id'])

        buddy_str += '-------------------------\n'

        self.info['profileTab']['buddies']['formatted'] = buddy_str
        self.info['single_request']['buddies'] = buddy_str


    def get_profile_url(self, esea_username):
        """
        :param esea_username: pretty self-explanatory
        :return: the corresponding profile url or None if it isn't found or does not exist
        """
        esea_username = esea_username.lower()

        url = 'https://play.esea.net/index.php?s=search&source=users&query=' + esea_username
        page = self.requests_flare.get(url)
        soup = BeautifulSoup(page.content, 'html5lib')

        result_anchors = soup.find_all('a', {'class': 'result', 'href': True})

        for result_anchor in result_anchors:
            result_profile = result_anchor.contents[0].split()
            for name in result_profile:
                if name[0] and name[-1] == "\"":
                    if name.strip("\"").lower() == esea_username:
                        profile_link = 'https://play.esea.net' + result_anchor['href']
                        return profile_link

        return None

    
    def scrape_profile(self, url):
        if url is None:
            print('User not found or does not exist.')

        page = self.requests_flare.get(url)
        soup = BeautifulSoup(page.content, 'html5lib')
        print(soup.prettify())

        profile_info = soup.find('div', id="layout-container")
        self.get_profile_info(profile_info, url)

        buddies = profile_info.find_all('script')[8].get_text()
        self.get_buddies(buddies)


    def scrape_stats(self, url):
        """
        retrieves info from 'stats' section of requester's profile
        :param url:
        :return:
        """
        pass


    def scrape_current_game(self, url):
        """
        gets basic stats of players in the requester's current ESEA match
        :param url: requester's ESEA profile link / username
        :return: n/a
        """
        pass


    def track(self, esea_username, *args):
        """
        Sends updates via discord about change in statistics/rank of tracked players automatically after they finish a match
        :param esea_username: esea username or profile url to track
        :param args: other users to track
        :return:
        """

        pass


    def compare_profiles(self, esea_username1, esea_username2, *args):
        user1 = EseaProfile()
        user2 = EseaProfile()

        opts = {}


    def scrape_esea(self, esea_username, opts):

        try:
            profile_url = self.get_profile_url(esea_username)
        except requests.exceptions.MissingSchema:
            info = 'User not found or does not exist.'

        self.scrape_profile(profile_url)

        info = self.info['header']

        if opts['specific_value'] is True:
            info += opts['specific_value_key'] + ': ' + self.info['single_request'][opts['specific_value_key']]

        elif opts['specific_values'] is True:
            if opts['profile_info'] is True:
                info += self.info['profileTab']['profile']['formatted']
            for i in opts['specific_values_keys']:
                info += i + ': ' + self.info['single_request'][i] + '\n'
                opts['specific_values_keys'].remove(i)

        else:
            if opts['profile_info'] is True:
                info += self.info['profileTab']['profile']['formatted']
            if opts['buddies'] is True:
                info += self.info['profileTab']['buddies']['formatted']

        return info


#Testing
x = EseaScraper()
x.scrape_profile('https://play.esea.net/users/1481222')
