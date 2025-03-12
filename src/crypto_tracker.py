import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# CoinGecko API URL
API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Email Configuration
EMAIL_SENDER = "codemail20252004@gmail.com"
EMAIL_PASSWORD = "bpxg epgn rkpd sgvw"  # Fetch from environment variable
EMAIL_RECEIVER = "codemail20252004@gmail.com"


# Function to fetch crypto prices
def get_crypto_price(crypto_id, currency="usd"):
    params = {"ids": crypto_id, "vs_currencies": currency}
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get(crypto_id, {}).get(currency)
    else:
        print(f"❌ Error fetching data (Status Code: {response.status_code})")
        return None

# Function to track prices over time
def track_prices(crypto_id, interval=10, duration=60, alert_threshold=None):
    prices, timestamps = [], []

    print(f"📈 Tracking {crypto_id} prices for {duration} seconds...")

    for _ in range(duration // interval):
        price = get_crypto_price(crypto_id)
        if price:
            prices.append(price)
            timestamps.append(time.strftime("%H:%M:%S"))
            print(f"💰 {crypto_id.upper()} Price: ${price}")

            # Check price alert
            if alert_threshold and price >= alert_threshold:
                print(f"🚨 ALERT! {crypto_id.upper()} reached ${price}!")
                send_email_alert(crypto_id, price, alert_threshold)

        time.sleep(interval)

    # Save to CSV
    df = pd.DataFrame({"Time": timestamps, "Price": prices})
    df.to_csv(f"{crypto_id}_prices.csv", index=False)
    print(f"✅ Data saved to {crypto_id}_prices.csv")

    return df

# Function to plot price trend
def plot_prices(df, crypto_id):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Time"], df["Price"], marker="o", linestyle="-", label=crypto_id.upper())
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.title(f"{crypto_id.upper()} Price Trend")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()

# Function to send email alerts
def send_email_alert(crypto_id, price, threshold):
    subject = f"🚨 {crypto_id.upper()} Price Alert: ${price}!"
    body = f"The price of {crypto_id.upper()} has reached ${price}, crossing your alert threshold of ${threshold}."

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")

# Main execution
if __name__ == "__main__":
    crypto_id = input("Enter cryptocurrency (e.g., bitcoin, ethereum, dogecoin): ").strip().lower()
    alert_threshold = float(input(f"Enter alert price for {crypto_id.upper()} (USD): "))

    df = track_prices(crypto_id, interval=10, duration=60, alert_threshold=alert_threshold)

    if not df.empty:
        plot_prices(df, crypto_id)
