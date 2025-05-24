import os
import time
import json
import requests
import openai
from dotenv import load_dotenv

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client

# Load .env variables
load_dotenv()

# OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Phantom Wallet (private key in hex)
private_key_hex = os.getenv("PRIVATE_KEY_HEX")
if not private_key_hex:
    raise Exception("PRIVATE_KEY_HEX not found in environment variables")

private_key = bytes.fromhex(private_key_hex)
keypair = Keypair.from_bytes(private_key)

# Solana RPC
client = Client("https://api.mainnet-beta.solana.com")

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
JUPITER_TOKENS_URL = "https://token.jup.ag/all"
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
MAX_SOL_PER_TRADE = float(os.getenv("MAX_SOL_PER_TRADE", 0.1))

# Get Solana tokens list from Jupiter
def get_jupiter_tokens():
    response = requests.get(JUPITER_TOKENS_URL)
    tokens = response.json()
    filtered = [t for t in tokens if t.get("symbol") and t.get("mint") and t.get("chainId") == 101]
    return filtered[:50]  # limit for prompt

# Ask GPT-4 to choose best token
def analyze_tokens_with_gpt(token_list):
    symbols = ", ".join([t["symbol"] for t in token_list])
    prompt = f"Here is a list of trending Solana tokens: {symbols}. Which one looks best to buy today and why? Return only the SYMBOL."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Solana crypto trader bot."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip().upper()

# Get Jupiter swap quote
def get_jupiter_quote(output_mint, amount_sol):
    params = {
        "inputMint": SOL_MINT,
        "outputMint": output_mint,
        "amount": int(amount_sol * 1e9),  # in lamports
        "slippageBps": 100,
        "onlyDirectRoutes": False
    }
    response = requests.get(JUPITER_QUOTE_URL, params=params)
    return response.json()

# Simulate trade
def execute_trade(token):
    quote = get_jupiter_quote(token["mint"], MAX_SOL_PER_TRADE)
    if "data" not in quote or not quote["data"]:
        print(f"[ERROR] No route to trade for {token['symbol']}")
        return
    best = quote["data"][0]
    out_amount = int(best["outAmount"]) / (10 ** token["decimals"])
    print(f"[TRADE] Would buy {out_amount:.4f} {token['symbol']} for {MAX_SOL_PER_TRADE} SOL.")

# Main loop
while True:
    print("[INFO] Fetching token list...")
    tokens = get_jupiter_tokens()

    print("[INFO] Asking GPT for best token...")
    best_symbol = analyze_tokens_with_gpt(tokens)
    selected = next((t for t in tokens if t["symbol"].upper() == best_symbol), None)

    if selected:
        execute_trade(selected)
    else:
        print(f"[WARN] Token '{best_symbol}' not found in list.")

    print("[WAIT] Sleeping for 5 minutes...\n")
    time.sleep(300)
