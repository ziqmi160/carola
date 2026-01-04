import oracledb
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _connection = None
    
    @staticmethod
    def get_connection():
        """Get or create database connection"""
        if Database._connection is None:
            try:
                Database._connection = oracledb.connect(
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    dsn=DB_CONFIG['dsn']
                )
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Error connecting to database: {e}")
                raise
        return Database._connection
    
    @staticmethod
    def close_connection():
        """Close database connection"""
        if Database._connection:
            Database._connection.close()
            Database._connection = None
            logger.info("Database connection closed")
    
    @staticmethod
    def execute_query(query, params=None, fetch=True):
        """Execute a query and return results"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                columns = [desc[0].upper() for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows] if columns else []
                return result
            else:
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Query error: {e}")
            raise
        finally:
            cursor.close()
    
    @staticmethod
    def execute_many(query, params_list):
        """Execute a query multiple times with different parameters"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error(f"Batch query error: {e}")
            raise
        finally:
            cursor.close()

