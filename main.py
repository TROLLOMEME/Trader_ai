import os
import time
import openai
import requests
from dotenv import load_dotenv

from solders.keypair import Keypair
from solana.rpc.api import Client
from solana.publickey import PublicKey

# Load env variables
load_dotenv()

# Setup
client = Client("https://api.mainnet-beta.solana.com")
private_key_hex = os.getenv("PRIVATE_KEY_HEX")
if not private_key_hex:
    raise Exception("Missing PRIVATE_KEY_HEX in .env")
private_key = bytes.fromhex(private_key_hex)
keypair = Keypair.from_bytes(private_key)

openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_SOL_PER_TRADE = float(os.getenv("MAX_SOL_PER_TRADE", 0.1))

# Get trending tokens
def get_trending_tokens():
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    coins = response.json().get("coins", [])
    return [coin["item"]["name"] + " (" + coin["item"]["symbol"] + ")" for coin in coins]

# Ask GPT
def analyze_tokens_with_gpt(token_list):
    prompt = f"Here is a list of trending tokens: {', '.join(token_list)}. Which one looks like a good buy today based on hype and momentum? Only reply with the token name."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a crypto market analyst bot."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip
