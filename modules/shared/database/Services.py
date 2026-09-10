from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from modules.shared.database.Models import ArtistsModel, ExecutionsModel, MusicsModel, QueueModel

VALID_TIME = 30000


def search_in_queue(session: Session, item: QueueModel) -> bool:
    statement = select(QueueModel).where(
        QueueModel.source_file == item.source_file,
        QueueModel.source_file_row == item.source_file_row,
    )

    result: QueueModel = session.execute(statement).scalar_one_or_none()
    return result


def reject_queue_items(session: Session) -> int:
    statement = (
        update(QueueModel)
        .where(QueueModel.ms_played < VALID_TIME, QueueModel.status == 'in_queue')
        .values(status='rejected')
    )

    result = session.execute(statement)
    return result.rowcount


def missing_tracks(session: Session) -> list[str]:
    statement = (
        select(QueueModel.track)
        .outerjoin(MusicsModel, QueueModel.track == MusicsModel.reference)
        .where(QueueModel.status == 'in_queue', MusicsModel.reference.is_(None))
        .group_by(QueueModel.track)
    )

    result = session.execute(statement).scalars().all()
    return result


def search_music(session: Session, id: str) -> MusicsModel:
    statement = select(MusicsModel).where(MusicsModel.reference == id)

    result = session.execute(statement).scalar_one_or_none()
    return result


def search_artist(session: Session, id: str) -> ArtistsModel:
    statement = select(ArtistsModel).where(ArtistsModel.reference == id)

    result = session.execute(statement).scalar_one_or_none()
    return result


def get_queue_size(session: Session) -> int:
    statement = select(func.count(QueueModel.track)).where(
        QueueModel.ms_played >= VALID_TIME, QueueModel.status == 'in_queue'
    )

    result = session.execute(statement).scalar()
    return result


def get_to_process(session: Session, limit: int = 1000, offset: int = 0) -> list[QueueModel]:
    statement = (
        select(QueueModel).where(QueueModel.status == 'in_queue').limit(limit).offset(offset)
    )

    result: list[QueueModel] = session.execute(statement).scalars().all()
    return result


def search_execution(session: Session, item: ExecutionsModel) -> ExecutionsModel:
    statement = select(ExecutionsModel).where(
        ExecutionsModel.music_reference == item.music_reference,
        ExecutionsModel.played_at == item.played_at,
        ExecutionsModel.source == item.source,
    )

    result = session.execute(statement).scalar_one_or_none()
    return result


def update_queue_status(session: Session, item: QueueModel, new_status: str) -> None:
    statement = update(QueueModel).where(QueueModel.id == item.id).values(status=new_status)

    session.execute(statement)
