import logging
import time
import datetime

import psycopg2

logger = logging.getLogger(__name__)
RETRY_COUNT = 5


class SensorDataStore:
    def __init__(self, host, database, user):
        self.host = host
        self.database = database
        self.user = user
        self._db_conn = None

    def _connect(self, retry_counter=0):
        logger.info('Connecting to DB')

        try:
            self._db_conn = psycopg2.connect(user=self.user, host=self.host, database=self.database)
            logger.info('Connected to DB')
        except psycopg2.OperationalError:
            logger.exception('Failed to connect to DB')

            if retry_counter > RETRY_COUNT:
                time.sleep(1200)
            else:
                time.sleep(10)
            retry_counter += 1
            self._connect(retry_counter)

    def store_sensor_values(self, project_code, source_addr, data_type: str, data_value):
        sql = """
        INSERT INTO env_sensor(recv_date,
                                project_code,
                                source_addr,
                                data_type,
                                data_value) 
        VALUES(%s,%s,%s,%s,%s)
        """
        if not self._db_conn:
            self._connect()
        cur = self._db_conn.cursor()
        cur.execute(sql, (datetime.datetime.now(), int(project_code), int(source_addr), data_type, float(data_value)))

        self._db_conn.commit()
        cur.close()

    def destroy(self):
        self._db_conn.close()
