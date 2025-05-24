import os import time import openai import requests from dotenv import load_dotenv from solders.keypair import Keypair from solana.rpc.api import Client from solana.transaction import Transaction from solana.publickey import PublicKey

Load environment variables 

load_dotenv()

Set up Solana client and wallet 

client = Client("https://api.mainnet-beta.solana.com") private_key_hex = os.getenv("PRIVATE_KEY_HEX") if not private_key_hex: raise Exception("Missing PRIVATE_KEY_HEX in .env") private_key = bytes.fromhex(private_key_hex) keypair = Keypair.from_bytes(private_key)

OpenAI setup 

openai.api_key = os.getenv("OPENAI_API_KEY")

Trade configuration 

MAX_SOL_PER_TRADE = float(os.getenv("MAX_SOL_PER_TRADE", 0.1))

Get trending tokens from CoinGecko 

def get_trending_tokens(): url = "https://api.coingecko.com/api/v3/search/trending" response = requests.get(url) coins = response.json().get("coins", []) return [coin["item"]["name"] + " (" + coin["item"]["symbol"] + ")" for coin in coins]

Ask OpenAI to pick best token to buy 

def analyze_tokens_with_gpt(token_list): prompt = f"Here is a list of trending tokens: {', '.join(token_list)}. Which one looks like a good buy today based on hype and momentum? Only reply with the token name." response = openai.ChatCompletion.create( model="gpt-4", messages=[ {"role": "system", "content": "You are a crypto market analyst bot."}, {"role": "user", "content": prompt} ] ) return response.choices[0].message.content.strip()

Placeholder for executing buy order (to be replaced with real Jupiter/Raydium interaction) 

def execute_buy(token_name): print(f"[ACTION] Would attempt to buy {token_name} with up to {MAX_SOL_PER_TRADE} SOL.") # TODO: Integrate with Jupiter API or build Raydium transaction

Main loop 

while True: print("[INFO] Fetching trending tokens...") tokens = get_trending_tokens() print("[INFO] Asking GPT to analyze...") best_pick = analyze_tokens_with_gpt(tokens) print(f"[GPT DECISION] Buy: {best_pick}") execute_buy(best_pick) print("[WAIT] Sleeping 5 minutes...") time.sleep(300)

