from reviewSetimentAnalysis import Scraper, Analysis 

if __name__ == '__main__':
	url = input("Enter a Flipkart or Amazon product URL to analyze: \n")	
	reviews = Scraper.get_reviews(url)	# Scraping reviews for this url
	scores = Analysis.analyze(reviews, wordcloud=True, file_path='another\\temp.png')	# Analyzing scraped reviews
	print(f'\nNegative {scores["neg"]:.2f}% Neutral {scores["neu"]:.2f}% Positive {scores["pos"]:.2f}%')