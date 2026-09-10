import logging
from sqlalchemy import select, update
from modules.shared.database.Models import ArtistsModel
from sqlalchemy.orm import Session
from modules.shared.database.Connection import get_session
from modules.shared.api.Spotify import SpotifyAPI

class Complete_Data:
    SIZE_BATCH = 50

    def __init__(self):
        self.spotify = SpotifyAPI()
        self.session: Session = get_session()

    def chunked(self, iterable: list[str], size: int):
        for i in range(0, len(iterable), size):
            yield iterable[i : i + size]

    def execute(self):

        # Pegando a url das imagens do perfil do artista
        statement = select(ArtistsModel.reference).where(ArtistsModel.profile_img_url.is_(None))
        missing = self.session.execute(statement).scalars().all()

        for batch in self.chunked(missing, self.SIZE_BATCH):
            response = self.spotify.get_several_artists(batch)

            for artist_data in response['artists']:
                try:
                    img_url = artist_data['images'][0]['url']
                except Exception:
                    img_url = None

                statement = (
                    update(ArtistsModel)
                    .where(ArtistsModel.reference == artist_data['id'])
                    .values(profile_img_url=img_url)
                )

                self.session.execute(statement)
                logging.debug(f'Adicionada a imagem do artista: {artist_data["name"]}')

            self.session.commit()

if __name__ == '__main__':
    logFileName = 'Complete_Data.log'

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s | %(module)s: %(message)s',
        encoding='utf-8',
        handlers=[logging.FileHandler(logFileName, encoding='utf-8'), logging.StreamHandler()],
    )

    # Desativa os logs de DEBUG da biblioteca urllib3
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    main = Complete_Data()
    main.execute()
