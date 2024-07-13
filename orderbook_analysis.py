from decimal import Decimal, getcontext
import json
# Constants
getcontext().prec = 28
INITIAL_INVESTMENT = Decimal('10')
BROKERAGE_FEE = Decimal('0') #MEXC doesn't have a taker fee, so we will disable the get_effective_investment function

class OrderBookException(Exception):
    pass

def calculate_effective_price(order_book: list, initial_quantity: Decimal) -> tuple:
    """
    Calculate the effective price and quantity based on the order book and initial quantity.

    Args:
        order_book (list): List of tuples containing price and quantity.
        initial_quantity (Decimal): Initial quantity to invest.

    Returns:
        tuple: Effective price and quantity.
    """
    total_quantity = Decimal('0')
    total_cost = Decimal('0')
    remaining_quantity = initial_quantity
    for price, quantity in order_book:
        if remaining_quantity == 0:
            break
        if remaining_quantity > quantity:
            total_cost += price * quantity
            total_quantity += quantity
            remaining_quantity -= quantity
        else:
            total_cost += price * remaining_quantity
            total_quantity += remaining_quantity
            remaining_quantity = 0
    if total_quantity == 0:
        raise OrderBookException("Total quantity is zero, leading to an invalid effective price calculation")
    effective_price = total_cost / total_quantity
    return effective_price, total_quantity

#MEXC doesn't have a taker fee, so we will disable the get_effective_investment function
def get_effective_investment(initial_investment: Decimal, pair: str, brokerage_fee: Decimal, exempt_pairs: list = ["USDC"]) -> Decimal:
    """
    Calculate the effective investment amount based on the brokerage fee and exempt pairs.

    Args:
        initial_investment (Decimal): Initial investment amount.
        pair (str): Trading pair.
        brokerage_fee (Decimal): Brokerage fee.
        exempt_pairs (list): List of exempt pairs.

    Returns:
        Decimal: Effective investment amount.
    """
    if pair in exempt_pairs:
        return initial_investment
    else:
        return initial_investment * (Decimal('1') - brokerage_fee)

def execute_routes(filter_combinations: list, orderbook_data: dict, initial_quantity: Decimal) -> None:
    """
    Execute the triangular arbitrage routes and calculate the profit/loss.

    Args:
        filter_combinations (list): List of combinations to execute.
        orderbook_data (dict): Order book data.
        initial_quantity (Decimal): Initial quantity to invest.
    """

    for combination in filter_combinations:
        #type = combination['combo_type']
        initial = combination['initial']
        operation = combination['operation']
        a_symbol = combination['a_symbol']
        b_symbol = combination['b_symbol']
        #c_symbol = combination['c_symbol']
        combined = combination['combined']
        n = combination['n']

        #efec_initial = get_effective_investment(initial_quantity, a_symbol, BROKERAGE_FEE)

        if operation[0] == "B":
            A_B_price, A_quantity = calculate_effective_price(orderbook_data[a_symbol]['a'], initial_quantity)
        elif operation[0] == "S":
            A_B_price, A_quantity = calculate_effective_price(orderbook_data[a_symbol]['b'], initial_quantity)

        #A_quantity = get_effective_investment(A_quantity, b_symbol, BROKERAGE_FEE)

        if operation[1] == "B":
            B_B_price, B_quantity = calculate_effective_price(orderbook_data[b_symbol]['a'], A_quantity)
        elif operation[1] == "S":
            B_B_price, B_quantity = calculate_effective_price(orderbook_data[b_symbol]['b'], A_quantity)

        #B_quantity = get_effective_investment(B_quantity, c_symbol, BROKERAGE_FEE)

        if operation[2] == "B":
            C_B_price, C_quantity = calculate_effective_price(orderbook_data[b_symbol]['a'], B_quantity)
        if operation[2] == "S":
            C_B_price, C_quantity = calculate_effective_price(orderbook_data[b_symbol]['b'], B_quantity)

        profit = C_quantity - initial_quantity

        if profit > 0:
            print(f"Oportunity found! {n} {combined} profit amount = {profit} profit coin = {initial}")

def read_combinations(filename: str) -> list:
    """
    Read combinations from a JSON file.

    Args:
        filename (str): Filename to read from.

    Returns:
        list: List of combinations.
    """
    with open(filename, 'r') as file:
        return json.load(file)

def filter_combinations(combinations: list, initial_coin: str) -> list:
    """
    Filter combinations based on the initial coin.

    Args:
        combinations (list): List of combinations.
        initial_coin (str): Initial coin to filter by.

    Returns:
        list: Filtered list of combinations.
    """
    return [combo for combo in combinations if combo['initial'] == initial_coin]