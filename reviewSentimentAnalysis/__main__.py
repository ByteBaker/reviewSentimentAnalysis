try:
	from reviewSentimentAnalysis import scrape_and_analyze
except ImportError:
	from __init__ import scrape_and_analyze

def main():
	url = input("Enter a Flipkart or Amazon product URL to analyze: \n")	
	scores = scrape_and_analyze(url)	# Analyzing scraped reviews
	print(f'\nNegative {scores["neg"]:.2f}%, Neutral {scores["neu"]:.2f}%, Positive {scores["pos"]:.2f}%')

if __name__ == '__main__':
	main()