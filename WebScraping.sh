#!/bin/bash
# TTE Stock Price Scraper
# Scrapes stock prices from Zacks.com using bash and regex

# Configuration
CSV_FILE="stock_prices.csv"
LOG_FILE="scraper.log"
INTERVAL=120  # Wait time in seconds between requests
URL="https://www.zacks.com/stock/quote/TTE"
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

# Helper functions
log_message() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# Create CSV with headers if it doesn't exist
if [ ! -f "$CSV_FILE" ]; then
    log_message "Creating new CSV file with headers"
    echo "Price,LastUpdated" > "$CSV_FILE"
fi

# Trap Ctrl+C to exit gracefully
trap 'log_message "Script terminated by user"; exit 0' INT

# Main loop
log_message "Starting TTE stock price scraper"
while true; do
    # Fetch the webpage
    log_message "Fetching data from $URL"
    html_content=$(curl -s -A "$USER_AGENT" "$URL")
    
    if [ -z "$html_content" ]; then
        log_message "ERROR: Failed to fetch content from $URL"
        sleep $INTERVAL
        continue
    fi
    
    # Extract price using regex
    # Look for a pattern like: <p class="last_price">$65.48<span>
    if [[ $html_content =~ \<p\ class=\"last_price\"\>\$([0-9.]+)\<span\> ]]; then
        price="${BASH_REMATCH[1]}"
        log_message "Price extracted: \$$price"
    else
        log_message "ERROR: Could not extract price from HTML content"
        sleep $INTERVAL
        continue
    fi
    
    # Extract timestamp using regex
    # Look for a pattern like: <span id="timestamp">Mar 27, 2025 02:38 PM</span>
    if [[ $html_content =~ \<span\ id=\"timestamp\"\>([^<]+)\<\/span\> ]]; then
        timestamp="${BASH_REMATCH[1]}"
        log_message "Timestamp extracted: $timestamp"
    else
        log_message "ERROR: Could not extract timestamp from HTML content"
        sleep $INTERVAL
        continue
    fi
    
    # Read the last timestamp from the CSV (skip header)
    last_timestamp=$(tail -n 1 "$CSV_FILE" 2>/dev/null | awk -F, '{gsub(/"/,"",$2); print $2}')
    
    # If the timestamps are different or if last_timestamp is empty, append the data
    if [ -z "$last_timestamp" ] || [ "$timestamp" != "$last_timestamp" ]; then
        echo "$price,\"$timestamp\"" >> "$CSV_FILE"
        log_message "New data saved: \$$price at $timestamp"
    else
        log_message "No change in data (still $timestamp)"
    fi
    
    log_message "Waiting $INTERVAL seconds before next check..."
    sleep $INTERVAL
done