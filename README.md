# reviewSentimentAnalysis

reviewSentimentAnalysis is a Python module that can be used to scrape reviews from Flipkart & Amazon product pages. 

It can also be used either as a review scraper, or just as a sentiment analysis tool.

### Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install reviewSentimentAnalysis.

```bash
pip install git+https://github.com/ByteBaker/reviewSentimentAnalysis
```

### Usage

**Python script**

```python
"""
METHOD #1: Using single function for the job.
To use the scraper and analyzer separately, use METHOD #2
Function arguments and return types are the same.
"""

from reviewSentimentAnalysis import scrape_and_analyze

url = 'https://flipkart.com/blue-jeans-...' # URL to scan

scores = scrape_and_analyze(url)
```


```python
"""
METHOD #2: Using scraper and analyzer separately.
"""

from reviewSentimentAnalysis import Analysis, Scraper

url = 'https://flipkart.com/blue-jeans-...' # Flipkart product URL to analyze
# or
url = 'https://www.amazon.in/men-grey-...' # Amazon product URL to analyze

reviews = Scraper.get_reviews(url) # returns list of reviews

scores = Analysis.analyze(reviews)
# Returns a dictionary of scores and displays word cloud
# scores ~ {'pos': 0, 'neg': 0, 'neu' : 0}

scores = Analysis.analyze(reviews, wordcloud=True)
# Also saves the word cloud as 'temp.png' in current directory

scores = Analysis.analyze(reviews, wordcloud=True, file_path='path\to\file.png')
# Saves the word cloud in 'file.png' at specified location
```

**Command line**
```bash
$ reviewSentimentAnalysis ↵
Enter a Flipkart or Amazon product URL to analyze: 
https://flipkart.com/blue-jeans-... ↵
..
..
..

Negative 10.15%, Neutral 48.37%, Positive 41.48%
```
### Requirements
```
vaderSentiment==3.3.2
wordcloud==1.8.0
beautifulsoup4==4.6.0
requests==2.18.4
progressbar==2.5
```
### Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### License
[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)
