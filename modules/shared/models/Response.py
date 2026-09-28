from pydantic import BaseModel, Field, model_validator

class TEPM(BaseModel):
    """Total Executions Per Month (EPM)"""

    jan: int = 0
    feb: int = 0
    mar: int = 0
    apr: int = 0
    may: int = 0
    jun: int = 0
    jul: int = 0
    aug: int = 0
    sep: int = 0
    oct: int = 0
    nov: int = 0
    dec: int = 0
    total: int = 0

    @model_validator(mode="after")
    def calculate_total(self) -> "TEPM":
        """Calcula automaticamente o total se não for fornecido ou atualiza-o."""
        months = [
            self.jan, self.feb, self.mar, self.apr, 
            self.may, self.jun, self.jul, self.aug, 
            self.sep, self.oct, self.nov, self.dec
        ]
        if self.total == 0:
            self.total = sum(months)
        return self


class Artist(BaseModel):
    """Base Artist"""

    reference: str
    name: str
    profile_img_url: str


class Music(BaseModel):
    """Base Music"""

    reference: str
    title: str
    album_img_url: str


class RMEPM(Music):
    """Rank Music Executions Per Month (RMEPM)"""

    executions: TEPM = Field(default_factory=TEPM)


class RAEPM(Artist):
    """Rank Artists Executions Per Month (RAEPM)"""

    executions: TEPM = Field(default_factory=TEPM)
    musics: list[RMEPM] = Field(default_factory=list)


class LRAEPM(BaseModel):
    """List Rank Artists Executions Per Month (LRAEPM)"""

    artists: list[RAEPM] = Field(default_factory=list)

class GMTA(Music, TEPM):
    pass

class GATR(Artist, TEPM):
    pass