#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 23:54:17 2022

@author: Ragdehl
"""
import ccxt
import requests
import datetime
import json


def get_crypto_price(time, name, crypto_id, crypto_symbol, stop_rate = 0.5):
    '''
    Finds the price of the crypto (based on USDT) at a exact time (1 minute precission).
    It search the information in several exanges. 
    To go quicker reduce de number of exqnges to check with stop_rate.
    If price not found, it searches the information of the daily price (not 1 minute precission) in coingecko.
    '''
    
    currency = crypto_symbol + '/USDT'

    if isinstance(time, datetime.date): time = time.strftime("%d/%m/%Y %H:%M")
    timestamp = int(datetime.datetime.strptime(time, '%d/%m/%Y %H:%M').timestamp() * 1000)

    i = 0
    found = 0
    
    # Opens files that stores list of best exchanges: based on previous researches
    with open('performance_exchange.json') as jsonFile:
        performance_exchange = json.load(jsonFile)
        jsonFile.close()

    #exchanges = list(ccxt.exchanges)
    #exchanges = random.sample(exchanges, len(exchanges))
    
    stop = False
    
    price_exchange = {}
    #performance_exchange = {}
    
    # This for loop tries to find the currency in one exchange
    for exchange_id in performance_exchange:
        i += 1
        try:
            # Get exange markets list(CRYPTO1/CRYPTO2",...)
            exchange = getattr(ccxt, exchange_id)()
            exchange.load_markets()

            # Find if your currency (CRYPTO/USDT) appears on the exchange
            if currency.upper() in exchange.symbols:
                
                # Retreive price at a given time
                price = exchange.fetch_ohlcv(currency.upper(), '1m', timestamp, 1)[0][-2]

                # If price is in good format -> Found++
                if isinstance(price,float):
                    price_exchange[exchange_id] = price
                    print(exchange_id, price)
                    found += 1
                
                # Select the best price from the different 'found' exchanges
                if found >= 3:
                    ratios = {}
                    
                    # Calculate the 'ratios' difference between prices of different exchanges
                    # Only those who differe 0.01 between them will be choosen
                    for ex in price_exchange:
                        ratios[ex] = []
                        for ex2 in price_exchange:
                            ratios[ex].append(abs((price_exchange[ex] - price_exchange[ex2]) / price_exchange[ex]) >= 0.01)

                    p_e = {}
                    for ex in ratios:
                        if sum(ratios[ex]) < len(ratios[ex])/2:
                            p_e[ex] = price_exchange[ex]

                    if p_e == {}:
                        found = 0
                    else:
                        price_exchange = p_e
            else:
                print(currency.upper(), 'NOT FOUND in ', exchange_id)

            if (found >= 3) or (i >=len(performance_exchange)):
                for ex in price_exchange:
                    performance_exchange[ex] += 1

                performance_exchange = {k: v for k, v in sorted(performance_exchange.items(), key=lambda item: item[1], reverse=True)}
                with open('performance_exchange.json', 'w') as f:
                    json.dump(performance_exchange, f)

                prices = []
                for exchange in price_exchange:
                    prices.append(price_exchange[exchange])

                price = sum(prices) / len(prices)
                print('price', price)

                #print(price_exchange, performance_exchange)
                #return price_exchange, performance_exchange, ratios
                return price
                break

        except:
            print(currency.upper(), 'NOT FOUND in ', exchange_id)

    if stop:

        try:
            url = 'https://api.coingecko.com/api/v3/coins/' + crypto_id + '/history?date=' + time[:10].replace('/','-')
                        
            data = requests.get(url)
            price = data.json()
            
            print('coingecko')
            return price['market_data']['current_price']['usd'], 'coingecko'
        except:
            print('Crypto', name, 'NOT FOUND on exanges or coingecko')
            
            
class Portfolio():
    def __init__(self, name = 'Portfolio'):
        '''
        Initialisation of the Portfolio.
        '''
        self.name = name.lower()
        self.wallets = {}
        
    def add_wallet(self, wallet):
        '''
        Add wallet to the portfolio
        '''
        self.wallets[wallet.chain]=wallet
