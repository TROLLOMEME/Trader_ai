import os 
import time 
import json 
import requests 
import openai

from dotenv import load_dotenv 
from solana.keypair import Keypair 
from solana.rpc.api import Client

Load .env file 

load_dotenv()

OpenAI setup 

openai.api_key = os.getenv("OPENAI_API_KEY") MAX_SOL_PER_TRADE = float(os.getenv("MAX_SOL_PER_TRADE", 0.1))

Load Solana keypair from keypair.json 

with open("keypair.json") as f: secret = json.load(f) keypair = Keypair.from_secret_key(bytes(secret))

Setup Solana RPC client 

client = Client("https://api.mainnet-beta.solana.com")

Jupiter constants 

SOL_MINT = "So11111111111111111111111111111111111111112" JUPITER_TOKENS_URL = "https://token.jup.ag/all" JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"

Get token list from Jupiter 

def get_jupiter_tokens(): res = requests.get(JUPITER_TOKENS_URL) tokens = res.json() return [t for t in tokens if t.get("symbol") and t.get("mint") and t.get("chainId") == 101][:50]

Use GPT to pick a token to buy 

def analyze_tokens_with_gpt(tokens): symbols = ", ".join([t["symbol"] for t in tokens]) prompt = f"From these Solana tokens: {symbols}, which one looks best to buy today? Only return the SYMBOL." res = openai.ChatCompletion.create( model="gpt-4", messages=[ {"role": "system", "content": "You are a Solana trading bot."}, {"role": "user", "content": prompt} ] ) return res.choices[0].message.content.strip().upper()

Get price quote from Jupiter 

def get_jupiter_quote(output_mint, sol_amount): params = { "inputMint": SOL_MINT, "outputMint": output_mint, "amount": int(sol_amount * 1e9), "slippageBps": 100, "onlyDirectRoutes": False } res = requests.get(JUPITER_QUOTE_URL, params=params) return res.json()

Simulate trade 

def simulate_trade(token): quote = get_jupiter_quote(token["mint"], MAX_SOL_PER_TRADE) if "data" not in quote or not quote["data"]: print(f"[ERROR] No route to {token['symbol']}") return best = quote["data"][0] out_amount = int(best["outAmount"]) / (10 ** token["decimals"]) print(f"[SIMULATED TRADE] Buy {out_amount:.4f} {token['symbol']} for {MAX_SOL_PER_TRADE} SOL")

Main loop 

while True: print("[INFO] Getting token list from Jupiter...") tokens = get_jupiter_tokens()

print("[INFO] Asking GPT for best token...") symbol = analyze_tokens_with_gpt(tokens) selected = next((t for t in tokens if t["symbol"].upper() == symbol), None) if selected: simulate_trade(selected) else: print(f"[WARN] Token '{symbol}' not found.") print("[WAIT] Sleeping 5 minutes...") time.sleep(300) 
