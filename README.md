# mexc_triangular_arbitrage_scanner
That is a code made generate all possible triangular arbitrage combinations with a logic and with a certain execution route. 

So firstly run generate_combinations.py, wait for some hours, and it will generate a combinations.json file with all the possible combinations that MEXC has. 

Then run web_socket.py, which will open a websocket orderbook stram for each pair of each combinations of your desired initial coin, or of every combination possible (uncomment line 137 and comment all bellow on main to do so).

web_socket.py sends the data received to orderbook_analysis.py, in which calculates the real take price you will pay by executing a market order, thus giving you the most real triangular arbitrage profit prediction, in which is always lower than 0 (loss). That's why I didn't finish coding the functions to execute the trade since there are no profit trades of such type. 

Use it for edecational propose, please update me if you are able to identify real profit opportunities, I would love to improve my code and hear where what were my errors.
