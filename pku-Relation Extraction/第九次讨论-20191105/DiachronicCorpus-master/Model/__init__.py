import atexit
import pymysql
from pymysql import InterfaceError, OperationalError

port = 3306

db = pymysql.connect('localhost', 'root', '', 'DiachronicCorpus', use_unicode=True, charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor, port=port)
print(db.host, db.port)
print('database connected.')


def sql_execute(cursor, sql, args=None):
    try:
        return cursor.execute(sql, args)
    except (InterfaceError, OperationalError, OSError):
        print('db connection timeout, auto reconnect.')
        db.connect()
        return cursor.execute(sql, args)


@atexit.register
def close_connection():
    db.close()
    print('database disconnected.')

