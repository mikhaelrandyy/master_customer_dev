from pydantic import BaseModel

class AccessToken(BaseModel):
    active: bool
    scope: str | None
    exp: int | None
    client_id: str | None
    authorities: list[str] | None
    projects: list[str] | None
    segment: list[str] | None
    token: str | None
    name: str | None