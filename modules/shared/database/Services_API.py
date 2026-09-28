from datetime import datetime

from sqlalchemy import func, select, desc, case, extract
from sqlalchemy.orm import Session

from modules.shared.database.Connection import get_session

from modules.shared.database.Models import ArtistsModel, ExecutionsModel, MusicsModel
from modules.shared.models.Response import GMTA, GATR


def get_artists_top_rank(limit: int = 10, offset: int = 0) -> list[GATR]:
    session:Session = get_session()

    statement = (
        select(
            ArtistsModel.reference,
            ArtistsModel.name,
            ArtistsModel.profile_img_url,
            # Execuções por mes (colunas para cada mes)
            func.count(case((extract('month', ExecutionsModel.played_at) == 1, ExecutionsModel.id), else_=None)).label('jan'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 2, ExecutionsModel.id), else_=None)).label('feb'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 3, ExecutionsModel.id), else_=None)).label('mar'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 4, ExecutionsModel.id), else_=None)).label('apr'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 5, ExecutionsModel.id), else_=None)).label('may'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 6, ExecutionsModel.id), else_=None)).label('jun'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 7, ExecutionsModel.id), else_=None)).label('jul'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 8, ExecutionsModel.id), else_=None)).label('aug'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 9, ExecutionsModel.id), else_=None)).label('sep'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 10, ExecutionsModel.id), else_=None)).label('oct'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 11, ExecutionsModel.id), else_=None)).label('nov'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 12, ExecutionsModel.id), else_=None)).label('dec'),
            # Execuções por mes (coluna para o total)
            func.count(ExecutionsModel.id).label('total_ano')
        )
        .select_from(ArtistsModel)
        .join(ArtistsModel.musics)
        .join(MusicsModel.executions)
        .where(
            ExecutionsModel.played_at.between('2026-01-01', '2026-12-31')
        )
        .group_by(ArtistsModel.reference, ArtistsModel.name, ArtistsModel.profile_img_url)
        .order_by(desc('total_ano'))
        .limit(limit)
        .offset(offset)
    )

    result = session.execute(statement).mappings().all()

    session.close()
    return [GATR(**row) for row in result]

def get_music_top_artist(artist_reference: str, limit: int = 10, offset: int = 0) -> list[GMTA]:
    session = get_session()
    
    statement = (
        select(
            MusicsModel.reference,
            MusicsModel.title,
            MusicsModel.album_img_url,
            # Execuções por mes (colunas para cada mes)
            func.count(case((extract('month', ExecutionsModel.played_at) == 1, ExecutionsModel.id), else_=None)).label('jan'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 2, ExecutionsModel.id), else_=None)).label('feb'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 3, ExecutionsModel.id), else_=None)).label('mar'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 4, ExecutionsModel.id), else_=None)).label('apr'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 5, ExecutionsModel.id), else_=None)).label('may'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 6, ExecutionsModel.id), else_=None)).label('jun'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 7, ExecutionsModel.id), else_=None)).label('jul'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 8, ExecutionsModel.id), else_=None)).label('aug'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 9, ExecutionsModel.id), else_=None)).label('sep'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 10, ExecutionsModel.id), else_=None)).label('oct'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 11, ExecutionsModel.id), else_=None)).label('nov'),
            func.count(case((extract('month', ExecutionsModel.played_at) == 12, ExecutionsModel.id), else_=None)).label('dec'),
            # Execuções por mes (coluna para o total)
            func.count(ExecutionsModel.id).label('total_ano')
        )
        .join(MusicsModel.artists)
        .join(MusicsModel.executions)
        .where(
            ArtistsModel.reference == artist_reference,
            ExecutionsModel.played_at.between('2026-01-01', '2026-12-31')
        )
        .group_by(MusicsModel.reference, MusicsModel.title, MusicsModel.album_img_url)
        .order_by(desc('total_ano'))
        .limit(limit)
        .offset(offset)
    )

    result = session.execute(statement).mappings().all()

    session.close()
    return [GMTA(**row) for row in result]