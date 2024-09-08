from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.engine import URL
import config.settings as settings


def get_url():
    return URL.create(
        drivername=settings.ASYNC_DRIVER_NAME,
        username=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        database=settings.DB_NAME,
        port=settings.DB_PORT
    )


engine = create_async_engine(get_url(), echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
