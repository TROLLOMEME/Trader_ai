import os import time import openai import requests from dotenv import load_dotenv from solders.keypair import Keypair from solders.pubkey import Pubkey from solana.rpc.api import Client import json

Load env variables 

load_dotenv()

Setup Solana client and wallet 

client = Client("https://api.mainnet-beta.solana.com") private_key_hex = os.getenv("PRIVATE_KEY_HEX") if not private_key_hex: raise Exception("Missing PRIVATE_KEY_HEX in .env") private_key = bytes.fromhex(private_key_hex) keypair = Keypair.from_bytes(private_key)

OpenAI setup 

openai.api_key = os.getenv("OPENAI_API_KEY")

Trade configuration 

MAX_SOL_PER_TRADE = float(os.getenv("MAX_SOL_PER_TRADE", 0.1)) SOL_MINT = "So11111111111111111111111111111111111111112" JUPITER_TOKENS_API = "https://token.jup.ag/all" JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"

Get all tokens on Solana from Jupiter 

def get_all_jupiter_tokens(): response = requests.get(JUPITER_TOKENS_API) tokens = response.json() filtered = [t for t in tokens if t.get("symbol") and t.get("mint") and t.get("chainId") == 101] top_50 = filtered[:50] # Limit for GPT prompt return top_50

Ask GPT to pick one token to buy 

def analyze_tokens_with_gpt(tokens): token_list_str = ", ".join([f"{t['symbol']}" for t in tokens]) prompt = f"These are trending Solana tokens: {token_list_str}. Based on hype, momentum, and meme potential, which ONE looks best to buy today? Only return the SYMBOL." response = openai.ChatCompletion.create( model="gpt-4", messages=[ {"role": "system", "content": "You are a crypto trading bot focused on Solana tokens."}, {"role": "user", "content": prompt} ] ) return response.choices[0].message.content.strip().upper()

Get quote from Jupiter 

def get_jupiter_quote(output_mint, amount): params = { "inputMint": SOL_MINT, "outputMint": output_mint, "amount": int(amount * 1e9), "slippageBps": 100, "onlyDirectRoutes": False } response = requests.get(JUPITER_QUOTE_API, params=params) return response.json()

Execute simulated swap 

def execute_jupiter_swap(output_token): quote = get_jupiter_quote(output_token["mint"], MAX_SOL_PER_TRADE) if "data" not in quote or len(quote["data"]) == 0: print(f"[ERROR] No route found for {output_token['symbol']}") return best_route = quote["data"][0] out_amount = int(best_route['outAmount']) / (10 ** output_token['decimals']) print(f"[TRADE] Buying {out_amount:.4f} {output_token['symbol']} for {MAX_SOL_PER_TRADE} SOL") # TODO: Real transaction with Jupiter swap API

Main loop 

while True: print("[INFO] Fetching Solana tokens from Jupiter...") tokens = get_all_jupiter_tokens() print("[INFO] Asking GPT to choose best token to buy...") selected_symbol = analyze_tokens_with_gpt(tokens) match = next((t for t in tokens if t['symbol'].upper() == selected_symbol), None) if match: execute_jupiter_swap(match) else: print(f"[WARN] GPT selected unknown token: {selected_symbol}") print("[WAIT] Sleeping 5 minutes...") time.sleep(300)


