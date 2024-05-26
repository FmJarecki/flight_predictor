from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
import pandas as pd


class LTSMTicketPricePredictor:
    def __init__(self, data: pd.DataFrame):
        self._x_train, self._x_test, self._y_train, self._y_test = [], [], [], []
        self._model = Sequential()
        pd_lstm_data = self.fetch_data(data)
        self.prepare_data(pd_lstm_data)
        self.build_model()

    def predict(self, x_test):
        y_pred = self._model.predict(x_test)
        y_pred = (y_pred > 0.5).astype(int)
        return y_pred

    def train(self):
        history = self._model.fit(self._x_train,
                                  self._y_train,
                                  epochs=30,
                                  batch_size=1,
                                  validation_data=(self._x_test, self._y_test))

    def build_model(self):
        self._model = Sequential([
            LSTM(100, activation='tanh', input_shape=(1, 1)),
            Dense(1, activation='sigmoid')
        ])
        self._model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

    def prepare_data(self, data: pd.DataFrame):
        scaler = MinMaxScaler()
        x = scaler.fit_transform(data['days_to_flight'].values.reshape(-1, 1))
        x = x.reshape((x.shape[0], 1, x.shape[1]))
        y = data['prices_increased'].values.reshape(-1, 1)
        self._x_train, self._x_test, self._y_train, self._y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Changes the data read from json to the input for LSTM
    @staticmethod
    def fetch_data(data: pd.DataFrame) -> pd.DataFrame:
        data['day'] = pd.to_datetime(data['day'], format='%d-%m-%Y')
        data['flight_date'] = pd.to_datetime(data['flight_date'], format='%d-%m-%Y')

        lstm_data = pd.DataFrame(columns=['days_to_flight', 'prices_increased'])

        last_price = None
        last_day = data.iloc[0]['flight_date']
        for index, row in data.iterrows():
            current_day = row['flight_date']
            current_price = row['price']

            if current_day != last_day:
                price_increase = current_price - last_price
                if price_increase > 0:
                    price_increased = 1.0
                else:
                    price_increased = 0.0

                day_to_flight = abs(pd.to_datetime(row['day'], format='%d-%m-%Y') -
                                    pd.to_datetime(current_day, format='%d-%m-%Y'))

                new_row = {'days_to_flight': day_to_flight.days,
                           'prices_increased': price_increased}
                lstm_data = pd.concat([lstm_data, pd.DataFrame([new_row])], ignore_index=True)

            last_price = current_price
            last_day = current_day

        return lstm_data
