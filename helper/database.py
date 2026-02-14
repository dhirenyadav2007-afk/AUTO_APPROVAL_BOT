import motor.motor_asyncio
from datetime import datetime


class MongoDB:
    _instances = {}

    def __new__(cls, uri: str, db_name: str):
        if (uri, db_name) not in cls._instances:

            instance = super().__new__(cls)

            # Mongo Client
            instance.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            instance.db = instance.client[db_name]

            # Collections
            instance.users = instance.db["users"]
            instance.join_requests = instance.db["join_requests"]
            instance.premium = instance.db["premium"]

            cls._instances[(uri, db_name)] = instance

        return cls._instances[(uri, db_name)]

    # ───────────────────────────────
    # ✅ USER FUNCTIONS
    # ───────────────────────────────

    async def present_user(self, user_id: int) -> bool:
        """Check if user exists in DB"""
        return bool(await self.users.find_one({"_id": user_id}))

    async def add_user(self, user_id: int):
        """Insert new user into DB"""
        if not await self.present_user(user_id):
            await self.users.insert_one(
                {
                    "_id": user_id,
                    "joined_at": datetime.utcnow(),
                    "banned": False
                }
            )

    async def total_users(self) -> int:
        """Return total number of users"""
        return await self.users.count_documents({})

    async def full_userbase(self) -> list[int]:
        """Return all user IDs"""
        cursor = self.users.find({})
        return [doc["_id"] async for doc in cursor]

    # ───────────────────────────────
    # 🚫 BAN SYSTEM
    # ───────────────────────────────

    async def ban_user(self, user_id: int):
        """Ban a user"""
        await self.users.update_one(
            {"_id": user_id},
            {"$set": {"banned": True}}
        )

    async def unban_user(self, user_id: int):
        """Unban a user"""
        await self.users.update_one(
            {"_id": user_id},
            {"$set": {"banned": False}}
        )

    async def is_banned(self, user_id: int) -> bool:
        """Check ban status"""
        doc = await self.users.find_one({"_id": user_id})
        return doc.get("banned", False) if doc else False

    # ───────────────────────────────
    # ⭐ PREMIUM SYSTEM
    # ───────────────────────────────

    async def add_premium(self, user_id: int):
        """Add premium user"""
        await self.premium.update_one(
            {"_id": user_id},
            {"$set": {"since": datetime.utcnow()}},
            upsert=True
        )

    async def remove_premium(self, user_id: int):
        """Remove premium user"""
        await self.premium.delete_one({"_id": user_id})

    async def is_pro(self, user_id: int) -> bool:
        """Check if user is premium"""
        return bool(await self.premium.find_one({"_id": user_id}))

    # ───────────────────────────────
    # ✅ JOIN REQUEST TRACKING
    # ───────────────────────────────

    async def add_join_request(self, user_id: int, chat_id: int):
        """Store join request as pending"""
        await self.join_requests.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {
                "$set": {
                    "status": "pending",
                    "submitted_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def approve_join_request(self, user_id: int, chat_id: int):
        """Mark join request approved"""
        await self.join_requests.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_at": datetime.utcnow()
                }
            }
        )

    async def get_join_status(self, user_id: int, chat_id: int):
        """Get join request status"""
        doc = await self.join_requests.find_one(
            {"user_id": user_id, "chat_id": chat_id}
        )
        return doc.get("status") if doc else None

    async def total_join_requests(self, user_id: int) -> int:
        """Count total join requests submitted by user"""
        return await self.join_requests.count_documents(
            {"user_id": user_id}
        )
