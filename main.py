import os
import time
import json
import requests
import openai
import base58
from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.keypair import Keypair

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MAX_SOL = float(os.getenv("MAX_SOL_PER_TRADE", 0.1))

# Load Phantom keypair from base58 format
private_key = os.getenv("PRIVATE_KEY")
keypair = Keypair.from_secret_key(base58.b58decode(private_key))

# Connect to Solana
client = Client("https://api.mainnet-beta.solana.com")

# Print wallet balance
balance = client.get_balance(keypair.public_key)
sol_balance = balance['result']['value'] / 1e9
print(f"[WALLET] Balance: {sol_balance} SOL")

# Jupiter token list
def get_tokens():
    url = "https://token.jup.ag/all"
    res = requests.get(url)
    return [t for t in res.json() if t['chainId'] == 101][:50]

# Ask GPT for best token to buy
def ask_gpt(tokens):
    names = ", ".join([t["symbol"] for t in tokens])
    prompt = f"From these Solana tokens: {names}, which one looks best to buy today? Only return the SYMBOL."
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a Solana crypto analyst bot."},
            {"role": "user", "content": prompt}
        ]
    )
    return res['choices'][0]['message']['content'].strip().upper()

# Simulate trade (just prints output amount)
def simulate_trade(token):
    url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": token["mint"],
        "amount": int(MAX_SOL * 1e9),
        "slippageBps": 100
    }
    res = requests.get(url, params=params).json()
    if "data" in res and res["data"]:
        amount_out = int(res["data"][0]["outAmount"]) / (10 ** token["decimals"])
        print(f"[TRADE] Would buy {amount_out:.4f} {token['symbol']} for {MAX_SOL} SOL")
    else:
        print(f"[ERROR] No route found to {token['symbol']}")

# Main loop
while True:
    print("[INFO] Fetching tokens from Jupiter...")
    tokens = get_tokens()
    print("[INFO] Asking OpenAI for signal...")
    pick = ask_gpt(tokens)
    token = next((t for t in tokens if t["symbol"].upper() == pick), None)
    if token:
        simulate_trade(token)
    else:
        print(f"[WARN] Token '{pick}' not found.")
    time.sleep(300)
