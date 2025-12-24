"""
Singleton Pattern for Database Connection
Ensures only one database instance exists throughout the application lifecycle
"""

class DatabaseSingleton:
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
        return cls._instance
    
    def initialize(self, db_instance):
        """Initialize the database instance (called once from app.py)"""
        print(f"DEBUG: Initializing singleton {id(self)} with db {id(db_instance)}")
        DatabaseSingleton._db = db_instance
    
    def get_db(self):
        """Get the singleton database instance"""
        if DatabaseSingleton._db is None:
            print(f"DEBUG: get_db failed for singleton {id(self)}. _db is None.")
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return DatabaseSingleton._db

    
    @property
    def session(self):
        """Convenience property to access db.session"""
        return self.get_db().session

# Global singleton instance
db_singleton = DatabaseSingleton()

