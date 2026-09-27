from app.db.base import Base
from app.db.database import engine
from app.models import Order, OrderItem, Payment


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("PostgreSQL tables created successfully")


if __name__ == "__main__":
    init_db()