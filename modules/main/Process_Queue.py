import logging
import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from modules.shared.api.Spotify import SpotifyAPI
from modules.shared.database.Connection import get_session
from modules.shared.database.Models import ArtistsModel, ExecutionsModel, MusicsModel, QueueModel
from modules.shared.database.Services import (
    get_queue_size,
    get_to_process,
    missing_tracks,
    reject_queue_items,
    search_artist,
    search_execution,
    search_music,
    update_queue_status,
)


class Process_Queue:
    SIZE_BATCH = 50
    SIZE_PROCESS = 1000

    def __init__(self):

        self.spotify = SpotifyAPI()
        self.session: Session = get_session()
        self.total_process = get_queue_size(self.session)

        self.process = 0

    def chunked(self, iterable: list[str], size: int):
        for i in range(0, len(iterable), size):
            yield iterable[i : i + size]

    def create_obj_music(self, data: dict) -> MusicsModel:
        try:
            music = MusicsModel(reference=data['id'])
            music.title = data['name']

            music.artists = [
                search_artist(self.session, artist['id'])
                or ArtistsModel(reference=artist['id'], name=artist['name'])
                for artist in data['artists']
            ]

            music.duration = data['duration_ms']
            music.album_img_url = data['album']['images'][0]['url']

            return music

        except Exception:
            logging.error(f'Não foi possivel criar o objeto Musica: {data["id"]}')
            raise

    def create_music(self, item: MusicsModel) -> None:
        try:
            if search_music(self.session, item.reference) is None:
                self.session.add(item)
                logging.debug(f'Musica: {item.title} adicionada a tabela')

            else:
                logging.debug(f'Musica: {item.title} já existe na tabela')

        except Exception:
            self.session.rollback()
            logging.error(f'Não foi possivel criar a Musica: {item.title}')
            raise

    def create_obj_execution(self, data: QueueModel) -> ExecutionsModel:
        try:
            execution = ExecutionsModel(music_reference=data.track)
            execution.ms_played = data.ms_played

            if data.offline:
                if data.timestamp_off > 10000000000: 
                    timestamp_segundos = data.timestamp_off / 1000.0
                else:
                    timestamp_segundos = data.timestamp_off
                
                execution.played_at = datetime.fromtimestamp(timestamp_segundos, tz=timezone.utc)
            
            else:
                execution.played_at = data.played_at

            execution.offline = data.offline

            # Criado para controle de origem
            source_file = data.source_file
            year = re.search(r'\d{4}', source_file).group()
            row = f'{data.source_file_row:05d}'
            stream = 'Audio' if 'Audio' in source_file else 'Video'
            # Adicionando controle de origem
            execution.source = f'History_{row}{year}_{stream}'

            # Adicionando musica relacionado a execução
            execution.music = search_music(self.session, execution.music_reference)

            return execution

        except Exception:
            logging.error(f'Não foi possivel criar o objeto Execução: {data.track}')
            raise

    def create_execution(self, item: ExecutionsModel) -> None:
        try:
            if search_execution(self.session, item) is None:
                self.session.add(item)
                logging.debug(f'Execução: {item.source} adicionada a tabela')

            else:
                logging.debug(f'Execução: {item.source} já existe na tabela')

        except Exception:
            self.session.rollback()
            logging.error(f'Não foi possivel criar a Execução: {item.source}')
            raise

    def execute(self):
        try:
            # Muda o status de valores com execução menor que 30 segundo
            # Para as execuções, musicas e artistas referentes a esses dados não serem adicionadas
            # (Regra de Negocio)
            total_rejected = reject_queue_items(self.session)
            self.session.commit()
            logging.info(f'{total_rejected} Linhas foram rejeitadas por não cumprirem a regra')

            # Buscando as informações das musicas que não existem na tabela
            missing = missing_tracks(self.session)
            if not missing:
                logging.info('Não há musicas faltando na tabela')

            else:
                # Buscando os dados das musicas que não existem na tabela
                for batch in self.chunked(missing, self.SIZE_BATCH):
                    response = self.spotify.get_several_tracks(batch)

                    for music_data in response['tracks']:
                        music = self.create_obj_music(music_data)
                        self.create_music(music)

                        try:
                            self.session.commit()
                        except Exception:
                            logging.error('Não foi possivel salvar as alterações no banco')
                            raise

            # Processando as execuções
            for _ in range(0, self.total_process, self.SIZE_PROCESS):
                queue_items = get_to_process(self.session, limit=self.SIZE_PROCESS)

                if not queue_items:
                    logging.info('Não há itens na fila para processar')

                for queue_data in queue_items:
                    execution = self.create_obj_execution(queue_data)
                    self.create_execution(execution)

                    update_queue_status(self.session, queue_data, 'processed')
                    self.process += 1

                logging.info(f'Numero de execuções atual: {self.process}')
                self.session.commit()
                logging.info(f'Execuções salvas')

        except Exception as error:
            self.session.rollback()
            logging.error(error)
            raise

        finally:
            logging.info(f'Numero de execuções totais: {self.process}')
            self.session.commit()
            self.session.close()


if __name__ == '__main__':
    logFileName = 'Process_Queue.log'

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s | %(module)s: %(message)s',
        encoding='utf-8',
        handlers=[logging.FileHandler(logFileName, encoding='utf-8'), logging.StreamHandler()],
    )

    # Desativa os logs de DEBUG da biblioteca urllib3
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    main = Process_Queue()
    main.execute()
