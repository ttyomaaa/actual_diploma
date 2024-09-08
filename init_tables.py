# import asyncio
# from db.engine import engine
# from db.models.models import Base
#
#
# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#
# asyncio.run(init_models())
