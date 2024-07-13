import json
import requests

# Function to fetch symbols from MEXC API
def get_symbols():
    response = requests.get("https://api.mexc.com/api/v3/exchangeInfo")
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.json()

# Function to generate combinations
def generate_combinations(api_response):
    trading_pairs = [symbol for symbol in api_response['symbols'] if symbol['status'] == 'ENABLED']
    combinations = []
    passed = False

    for pair_a in trading_pairs:

        for pair_b in trading_pairs:

            if (pair_a['quoteAsset'] == pair_b['baseAsset'] or pair_a['quoteAsset'] == pair_b['quoteAsset'] or pair_a['baseAsset'] == pair_b['baseAsset'] or pair_a['baseAsset'] == pair_b['quoteAsset']) and pair_a != pair_b:

                for pair_c in trading_pairs:

                    if pair_a['baseAsset'] == pair_b['baseAsset']:
                        if (pair_c['baseAsset'] == pair_a['quoteAsset'] and pair_c['quoteAsset'] == pair_b['quoteAsset']):
                            operation = "BSB"
                            type = "baba"
                            initial = pair_a['quoteAsset']
                            intermediary = pair_b['quoteAsset']
                            final = pair_c['baseAsset']
                            passed = True
                        elif (pair_c['quoteAsset'] == pair_a['quoteAsset'] and pair_c['baseAsset'] == pair_b['quoteAsset']):
                            operation = "BSS"
                            type = "baba"
                            initial = pair_a['quoteAsset']
                            intermediary = pair_b['quoteAsset']
                            final = pair_c['quoteAsset']
                            passed = True

                    elif pair_a['baseAsset'] == pair_b['quoteAsset']:
                        if (pair_c['baseAsset'] == pair_a['quoteAsset'] and pair_c['quoteAsset'] == pair_b['baseAsset']):
                            operation = "BBB"
                            type = "baquo"
                            initial = pair_a['quoteAsset']
                            intermediary = pair_b['baseAsset']
                            final = pair_c['baseAsset']
                            passed = True
                        elif (pair_c['quoteAsset'] == pair_a['quoteAsset'] and pair_c['baseAsset'] == pair_b['baseAsset']):
                            operation = "BBS"
                            type = "baquo"
                            initial = pair_a['quoteAsset']
                            intermediary = pair_b['baseAsset']
                            final = pair_c['quoteAsset']
                            passed = True

                    elif pair_a['quoteAsset'] == pair_b['baseAsset']:
                        if (pair_c['baseAsset'] == pair_a['baseAsset'] and pair_c['quoteAsset'] == pair_b['quoteAsset']):
                            operation = "SSB"
                            type = "quoba"
                            initial = pair_a['baseAsset']
                            intermediary = pair_b['quoteAsset']
                            final = pair_c['baseAsset']
                            passed = True
                        elif (pair_c['quoteAsset'] == pair_a['baseAsset'] and pair_c['baseAsset'] == pair_b['quoteAsset']):
                            operation = "SSS"
                            type = "quoba"
                            initial = pair_a['baseAsset']
                            intermediary = pair_b['quoteAsset']
                            final = pair_c['quoteAsset']
                            passed = True

                    elif pair_a['quoteAsset'] == pair_b['quoteAsset']:
                        if (pair_c['baseAsset'] == pair_a['baseAsset'] and pair_c['quoteAsset'] == pair_b['baseAsset']):
                            operation = "SBB"
                            type = "quoquo"
                            initial = pair_a['baseAsset']
                            intermediary = pair_b['baseAsset']
                            final = pair_c['baseAsset']
                            passed = True
                        elif (pair_c['quoteAsset'] == pair_a['baseAsset'] and pair_c['baseAsset'] == pair_b['baseAsset']):
                            operation = "SBS"
                            type = "quoquo"
                            initial = pair_a['baseAsset']
                            intermediary = pair_b['baseAsset']
                            final = pair_c['quoteAsset']
                            passed = True

                    if passed:

                        match_dict = {
                            "n": len(combinations) + 1,
                            "type": type,
                            "operation": operation,
                            "initial": initial,
                            "final": final,
                            "intermediary": intermediary,
                            "a_base": pair_a['baseAsset'],
                            "a_quote": pair_a['quoteAsset'],
                            "a_symbol": pair_a['symbol'],
                            "b_base": pair_b['baseAsset'],
                            "b_quote": pair_b['quoteAsset'],
                            "b_symbol": pair_b['symbol'],
                            "c_base": pair_c['baseAsset'],
                            "c_quote": pair_c['quoteAsset'],
                            "c_symbol": pair_c['symbol'],
                            "combined": [pair_a['symbol'], pair_b['symbol'], pair_c['symbol']]
                        }
                        combinations.append(match_dict)
    return combinations

# Function to save combinations to a JSON file
def save_combinations_to_json(combinations, filename):
    with open(filename, 'w') as json_file:
        json.dump(combinations, json_file, indent=4)

# Main code to fetch data, generate combinations, and save to JSON
api_response = get_symbols()  # Fetch trading pairs from the API
combinations = generate_combinations(api_response)
print(combinations)
save_combinations_to_json(combinations, 'combinations.json')
print(f"Combinations saved to 'combinations.json'")