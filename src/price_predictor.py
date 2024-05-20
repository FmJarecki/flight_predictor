import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime


class TicketPricePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_names = None

    def prepare_data(self, data):
        today = datetime.strptime(data[0]['day'], '%Y-%m-%d')
        prepared_data = []

        for entry in data:
            for date, price in entry['prices'].items():
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                days_diff = (date_obj - today).days
                prepared_data.append([days_diff, float(price)])

        df = pd.DataFrame(prepared_data, columns=['days_diff', 'price'])
        self.feature_names = ['days_diff']
        return df

    def fit(self, data):
        df = self.prepare_data(data)
        X = df[['days_diff']]
        y = df['price']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)

        score = self.model.score(X_test, y_test)
        print(f'Model R^2 score: {score}')

    def predict(self, days_ahead):
        return self.model.predict(np.array([[days_ahead]]))
