# main.py
import time
from web3 import Web3
from apscheduler.schedulers.blocking import BlockingScheduler

# ===== Your Wallet Information =====
PRIVATE_KEY = "ddb3e978e53e72e26105743fb6cbc1223ce93e977059a5d9c54fd55e4312e9d5"
SENDER_ADDRESS = "0x03b1bb3cc74aa22822d401075d497d12c5a397d4"
RECEIVER_ADDRESS = "0x5592F60a5fDf5D4d38870051fd3e5997b8f5baf8"

# ===== Blockchain Configuration (Updated RPCs) =====
CHAINS = {
    "ethereum": {
        "rpc": "https://eth.llamarpc.com",  # Free public RPC
        "chain_id": 1,
        "min_balance": 0.00001,
        "symbol": "ETH"
    },
    "polygon": {
        "rpc": "https://polygon-bor.publicnode.com",  # Reliable public RPC
        "chain_id": 137,
        "min_balance": 0.00001,
        "symbol": "MATIC"
    },
    "bsc": {
        "rpc": "https://bsc.publicnode.com",  # Official BSC RPC
        "chain_id": 56,
        "min_balance": 0.00001,
        "symbol": "BNB"
    }
}

def transfer_crypto(chain_name):
    try:
        chain = CHAINS[chain_name]
        print(f"\nChecking {chain_name.upper()}...")
        
        # Connect to blockchain
        w3 = Web3(Web3.HTTPProvider(chain["rpc"], request_kwargs={'timeout': 15}))
        
        if not w3.is_connected():
            print(f"⚠️ {chain_name.upper()} connection failed!")
            return

        # Get balance
        balance = w3.eth.get_balance(SENDER_ADDRESS)
        balance_native = w3.from_wei(balance, 'ether')
        print(f"Current Balance: {balance_native:.8f} {chain['symbol']}")
        print(f"Minimum Required: {chain['min_balance']} {chain['symbol']}")

        if balance_native > chain["min_balance"]:
            # Get current gas price
            gas_price = w3.eth.gas_price
            gas_limit = 21000  # Standard transfer
            
            # Calculate gas cost
            gas_cost = gas_price * gas_limit
            amount_to_send = balance - gas_cost
            
            if amount_to_send > 0:
                # Get nonce
                nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)
                
                # Build transaction
                tx = {
                    'nonce': nonce,
                    'to': RECEIVER_ADDRESS,
                    'value': amount_to_send,
                    'gas': gas_limit,
                    'gasPrice': gas_price,
                    'chainId': chain["chain_id"]
                }
                
                # Sign and send transaction
                signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                print(f"✅ {chain_name.upper()} TRANSFER SUCCESSFUL!")
                print(f"TX Hash: {tx_hash.hex()}")
                print(f"Sent: {w3.from_wei(amount_to_send, 'ether'):.8f} {chain['symbol']}")
            else:
                print(f"⚠️ Insufficient balance for gas fee on {chain_name}")
        else:
            print(f"❌ Balance below threshold on {chain_name}")
    
    except Exception as e:
        print(f"🔥 {chain_name.upper()} ERROR: {str(e)}")
        time.sleep(5)  # Wait before retrying

def auto_transfer_job():
    print("\n" + "="*60)
    print(f"🔄 AUTO TRANSFER CHECK | {time.ctime()}")
    print("="*60)
    print(f"👤 Sender: {SENDER_ADDRESS}")
    print(f"🎯 Receiver: {RECEIVER_ADDRESS}")
    
    for chain in CHAINS:
        transfer_crypto(chain)

# Start scheduler (every 15 seconds)
scheduler = BlockingScheduler()
scheduler.add_job(auto_transfer_job, 'interval', seconds=15)
print("\n🤖 CRYPTO TRANSFER BOT STARTED!")
print("🔁 Monitoring Ethereum, Polygon, BSC every 15 seconds")
print("🛑 Press Ctrl+C to stop the bot")
scheduler.start()
