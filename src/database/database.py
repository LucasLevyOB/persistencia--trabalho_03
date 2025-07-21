import os
import motor.motor_asyncio

_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DATABASE_URL"))
db = _client["app_mobilidade_urbana"]