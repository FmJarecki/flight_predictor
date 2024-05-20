import json
from datetime import datetime
import os


def get_data_folder_path(folder_name: str = 'data'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, '..', folder_name))


class SaveToJson:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def save_prices(self, prices: dict, create_backup: bool = True):
        existing_data = self.read_prices()
        if create_backup:
            with open(f'{get_data_folder_path()}/{self.file_name}_backup.json', 'w') as json_file:
                json.dump(existing_data, json_file)

        current_datetime = datetime.now()
        new_data = {
            'day': current_datetime.strftime('%Y-%m-%d'),
            'time': current_datetime.strftime('%H:%M:%S'),
            'prices': prices
        }
        existing_data.append(new_data)

        with open(f'{get_data_folder_path()}/{self.file_name}.json', 'w') as json_file:
            json.dump(existing_data, json_file)

    def read_prices(self) -> list:
        try:
            with open(f'{get_data_folder_path()}/{self.file_name}.json', 'r') as file:
                existing_data = json.load(file)
            return existing_data
        except FileNotFoundError:
            print('File not found.')
            return []
        except json.decoder.JSONDecodeError:
            print('File was empty.')
            return []

