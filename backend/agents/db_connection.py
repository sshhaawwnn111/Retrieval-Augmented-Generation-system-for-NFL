import psycopg2
from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _writer_pool = None
    _reader_pool = None
    
    @classmethod
    def initialize_pools(cls, dbname, user, password, writer_host, reader_host, port=5432, min_conn=1, max_conn=10):
        """
        Initialize separate connection pools for writer and reader endpoints
        """
        if cls._writer_pool is None:
            try:
                cls._writer_pool = psycopg2.pool.SimpleConnectionPool(
                    min_conn,
                    max_conn,
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=writer_host,
                    port=port,
                    connect_timeout=10,
                    options='-c statement_timeout=30000'
                )
                logger.info(f"Writer connection pool created for {writer_host}:{port}/{dbname}")
            except Exception as e:
                logger.error(f"Failed to create writer pool: {e}")
                raise
        
        if cls._reader_pool is None:
            try:
                cls._reader_pool = psycopg2.pool.SimpleConnectionPool(
                    min_conn,
                    max_conn,
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=reader_host,
                    port=port,
                    connect_timeout=10,
                    options='-c statement_timeout=30000'
                )
                logger.info(f"Reader connection pool created for {reader_host}:{port}/{dbname}")
            except Exception as e:
                logger.error(f"Failed to create reader pool: {e}")
                raise
    
    def __init__(self, use_writer=False):
        """
        Initialize database connection
        
        Args:
            use_writer: If True, use writer pool. If False, use reader pool.
        """
        if not DatabaseConnection._writer_pool or not DatabaseConnection._reader_pool:
            raise Exception("Connection pools not initialized. Call initialize_pools() first.")
        
        self.use_writer = use_writer
        self.conn = None
        self.cursor = None
        
        # Get connection from appropriate pool
        if use_writer:
            self.conn = DatabaseConnection._writer_pool.getconn()
            logger.info("Connected to writer endpoint")
        else:
            self.conn = DatabaseConnection._reader_pool.getconn()
            logger.info("Connected to reader endpoint")
        
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        """
        Execute a query and return results
        
        Automatically detects write operations and validates pool usage
        """
        query_upper = query.strip().upper()
        is_write_operation = any(query_upper.startswith(op) for op in ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER'])
        
        # Validate that write operations use writer pool
        if is_write_operation and not self.use_writer:
            raise Exception("Write operation attempted on reader connection. Use use_writer=True")
        
        try:
            self.cursor.execute(query, params)
            if query_upper.startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return None
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self.conn.rollback()
            raise

    def close(self):
        """
        Return connection to appropriate pool
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if self.use_writer:
                DatabaseConnection._writer_pool.putconn(self.conn)
                logger.info("Writer connection returned to pool")
            else:
                DatabaseConnection._reader_pool.putconn(self.conn)
                logger.info("Reader connection returned to pool")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    @classmethod
    def close_all_connections(cls):
        """
        Close all connections in both pools (use on shutdown)
        """
        if cls._writer_pool:
            cls._writer_pool.closeall()
            logger.info("All writer connections closed")
        if cls._reader_pool:
            cls._reader_pool.closeall()
            logger.info("All reader connections closed")