import asyncio
import websockets
import json
from decimal import Decimal, getcontext
import logging

# Constants
WS_URL = "wss://wbs.mexc.com/ws"
INITIAL_COIN = "ETH"
DEPTH = 20  # Valid values: 5, 10, or 20

# Logging
logging.basicConfig(level=logging.INFO)

# Dictionary to keep track of active streams and their req_id
active_streams = {}
orderbook_data = {}
getcontext().prec = 28

class WebSocketConnection:
    def __init__(self, pair, depth, filtered_combinations, initial_quantity):
        self.pair = pair
        self.depth = depth
        self.filtered_combinations = filtered_combinations
        self.initial_quantity = initial_quantity
        self.req_id = 0

    async def connect(self):
        while True:
            try:
                async with websockets.connect(WS_URL) as websocket:
                    subscribe_message = {
                        "method": "SUBSCRIPTION",
                        "params": [f"spot@public.limit.depth.v3.api@{self.pair}@{self.depth}"]
                    }
                    self.req_id += 1
                    subscribe_message["id"] = self.req_id
                    await websocket.send(json.dumps(subscribe_message))

                    ping_task = asyncio.create_task(self.send_ping(websocket))

                    try:
                        async for message in websocket:
                            data = json.loads(message)
                            await self.process_message(data, self.filtered_combinations, self.initial_quantity)
                    finally:
                        await websocket.close()
                        ping_task.cancel()
            except websockets.exceptions.ConnectionClosedError as e:
                logging.info(f"Connection closed for pair {self.pair}. Reconnecting...")
                await asyncio.sleep(1)  # Wait before reconnecting
            except websockets.exceptions.ConnectionClosedOK as e:
                logging.info(f"Connection closed OK for pair {self.pair}. Reconnecting...")
                await asyncio.sleep(1)  # Wait before reconnecting
            except Exception as e:
                logging.error(f"Unexpected error for pair {self.pair}: {e}")
                await asyncio.sleep(1)  # Wait before reconnecting

    async def send_ping(self, websocket):
        while True:
            try:
                ping_message = {"method": "PING", "id": self.req_id}
                logging.info(f'Ping sent for pair {self.pair}')
                await websocket.send(json.dumps(ping_message))
                await asyncio.sleep(19)  # at 20 secs the connection is lost
            except websockets.exceptions.ConnectionClosed:
                break

    async def process_message(self, message, filtered_combinations, initial_quantity):
        if "c" in message.keys() and message["c"].startswith("spot@public.limit.depth.v3.api@"):
            pair = message["s"]
            asks = [(Decimal(item["p"]), Decimal(item["v"])) for item in message["d"]["asks"]]
            bids = [(Decimal(item["p"]), Decimal(item["v"])) for item in message["d"]["bids"]]

            if pair in orderbook_data:
                # Update existing orderbook data
                orderbook_data[pair]['a'] = asks
                orderbook_data[pair]['b'] = bids
            else:
                # Create new entry for the trading pair
                orderbook_data[pair] = {'a': asks, 'b': bids}

            from orderbook_analysis import execute_routes
            execute_routes(filtered_combinations, orderbook_data, initial_quantity)

    async def close_connection(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

async def manage_connections(pairs, depth, filtered_combinations, initial_quantity):
    tasks = []
    for pair in pairs:
        if pair not in active_streams:
            connection = WebSocketConnection(pair, depth, filtered_combinations, initial_quantity)
            task = asyncio.create_task(connection.connect())
            tasks.append(task)
            active_streams[pair] = task

    await asyncio.gather(*tasks)

def read_combinations(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def filter_combinations(combinations, initial_coin):
    return [combo for combo in combinations if combo['initial'] == initial_coin]

combinations = read_combinations('combinations.json')
initial_coin = INITIAL_COIN
initial_quantity = Decimal(5)
filtered_combinations = filter_combinations(combinations, initial_coin)

#it run all the combinations possible at the same time
async def run_initial_coins(combinations_file):
    # Read combinations from file
    combinations = read_combinations(combinations_file)

    # Get all unique initial coins
    initial_coins = list(set(combo['initial'] for combo in combinations))

    # Initiate websockets for combinations that have this coin as initial
    tasks = []
    for initial_coin in initial_coins:
        filtered_combinations = filter_combinations(combinations, initial_coin)
        pairs = [pair for combo in filtered_combinations for pair in combo['combined']]
        print(f"Initiating websockets for combinations with initial coin {initial_coin}...")
        task = asyncio.create_task(manage_connections(pairs, DEPTH, filtered_combinations, initial_quantity))
        tasks.append(task)
        await asyncio.sleep(20)  # Wait for 20 seconds before moving on to the next coin

async def main():
    #await run_initial_coins("combinations.json") run all the combinations possible at the same time

    # Flatten the list of pairs
    pairs = []
    for combo in filtered_combinations:
        pairs.extend(combo['combined'])

    await manage_connections(pairs, DEPTH, filtered_combinations, initial_quantity)

if __name__ == "__main__":
    asyncio.run(main())