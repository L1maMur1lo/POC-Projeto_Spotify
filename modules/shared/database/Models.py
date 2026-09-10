from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


# Tabela intermediaria de relação entre musicas e artistas
music_artist_association = Table(
    'music_artist_association',
    Base.metadata,
    Column('music_reference', String, ForeignKey('musics.reference'), primary_key=True),
    Column('artist_reference', String, ForeignKey('artists.reference'), primary_key=True),
)


class ArtistsModel(Base):
    """Tabela contendo os dados dos artistas"""

    __tablename__ = 'artists'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    # ID do artista no spotify
    reference: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    profile_img_url: Mapped[Optional[str]] = mapped_column(String, init=False)

    # Lista de objetos contendo os dados da musica relacionados ao artista
    # Tipo de relação (Many-to-Many)
    musics: Mapped[List[MusicsModel]] = relationship(
        'MusicsModel',
        secondary=music_artist_association,
        back_populates='artists',
        default_factory=list,
        lazy='selectin',
        init=False,
    )

    @property
    def musics_titles(self) -> List[str]:
        """Retorna dinamicamente apenas os títulos de todas as músicas deste artista."""
        return [music.title for music in self.musics]


class MusicsModel(Base):
    """Tabela contendo os dados da musica"""

    __tablename__ = 'musics'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    # ID da track no spotify
    reference: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String, nullable=False, init=False)

    # Lista de objetos contendo os dados dos artistas relacionados a musica
    # Tipo de relação (Many-to-Many)
    artists: Mapped[List[ArtistsModel]] = relationship(
        'ArtistsModel',
        secondary=music_artist_association,
        back_populates='musics',
        default_factory=list,
        lazy='selectin',
        init=False,
    )

    # Tempo da musica em milisegundos
    duration: Mapped[int] = mapped_column(Integer, nullable=False, init=False)
    album_img_url: Mapped[str] = mapped_column(String, init=False)

    # Associando a musica a execução
    # Tipo de relação: (One-to-Many)
    executions: Mapped[List[ExecutionsModel]] = relationship(
        'ExecutionsModel',
        default_factory=list,
        back_populates='music',
        cascade='all, delete-orphan',
    )

    @property
    def artists_names(self) -> List[str]:
        """Retorna dinamicamente a lista de nomes dos artistas vinculados a esta música."""
        return [artist.name for artist in self.artists]

    @property
    def executions_date(self) -> List[str]:
        """Retorna uma lista com as datas de execução"""
        dates = []
        for execution in self.executions:
            date = execution.played_at.strftime('%d-%m-%Y %H:%M:%S')
            dates.append(date)

        return dates


class ExecutionsModel(Base):
    """Tabela contendo os dados de execução das musicas do usuario"""

    __tablename__ = 'executions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)

    # Chave estrangeira da tabela musics
    music_reference: Mapped[str] = mapped_column(
        ForeignKey('musics.reference', ondelete='CASCADE', onupdate='CASCADE'), nullable=False
    )

    ms_played: Mapped[int] = mapped_column(Integer, nullable=False, init=False)
    played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, init=False)
    offline: Mapped[Optional[bool]] = mapped_column(Boolean, server_default='false', init=False)
    source: Mapped[Optional[str]] = mapped_column(String, default='Unknown', init=False)

    # Associando a execução a musica
    # Tipo de relação: (Many-to-One)
    music: Mapped[MusicsModel] = relationship(
        'MusicsModel',
        lazy='selectin',
        back_populates='executions',
        init=False,
    )

    @property
    def music_name(self) -> str:
        """Retorna o nome da musica associada a execução"""
        return self.music.title


class QueueModel(Base):
    """Tabela para controle de dados"""

    __tablename__ = 'queue'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    # ID da track no spotify
    track: Mapped[str] = mapped_column(String, nullable=False)
    ms_played: Mapped[int] = mapped_column(Integer, nullable=False)
    played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    offline: Mapped[Optional[bool]] = mapped_column(Boolean, server_default='false', default=False)
    timestamp_off: Mapped[Optional[BigInteger]] = mapped_column(BigInteger, default=0)
    # Origem dos dados
    source_file: Mapped[str] = mapped_column(String, default='')
    source_file_row: Mapped[int] = mapped_column(Integer, default='')
    # Status para controle
    status: Mapped[Optional[str]] = mapped_column(String, server_default='in_queue', init=False)
