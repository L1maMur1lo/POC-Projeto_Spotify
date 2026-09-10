import base64
import logging

import requests

from modules.shared.Settings import settings


class SpotifyAPI:
    SUCESS: int = 200
    EXPIRED: int = 401
    TOO_MANY: int = 429
    NO_CONTENT: int = 204
    SERVICE_UNAVALABLE: int = 503
    MAX_TRYES: int = 3

    def __init__(self):
        logging.getLogger('Spotify')

        self.__client_id = settings.CLIENT_ID
        self.__client_secret = settings.CLIENT_SECRET
        self.__refresh_token = settings.REFRESH_TOKEN

        self.__token: str = self.get_token()
        self.num_tryes: int = 0

    def get_token(self):
        logging.info('Gerando novo Token de acesso...')

        # Unindo 'ClientID' + 'ClientSecret'
        # Convertendo em 'bytes'
        authBytes = (self.__client_id + ':' + self.__client_secret).encode('utf-8')

        # Criando 'string' de 'autorização'
        # Codificada em base64
        authStr = str(base64.b64encode(authBytes), 'utf-8')

        # Criando 'cabeçalho' para request (post)
        header = {
            'Authorization': 'Basic ' + authStr,
            'content-type': 'application/x-www-form-urlencoded',
        }

        # Criando 'conteudo' para request (post)
        content = {'grant_type': 'refresh_token', 'refresh_token': self.__refresh_token}

        # Requisitando informações
        response = requests.post(url=settings.TOKEN_URL, headers=header, data=content)

        # Verificando se a request foi 'Sucesso'
        if response.status_code == self.SUCESS:
            # Reescrevendo Token
            self.__token = f'Bearer {response.json()["access_token"]}'
            logging.info('Token gerado com sucesso')

        else:
            # Criando erro
            error = f'{response.status_code} - {response.reason}'
            logging.error(f'\n{"-" * 100}\n{error}\n{"-" * 100}')
            # Forçando erro
            raise Exception(error)

    def get_track(self, id: str) -> dict:
        logging.info('Solicitando "Track"...')

        # Alterando a URL
        url = settings.TRACKS_URL + f'/{id}'

        # Requisitando informações
        response = requests.get(url=url, headers={'Authorization': self.__token})

        # Verificando se a request foi 'Sucesso'
        if response.status_code == self.SUCESS:
            logging.info('Sucesso na solicitação')
            self.num_tryes = 0
            return response.json()

        # Verificando se a resposta foi 'token expirado'
        elif response.status_code == self.EXPIRED:
            if self.num_tryes < self.MAX_TRYES:
                logging.warning('Token expirado')
                self.num_tryes += 1
                # Renovando token
                self.get_token()

                # Executando novamente o metodo
                return self.get_several_tracks(id)

        else:
            # Só aparece caso a renovação do token falhe mais de 3 vezes
            if self.num_tryes >= self.MAX_TRYES:
                logging.warning('Número de tentativas excedido')

            # Criando erro
            error = f'{response.status_code} - {response.reason}'
            logging.error(f'\n{"-" * 100}\n{error}\n{"-" * 100}')
            # Forçando erro
            raise Exception(error)

    def get_several_tracks(self, ids: list[str]) -> dict:
        logging.info('Solicitando "Tracks"...')

        # Muda a variavel
        str_tracks: str = ','.join(ids)
        # Alterando a URL
        url = settings.TRACKS_URL + f'?ids={str_tracks}'

        # Requisitando informações
        response = requests.get(url=url, headers={'Authorization': self.__token})

        # Verificando se a request foi 'Sucesso'
        if response.status_code == self.SUCESS:
            logging.info('Sucesso na solicitação')
            self.num_tryes = 0
            return response.json()

        # Verificando se a resposta foi 'token expirado'
        elif response.status_code == self.EXPIRED:
            if self.num_tryes < self.MAX_TRYES:
                logging.warning('Token expirado')
                self.num_tryes += 1
                # Renovando token
                self.get_token()

                # Executando novamente o metodo
                return self.get_several_tracks(ids)

        else:
            # Só aparece caso a renovação do token falhe mais de 3 vezes
            if self.num_tryes >= self.MAX_TRYES:
                logging.warning('Número de tentativas excedido')

            # Criando erro
            error = f'{response.status_code} - {response.reason}'
            logging.error(f'\n{"-" * 100}\n{error}\n{"-" * 100}')
            # Forçando erro
            raise Exception(error)
