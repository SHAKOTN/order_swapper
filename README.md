# Binance Automatic Trader POC

This is a proof of concept for a Binance automatic trader

Tests: 

[![Test Run](https://github.com/SHAKOTN/order_swapper/actions/workflows/test-run.yml/badge.svg)](https://github.com/SHAKOTN/order_swapper/actions/workflows/test-run.yml)

## How it works?
- Bot asynchroniously fetches data from Binance klines websocket and then places bid and ask orders on the market.
- Bid and ask prices are calculated based on bid-ask spread that is calculated each time new data is fetched from the websocket.

- Bid-ask formula is as follows:

    ```python
    spread = (high_price - low_price) / low_price * 100)
    ```
- If existing orders are at risk to be filled with market-price movement, bot cancels them and places new orders.

## Installation
Create `.env` file with the following content:

```bash
API_KEY=<API_KEY>
SECRET_KEY=<SECRET_KEY>
```
You can get keys for testing purposes from https://testnet.binance.vision/

To build container run:
```bash
$ docker-compose build
```

To run container run:
```bash
$ docker-compose up
```

## Running tests:
    
```bash
$ docker-compose run --rm order_swapper pytest
```
