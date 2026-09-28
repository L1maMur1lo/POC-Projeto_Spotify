import logging
import os

import numpy as np
import pandas as pd

from modules.shared.database.Connection import get_session
from modules.shared.database.Models import QueueModel
from modules.shared.database.Services import search_in_queue
from modules.shared.Settings import settings


class Create_Queue:
    COLUMN_TIMESTAMP = 'ts'
    COLUMN_OFFLINE = 'offline'
    COLUMN_MS_PLAYED = 'ms_played'
    COLUMN_TRACK = 'spotify_track_uri'
    COLUMN_OFFLINE_TS = 'offline_timestamp'

    def __init__(self):
        self.data_path = settings.DATA_PATH

        self.session = get_session()

        # Variaveis de controle
        self.rows_sucess = 0
        self.rows_existing = 0

    def create_queue_item(self, item: QueueModel):
        try:
            if search_in_queue(self.session, item) is None:
                self.session.add(item)
                self.rows_sucess += 1
                logging.debug(f'File: {item.source_file}, Row: {item.source_file_row}')
                logging.debug('Item adicionado a fila')
            else:
                self.rows_existing += 1
                logging.debug(f'File: {item.source_file}, Row: {item.source_file_row}')
                logging.debug('Item já existe na fila')

        except Exception:
            logging.error('Não foi possivel criar o item')
            raise

    def execute(self):
        """Insere os dados a serem processados em uma 'fila'."""

        logging.info('Executando criacao da fila')

        files = [file for file in os.listdir(self.data_path) if file.endswith('.json')]

        for file in files:
            if 'processado' in file:
                continue

            dataframe = pd.read_json(f'{self.data_path}/{file}')
            columns = dataframe[
                [
                    self.COLUMN_TIMESTAMP,
                    self.COLUMN_TRACK,
                    self.COLUMN_MS_PLAYED,
                    self.COLUMN_OFFLINE,
                    self.COLUMN_OFFLINE_TS,
                ]
            ]

            columns[self.COLUMN_OFFLINE_TS] = columns[self.COLUMN_OFFLINE_TS].replace(np.nan, 0)
            dataframe = columns.dropna(subset=[self.COLUMN_TRACK])

            # Variaveis de controle
            self.rows_sucess = 0
            self.rows_existing = 0
            rows_total = len(dataframe)

            for index, item in dataframe.iterrows():
                item[self.COLUMN_TRACK] = str(item[self.COLUMN_TRACK]).rsplit(':', maxsplit=1)[-1]
                if type(item[self.COLUMN_OFFLINE]) is not bool:
                    item[self.COLUMN_OFFLINE] = False

                queue = QueueModel(
                    track=item[self.COLUMN_TRACK],
                    ms_played=item[self.COLUMN_MS_PLAYED],
                    played_at=item[self.COLUMN_TIMESTAMP],
                    offline=item[self.COLUMN_OFFLINE],
                    timestamp_off=item[self.COLUMN_OFFLINE_TS],
                    source_file=file,
                    source_file_row=index + 1,
                )

                logging.debug(f'{"-" * 100}')

                self.create_queue_item(queue)

                logging.debug(f'Total: {index + 1} of {rows_total}')

            logging.info(f'{"-" * 100}')
            logging.info(f'Ja existente: {self.rows_existing}')
            logging.info(f'Sucesso: {self.rows_sucess}')
            logging.info(f'Total: {rows_total}')

            self.session.commit()
            os.rename(
                f'{self.data_path}/{file}',
                f'{self.data_path}/{file.replace(".json", "")}-processado.json',
            )

            logging.info(f'Arquivo: {file} processado!')

        logging.info(f'{"-" * 100}')


if __name__ == '__main__':
    logFileName = 'Create_Queue.log'

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s | %(module)s: %(message)s',
        encoding='utf-8',
        handlers=[logging.FileHandler(logFileName, encoding='utf-8'), logging.StreamHandler()],
    )

    main = Create_Queue()
    main.execute()
