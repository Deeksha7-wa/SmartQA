from app.db.session import Base, engine
import app.db.init_models  # 🔥 ensures models + tables are loaded

print("Tables:", Base.metadata.tables.keys())
print("✅ Tables created successfully")