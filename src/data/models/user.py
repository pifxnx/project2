from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    fullname: Mapped[str]
    hashed_password: Mapped[str]
    organization: Mapped[str] = mapped_column(nullable=True)
