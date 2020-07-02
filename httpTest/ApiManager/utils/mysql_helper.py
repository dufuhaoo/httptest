# -*- coding:utf-8 -*-
from ApiManager.utils.base_logger import BaseLogger
from HttpRunnerManager.settings import DATABASES
import pymysql


logger = BaseLogger(__name__).get_logger()



def mysql_execute(sql, params=None, is_fetchone=True,trade=False,platform=False,bank=1):
    """
    数据库SQL执行器
    :param is_fetchone:
    :param logging:
    :return:
    bank = 1 浦发
    bank = 2 中信
    """
    connection = None
    def mysql_connect(host,port,user,password,db):
        """
        链接数据库
        :return:
        """
        connection = pymysql.connect(host=host, port=port, user=user,password=password, db=db, autocommit=True, charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        return connection
    if platform:
        connection = mysql_connect(host=DATABASES['default']['HOST'],port=int(DATABASES['default']['PORT']),user=DATABASES['default']['USER'],password=DATABASES['default']['PASSWORD'],db=DATABASES['default']['NAME'])
    else:
        if bank == 1: # 浦发
            if trade:
                connection = mysql_connect(host='111.202.106.110',port=18010,user='netcar',password='feajiEgerjaieo',db='netcar')
            else:
                connection = mysql_connect(host='111.202.106.110',port=18010,user='netcar',password='feajiEgerjaieo',db='netcarplatform')
        elif bank == 2: # 中信
            if trade:
                connection = mysql_connect(host='47.101.69.189', port=3306, user='dbs_pufa_wr',password='Zpv_Uy89Zva3h7@103', db='netcarcitic')
            else:
                connection = mysql_connect(host='47.101.69.189', port=3306, user='dbs_pufa_wr',password='Zpv_Uy89Zva3h7@103', db='netcarplatform')
        elif bank == 3: # 广发
            if trade:
                connection = mysql_connect(host='47.103.85.168', port=3306, user='netcar', password='feajiEgerjaieo',db='netcarcgb')
            else:
                connection = mysql_connect(host='47.103.85.168', port=3306, user='netcar', password='feajiEgerjaieo',db='netcarplatform')
    try:
        with connection.cursor() as cursor:
            logger.info(sql)
            cursor.execute(sql, params)
            if is_fetchone:
                result = cursor.fetchone()
                logger.info(result)
                return result
            else:
                result = cursor.fetchall()
                logger.info(result)
                return result
    except:
        connection.rollback()
    finally:
        connection.close()
