import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


class LTSMTicketPricePredictor:
    def __init__(self, data: pd.DataFrame, seq_len: int = 5):
        self._sequence_length = seq_len
        self._scaler = StandardScaler()
        self._x_train, self._x_test = np.array([]), np.array([]),
        self._y_train, self._y_test = np.array([]), np.array([])
        self._model = Sequential()
        pd_lstm_data = self.fetch_data(data)
        self.prepare_data(pd_lstm_data)
        self.build_model()

    def predict(self, day: int, prices_before: list):
        days_until_flight = [i for i in range(day, day+5)]

        new_data = np.column_stack((prices_before, days_until_flight))
        new_data = self._scaler.transform(new_data)

        new_sequence = new_data.reshape((1, self._sequence_length, self._x_train.shape[2]))

        prediction = self._model.predict(new_sequence)

        price_movement = 'up' if prediction[0][0] > 0.5 else 'down'
        print(f'Ticket price for {day} days will go {price_movement}.')

    def evaluate(self):
        loss, accuracy = self._model.evaluate(self._x_test, self._y_test)
        print(f'Accuracy: {accuracy * 100:.2f}%')

    def train(self):
        history = self._model.fit(self._x_train, self._y_train, epochs=50, validation_split=0.2, batch_size=2)

    def build_model(self):
        self._model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self._x_train.shape[1], self._x_train.shape[2])),
            LSTM(50),
            Dense(1, activation='sigmoid')
        ])

        self._model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def prepare_data(self, df: pd.DataFrame):

        def create_sequences(data: np.array):
            x_data, y_data = [], []
            for i in range(len(data) - self._sequence_length):
                x_data.append(data[i:i + self._sequence_length, :-1])
                y_data.append(data[i + self._sequence_length, -1])
            return np.array(x_data), np.array(y_data)

        x, y = create_sequences(df.values)

        self._x_train, self._x_test, self._y_train, self._y_test = train_test_split(x,
                                                                                    y,
                                                                                    test_size=0.2,
                                                                                    random_state=42)

    # Changes the data read from json to the input for LSTM
    def fetch_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Convert dates to datetime objects
        df['day'] = pd.to_datetime(df['day'], format='%d-%m-%Y')
        df['flight_date'] = pd.to_datetime(df['flight_date'], format='%d-%m-%Y')

        # Calculate the number of days from 'day' to 'flight_date'
        df['days_until_flight'] = (df['flight_date'] - df['day']).dt.days

        # Shift the price column to get the next day's price
        df['next_day_price'] = df['price'].shift(-1)

        # Remove rows where we don't have the next day's price
        df = df.dropna()

        # Determine if the price will go up (1) or down (0)
        df = df.assign(price_direction=(df['next_day_price'] > df['price']).astype(int))

        # Select relevant columns
        df = df[['price', 'days_until_flight', 'price_direction']]

        # Normalize the features
        df[['price', 'days_until_flight']] = self._scaler.fit_transform(df[['price', 'days_until_flight']])

        return df
