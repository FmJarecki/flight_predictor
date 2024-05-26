import json
from datetime import datetime
import os
import pandas as pd


def get_data_folder_path(folder_name: str = 'data'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, '..', folder_name))


def remove_spaces_and_convert(val: str) -> float:
    return float(val.replace(' ', ''))


class JsonHandler:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def save_prices(self, prices: dict, create_backup: bool = True):
        existing_data = self.read_prices()
        if create_backup:
            existing_data.to_json(f'{get_data_folder_path()}/{self.file_name}_backup.json',
                                  orient='records',
                                  lines=True)

        new_rows = []
        day = datetime.now().strftime('%d-%m-%Y')
        for flight_date, price in prices.items():
            new_rows.append({"day": day, "flight_date": flight_date, "price": remove_spaces_and_convert(price)})
        new_df = pd.DataFrame(new_rows)
        new_df["day"] = new_df["day"]
        new_df["flight_date"] = new_df["flight_date"]

        df = pd.concat([existing_data, new_df], ignore_index=True)

        df.to_json(f'{get_data_folder_path()}/{self.file_name}.json', orient='records', lines=True)

    def read_prices(self) -> pd.DataFrame:
        try:
            with open(f'{get_data_folder_path()}/{self.file_name}.json', 'r') as file:
                data_list = [json.loads(line) for line in file]

                df = pd.DataFrame(data_list)
                df['day'] = df['day']
                df['flight_date'] = df['flight_date']
                return df

        except FileNotFoundError:
            print('File not found.')
            return pd.DataFrame([])
        except json.decoder.JSONDecodeError:
            print('File was empty.')
            return pd.DataFrame([])

