import os
import mysql.connector
from dotenv import load_dotenv
from typing import Tuple

class DBConnector:
    def __init__(self) -> None:
        load_dotenv()
        DB_HOST = os.getenv("DB_HOST")
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_DATABASE = os.getenv("DB_DATABASE")
        SSL_PATH = os.getenv("SSL_PATH")
        # PROD
        self._db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            # ssl_verify_identity=True,
            # ssl_ca=SSL_PATH,
        )
        # DEV 
        # self._db = mysql.connector.connect(
        #         user="root",
        #         # password=DB_PASSWORD,
        #         host="127.0.0.1",
        #         port=3306,
        #         database="cvboost-db"
        #         )
    
    def __del__(self) -> None:
        self._db.close()
    
    def post(self, query: str, values: Tuple[str, ...]) -> int | None:
        try:
            cursor = self._db.cursor(dictionary=True)
            cursor.execute(query, values)
            self._db.commit()
            item_id = cursor.lastrowid
        except Exception as e:
            print("Error in DBConnector.post(): ", e)
            return None
        finally:
            cursor.close()
        
        return item_id
        

    def get(self, query: str,  values: Tuple[str, ...]) -> list:
        try:
            cursor = self._db.cursor(dictionary=True)
            cursor.execute(query, values)
            result = cursor.fetchall()
        except Exception as e:
            print("Error in DBConnector.get(): ", e)
            return []
        finally:
            cursor.close()

        return result
    
    def delete(self, query: str) -> bool:
        try:
            cursor = self._db.cursor(dictionary=True)
            cursor.execute(query)
            self._db.commit()
        except Exception as e:
            print("Error in DBConnector.post(): ", e)
            return False
        finally:
            cursor.close()
        
        return True
