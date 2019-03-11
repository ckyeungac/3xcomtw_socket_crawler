# Web Socket Crawler for 3x.com.tw

This is a crawler that listens to the websocket of [3x.com.tw](3x.com.tw).

---

## Todo

- Terminate the multiprocessing process when the websocket's connection is close.
- Continous integration and deployment of the crawler
  - How can we keep crawl the data without duplication or missing during deployment?
  - How can we update the trade data when we implement new measurements?
- Better software engineering job on saving the trade data and updating the OHLC record.

## How to run

Install the require packages

```terminal
conda create --name trading
source activate trading
pip install -r requirements.txt
```

Run the crawler to listen a specific future product

```terminal
python websocket_crawler.py --product $product_code
```

Run multiple crawlers to listen all future products

```terminal
bash start_crawling_script.sh
```

## Claim

This crawler aims at trading experimentation, it should not be used for any commercial purpose. If this crawler involves any infringement, please contact me to remove the repository.