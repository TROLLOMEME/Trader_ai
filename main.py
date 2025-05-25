import os
import json
import time
import requests
import openai
from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.keypair import Keypair
from base58 import b58decode

# Load environment variables
load_dotenv()

# Load private key and OpenAI API key from .env
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_SOL = float(os.getenv("MAX_SOL_PER_TRADE", 0.1))

if not PRIVATE_KEY or not OPENAI_API_KEY:
    raise Exception("Missing PRIVATE_KEY or OPENAI_API_KEY in .env")

# Setup wallet
secret_key_bytes = b58decode(PRIVATE_KEY)
keypair = Keypair.from_secret_key(secret_key_bytes)

# Connect to Solana
client = Client("https://api.mainnet-beta.solana.com")
wallet_address = keypair.public_key
balance = client.get_balance(wallet_address)
sol_balance = balance["result"]["value"] / 1e9
print(f"[WALLET] Address: {wallet_address}")
print(f"[WALLET] Balance: {sol_balance} SOL")

# Setup OpenAI
openai.api_key = OPENAI_API_KEY

# Get token list from Jupiter
def get_tokens():
    url = "https://token.jup.ag/all"
    res = requests.get(url)
    return [t for t in res.json() if t["chainId"] == 101 and "symbol" in t][:50]

# Ask GPT for a buy signal
def ask_gpt(tokens):
    names = ", ".join([t["symbol"] for t in tokens])
    prompt = f"From these Solana tokens: {names}, which one looks best to buy today? Only return the SYMBOL."
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a Solana trading bot."},
            {"role": "user", "content": prompt}
        ]
    )
    return res["choices"][0]["message"]["content"].strip().upper()

# Simulate buying token using Jupiter quote
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
        out_amount = int(res["data"][0]["outAmount"]) / (10 ** token["decimals"])
        print(f"[TRADE] Buy {out_amount:.4f} {token['symbol']} for {MAX_SOL} SOL")
    else:
        print(f"[ERROR] No quote for {token['symbol']}")

# Main loop (run once)
print("[INFO] Fetching token list from Jupiter...")
tokens = get_tokens()

print("[INFO] Asking OpenAI for trading signal...")
symbol = ask_gpt(tokens)

selected = next((t for t in tokens if t["symbol"].upper() == symbol), None)
if selected:
    simulate_trade(selected)
else:
    print(f"[WARN] Token '{symbol}' not found in token list.")
