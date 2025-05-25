import os import time import json import requests import openai from dotenv import load_dotenv from solana.keypair import Keypair from solana.rpc.api import Client

Load .env 

load_dotenv()

Setup OpenAI 

openai.api_key = os.getenv("OPENAI_API_KEY") MAX_SOL_PER_TRADE = float(os.getenv("MAX_SOL_PER_TRADE", 0.1))

Load Solana Keypair from file 

with open("keypair.json") as f: secret_key = json.load(f) keypair = Keypair.from_secret_key(bytes(secret_key))

Setup Solana RPC 

client = Client("https://api.mainnet-beta.solana.com")

Constants 

SOL_MINT = "So11111111111111111111111111111111111111112" JUPITER_TOKENS_URL = "https://token.jup.ag/all" JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"

Get tokens from Jupiter 

def get_jupiter_tokens(): response = requests.get(JUPITER_TOKENS_URL) tokens = response.json() return [t for t in tokens if t.get("symbol") and t.get("mint") and t.get("chainId") == 101][:50]

Ask GPT to analyze 

def analyze_tokens_with_gpt(tokens): symbols = ", ".join([t["symbol"] for t in tokens]) prompt = f"Here is a list of Solana tokens: {symbols}. Which one looks best to buy today? Return only the SYMBOL." response = openai.ChatCompletion.create( model="gpt-4", messages=[ {"role": "system", "content": "You are a Solana trader bot."}, {"role": "user", "content": prompt} ] ) return response.choices[0].message.content.strip().upper()

Quote from Jupiter 

def get_jupiter_quote(output_mint, amount_sol): params = { "inputMint": SOL_MINT, "outputMint": output_mint, "amount": int(amount_sol * 1e9), "slippageBps": 100, "onlyDirectRoutes": False } res = requests.get(JUPITER_QUOTE_URL, params=params) return res.json()

Simulated swap 

def simulate_trade(token): quote = get_jupiter_quote(token["mint"], MAX_SOL_PER_TRADE) if "data" not in quote or not quote["data"]: print(f"[ERROR] No route for {token['symbol']}") return best = quote["data"][0] out_amount = int(best["outAmount"]) / (10 ** token["decimals"]) print(f"[SIM] Buy {out_amount:.4f} {token['symbol']} for {MAX_SOL_PER_TRADE} SOL")

Main loop 

while True: print("[INFO] Getting tokens...") tokens = get_jupiter_tokens() print("[INFO] Asking GPT...") chosen = analyze_tokens_with_gpt(tokens) token = next((t for t in tokens if t["symbol"].upper() == chosen), None) if token: simulate_trade(token) else: print(f"[WARN] GPT returned unknown token: {chosen}") time.sleep(300)


