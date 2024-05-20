from data_fetcher import RyanairWrapper
from data_saver import SaveToJson
from price_predictor import TicketPricePredictor


if __name__ == '__main__':
    obj = RyanairWrapper()
    prices = obj.get_flight_prices('Poznań', 'Mediolan-Bergamo')

    json_saver = SaveToJson('prices')
    json_saver.save_prices(prices)
    prices = json_saver.read_prices()
    for price in prices:
        print(price)

    predictor = TicketPricePredictor()
    predictor.fit(prices)
    predicts = []
    for i in range(0, 50, 5):
        predicts.append(predictor.predict(i))

    for i in range(len(predicts)):
        print(f'Predicted price for {i*5} days ahead: {predicts[i][0]}')
