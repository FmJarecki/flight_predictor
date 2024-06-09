import pandas as pd
import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self, data: pd.DataFrame):
        self._grouped = pd.DataFrame([])
        self.fetch_data(data)
        data_to_visualize = self.calculate()
        self.visualize_data(data_to_visualize)

    @staticmethod
    def visualize_data(data: dict):

        plt.figure(figsize=(10, 6))
        for key, values in data.items():
            plt.plot(values.index, values.values, label=key)

        plt.title('Poznań-Bergamo route')
        plt.xlabel('Days until flight')
        plt.ylabel('Price [PLN]')
        plt.legend()

        plt.grid(True)
        plt.show()

    def calculate(self) -> dict:
        mean_prices = self._grouped['price'].mean()

        median_prices = self._grouped['price'].median()

        data_to_visualize = {'mean': mean_prices, 'median': median_prices}

        return data_to_visualize

    def fetch_data(self, df: pd.DataFrame):
        df['day'] = pd.to_datetime(df['day'], format='%d-%m-%Y')
        df['flight_date'] = pd.to_datetime(df['flight_date'], format='%d-%m-%Y')

        df['days_until_flight'] = (df['flight_date'] - df['day']).dt.days
        df['next_day_price'] = df['price'].shift(-1)

        df = df.dropna()

        self._grouped = df[['price', 'days_until_flight']].groupby('days_until_flight')

        # for name, group in self._grouped:
        #    print(f"Day until flight: {name}")
        #    print(group)
