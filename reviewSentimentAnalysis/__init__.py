from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as Analyzer
from wordcloud import WordCloud
from bs4 import BeautifulSoup as Soup
from requests import get
import re
import progressbar
from time import sleep
import os


class Scraper:
	"""
	Utility class with methods to scrape reviews from Amazon and Flipkart products.
	"""
	REQUEST_DELAY = 1

	@staticmethod
	def __get_website_type(url):
		# Returns 1 for Amazon and 0 for Flipkart else -1
		if url.startswith('https://flipkart.com') or url.startswith('https://www.flipkart.com'):
			return 0

		if url.startswith('https://amazon') or url.startswith('https://www.amazon'):
			return 1

		return -1


	@staticmethod
	def __get_review_link_and_count(url, site='Flipkart'):
		"""
		In-built private method of class 'Scraper'

		DO NOT USE separately.
		"""
		FLIPKART_PATTERN = '\\?pid=[A-Z0-9]+&?'
		AMAZON_PATTERN = 'https://www.amazon.in/[A-Za-z0-9\-]+/dp/[0-9A-Za-z]+/'

		print('[+] Verifying URL.')

		if site == 'Amazon':	
			url_clean = re.search(AMAZON_PATTERN, url).group()
			review_url = url_clean.replace('/dp/', '/product-reviews/')

			content = get(review_url).text
			temp_soup = Soup(content, 'lxml')
			
			review_count_div = temp_soup.find_all('div', attrs={'data-hook':'cr-filter-info-review-rating-count'})
			review_count_value = review_count_div[0].text.strip().split('|')[-1].strip().split('global')[0]
			no_of_reviews = int(''.join(review_count_value.split(',')))

			return no_of_reviews, review_url + '?pageNumber='

		if site == 'Flipkart':
			#url_clean = url[:re.search(FLIPKART_PATTERN, url).span()[1] - 1]
			content = get(url).text
			temp_soup = Soup(content, 'lxml')

			rcount_div = temp_soup.find('div', attrs={'class':'_3ors59'})

			if rcount_div:
				count_span = rcount_div.find('span', attrs={'class':'_38sUEc'})
				no_of_reviews = int(re.search('[0-9,]+ review', count_span.text.lower()).group().split()[0])
			else:
				no_of_reviews = 0

			return no_of_reviews, url.replace('/p/', '/product-reviews/') + '&page='


	@staticmethod
	def __get_flipkart_reviews(url, no_of_reviews):
		"""
		In-built private method of class 'Scraper'

		DO NOT USE separately.
		"""
		GET_REVIEW_TEXT_PRIMARY = lambda review: review.find('div').find('div').text
		GET_REVIEW_TEXT_SECONDARY = lambda review: review.find('div', attrs={'class':'_2t8wE0'}).text

		reviews_class_primary = 'qwjRop'
		reviews_class_secondary = '_2t8wE0'

		no_of_pages = int(-(-no_of_reviews//10))
		reviews = []

		print(f'[+] Scraping "{url[:50]}..."')
		print(f'[+] Total {no_of_pages} pages.')
		progress = progressbar.ProgressBar(maxval=no_of_pages+1, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
		progress.start()
		for i in range(1, no_of_pages+1):
			source = get(url+ str(i)).text
			temp_soup = Soup(source, 'lxml')
			review_divs = temp_soup.find_all('div', attrs={'class': reviews_class_primary})

			if review_divs[0].find('div', attrs={'class': reviews_class_secondary}):
				reviews.extend(list(map(GET_REVIEW_TEXT_SECONDARY, review_divs)))
			else:
				reviews.extend(list(map(GET_REVIEW_TEXT_PRIMARY, review_divs)))
			progress.update(i+1)
		progress.finish()
		return reviews


	@staticmethod
	def __get_amazon_reviews(url, no_of_reviews):
		"""
		In-built private method of class 'Scraper'

		DO NOT USE separately.
		"""
		GET_REVIEW_TEXT = lambda review: review.text.strip()
		no_of_pages = int(-(-no_of_reviews//10))
		reviews = []

		print(f'[+] Scraping "{url[:50]}..."')
		print(f'[+] Total {no_of_pages} pages.')
		progress = progressbar.ProgressBar(maxval=no_of_pages+1, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
		progress.start()
		for i in range(1, no_of_pages + 1):
			source = get(url+ str(i)).text
			temp_soup = Soup(source, 'lxml')
			reviews.extend(list(map(GET_REVIEW_TEXT, temp_soup.find_all('span', attrs={'data-hook':'review-body'}))))
			sleep(Scraper.REQUEST_DELAY)
			progress.update(i+1)
		progress.finish()
		return reviews


	@staticmethod
	def __get_list_of_review_text(url):
		"""
		In-built private method of class 'Scraper'

		DO NOT USE separately.
		"""
		if not url.startswith('https://'):
			url = 'https://' + url

		reviews = []

		site_type = Scraper.__get_website_type(url)
		if site_type == -1:
			print("[x] Error! Not a Flipkart or Amazon URL")

		if site_type == 0:
			no_of_reviews, link = Scraper.__get_review_link_and_count(url, site='Flipkart')
			if no_of_reviews:
				reviews = Scraper.__get_flipkart_reviews(link, no_of_reviews)

		if site_type == 1:
			no_of_reviews, link = Scraper.__get_review_link_and_count(url, site='Amazon')
			if no_of_reviews:
				reviews = Scraper.__get_amazon_reviews(link, no_of_reviews)

		return reviews

	@staticmethod
	def get_reviews(url):
		"""
		(Str)	url :	URL to the product page on Flipkart or Amazon

		Returns list of reviews [Str]
		"""

		return Scraper.__get_list_of_review_text(url)


class Analysis:
	"""
	Utility class with methods to analyze list of strings for sentiment.
	"""
	@staticmethod
	def __generate_word_cloud(lines, wordcloud=False, file_path='temp.png'):
		"""
		In-built private method of class 'Analysis'

		DO NOT USE separately.
		"""
		if not lines:
			return
		
		print('[+] Generating word cloud.')
		big_line = ' '.join(lines)
		cloud = WordCloud(width=600, height=400).generate(big_line)
		if wordcloud:
			file_path = os.path.join(os.getcwd(), file_path)
			if os.path.isfile(file_path):
				if not os.path.exists(os.path.dirname(file_path)):
					os.makedirs(os.path.dirname(file_path))
			else:
				print('[+] Given path not a file. Saving to temporary.')
				file_path = os.path.join(os.environ['temp'], 'temp.png')
		else:
			file_path = os.path.join(os.environ['temp'], 'temp.png')

		cloud.to_file(file_path)
		_ = os.system(file_path)



	@staticmethod
	def __average_sentiment_score(scores):
		"""
		In-built private method of class 'Analysis'

		DO NOT USE separately.
		"""
		average_score = dict.fromkeys(['neg', 'neu', 'pos'], 0)
		if not scores:
			return average_score

		print('[+] Calculating sentiment scores.')
		for score in scores:
			average_score['neg'] += score['neg']
			average_score['neu'] += score['neu']
			average_score['pos'] += score['pos']

		average_score['neg'] = average_score['neg']*100 / len(scores)
		average_score['neu'] = average_score['neu']*100 / len(scores)
		average_score['pos'] = average_score['pos']*100 / len(scores)
		
		return average_score


	@staticmethod
	def analyze(reviews, wordcloud=False, file_path='temp.png'):
		"""
		(List)	reviews :	Compulsary argument
		List of strings to be analyzed.

		(Bool)	wordcloud = False :	Default argument
		By default save word cloud to temporary directory.
		Setting True will save it to given file_path.

		(Str)	file_path = 'temp.png' :	Default argument
		Save word cloud to specified file_path if wordcloud == True
		Meaningless if wordcloud == False
		If nothing specified, save to temp.png in current directory.

		Returns:
		(Dict)	{
			'neg' : 0,		-> Fraction of negative score
			'pos' : 0,		-> Fraction of positive score
			'neu' : 0		-> Fraction of neutral score
		}

		"""
		analyzer_inst = Analyzer()
		scores = Analysis.__average_sentiment_score(list(map(analyzer_inst.polarity_scores, reviews)))
		Analysis.__generate_word_cloud(reviews, wordcloud=wordcloud, file_path=file_path)
		return scores


def scrape_and_analyze(url, wordcloud=False, file_path='temp.png'):
	analyzer_inst = Analyzer()
	reviews = Scraper.get_reviews(url)
	scores = Analysis.analyze(reviews, wordcloud=wordcloud, file_path=file_path)
	return scores