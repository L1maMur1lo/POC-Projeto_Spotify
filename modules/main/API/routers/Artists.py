from http import HTTPStatus

from fastapi import APIRouter

from modules.shared.models.Response import LRAEPM, RAEPM, RMEPM, TEPM
from modules.shared.database.Services_API import get_artists_top_rank, get_music_top_artist

router = APIRouter(prefix='/artists', tags=['Artists'])


@router.get('/rank', status_code=HTTPStatus.OK, response_model=LRAEPM)
async def get_rank_artists():
    response = LRAEPM()

    for artist in get_artists_top_rank():
        new_artist = RAEPM(
            reference=artist.reference,
            name=artist.name,
            profile_img_url=artist.profile_img_url
        )

        for music in get_music_top_artist(artist.reference):
            new_music = RMEPM(
                reference=music.reference,
                title=music.title,
                album_img_url=music.album_img_url
            )

            music_execution_per_month = TEPM(
                jan=music.jan,
                feb=music.feb,
                mar=music.mar,
                apr=music.apr,
                may=music.may,
                jun=music.jun,
                jul=music.jul,
                aug=music.aug,
                sep=music.sep,
                oct=music.oct,
                nov=music.nov,
                dec=music.dec
            )
            new_music.executions = music_execution_per_month

            new_artist.musics.append(new_music)

        artist_execution_per_month = TEPM(
            jan=artist.jan,
            feb=artist.feb,
            mar=artist.mar,
            apr=artist.apr,
            may=artist.may,
            jun=artist.jun,
            jul=artist.jul,
            aug=artist.aug,
            sep=artist.sep,
            oct=artist.oct,
            nov=artist.nov,
            dec=artist.dec
        )
        new_artist.executions = artist_execution_per_month

        response.artists.append(new_artist)

    return response
