from motor import motor_asyncio
from config import load_config

config = load_config()


class MongoDB:
    client = None
    db = None

    @staticmethod
    def get_client():
        if MongoDB.client is None:
            # MONGODB_USERNAME = config.db.username
            # MONGODB_PASSWORD = config.db.password
            MONGODB_HOSTNAME = config.db.host
            MONGODB_PORT = config.db.port

            # MongoDB.client = motor_asyncio.AsyncIOMotorClient("mongodb://{}:{}@{}:{}".format(
            #     MONGODB_USERNAME, MONGODB_PASSWORD, MONGODB_HOSTNAME, str(MONGODB_PORT)))
            MongoDB.client = motor_asyncio.AsyncIOMotorClient("mongodb://{}:{}".format(
                MONGODB_HOSTNAME, str(MONGODB_PORT)))

        return MongoDB.client

    @staticmethod
    def get_data_base():
        if MongoDB.db is None:
            client = MongoDB.get_client()
            MongoDB.db = client[config.db.database]

        return MongoDB.db

    @staticmethod
    async def add_group(group_name: str, group_id: str):
        await MongoDB.get_data_base().groups.update_one(
            filter={'group_id': group_id},
            update={"$set": {"group_name": group_name}},
            upsert=True,
        )
