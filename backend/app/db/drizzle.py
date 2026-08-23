from drizzle_orm import Database
from app.core.config import settings

# Global Drizzle database instance using Neon URL
db = Database(settings.NEON_DATABASE_URL)
