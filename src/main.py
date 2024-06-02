from data_fetcher import RyanairWrapper
from storage_manager import JsonHandler
from price_predictor import LTSMTicketPricePredictor


if __name__ == '__main__':
    ryanair_fetcher = RyanairWrapper('Poznań', 'Mediolan-Bergamo')
    # prices = ryanair_fetcher.get_flight_prices(92)
    # print(prices)
    json_saver = JsonHandler('prices')
    # json_saver.save_prices(prices)
    loaded_prices = json_saver.read_prices()

    nn = LTSMTicketPricePredictor(loaded_prices)
    nn.train()
    nn.evaluate()

    day_to_predict = 10
    prices = ryanair_fetcher.get_flight_prices(day_to_predict+2)
    prices_before_flight = [value for value in prices.values()][-5:]
