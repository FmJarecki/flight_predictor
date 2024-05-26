from data_fetcher import RyanairWrapper
from storage_manager import JsonHandler
from price_predictor import LTSMTicketPricePredictor


if __name__ == '__main__':
    # obj = RyanairWrapper()
    # prices = obj.get_flight_prices('Poznań', 'Mediolan-Bergamo')
    # print(prices)
    json_saver = JsonHandler('prices')
    # json_saver.save_prices(prices)
    prices = json_saver.read_prices()

    nn = LTSMTicketPricePredictor(prices)
    nn.train()
    #nn.evaluate()
    #nn.predict(2)
