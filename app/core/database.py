import motor.motor_asyncio
from app.core.config import settings

# MongoDB connection setup
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

# Collections
users_collection = db.users
widgets_collection = db.widgets