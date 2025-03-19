#!/bin/bash

url="https://www.zacks.com/stock/quote/TTE"

price=$(curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" "$url" | grep 'class="last_price"' | sed -E 's/.*<p class="last_price">\$([0-9.]+)<span>.*$/\1/')

timestamp=$(curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" "$url" | grep '<p class="date">Updated' | sed -E 's/.*<span id="timestamp">([^<]+)<\/span>.*/\1/')

# Print stock price and last time updated
echo "TTE Stock Price: \$$price (Updated $timestamp)"