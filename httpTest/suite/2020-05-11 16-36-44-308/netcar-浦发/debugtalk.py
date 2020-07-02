# -*- coding:utf-8 -*-
import redis,pymysql
from faker import Faker
import requests, json, random, pyDes, base64, re, time


fake = Faker(locale='zh_CN')
# trade端数据库配置
TRADE_MYSQL_CONFIG = {'host':'111.202.106.110','port':18010,'user':'netcar','password':'feajiEgerjaieo','db':'netCar'}
# pipe端数据库配置
PIPE_MYSQL_CONFIG = {'host':'111.202.106.110','port':18010,'user':'netcar','password':'feajiEgerjaieo','db':'netCarPlatform'}
# redis配置
REDIS_CONFIG = {'host':'111.202.106.110','port':18011,'password':'5W4Jl6MN','db':0}


def mysql_execute(sql, params=None, is_fetchone=True,server='trade'):
    """
    数据库SQL执行器
    :param is_fetchone:
    :param logging:
    :return:
    """
    def mysql_connect(host,port,user,password,db):
        """
        链接数据库
        :return:
        """
        connection = pymysql.connect(host=host, port=port, user=user,password=password, db=db, autocommit=True, charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        return connection

    if server == 'trade':
        connection = mysql_connect(host=TRADE_MYSQL_CONFIG['host'],port=TRADE_MYSQL_CONFIG['port'],user=TRADE_MYSQL_CONFIG['user'],password=TRADE_MYSQL_CONFIG['password'],db=TRADE_MYSQL_CONFIG['db'])
    else:
        connection = mysql_connect(host=PIPE_MYSQL_CONFIG['host'],port=PIPE_MYSQL_CONFIG['port'],user=PIPE_MYSQL_CONFIG['user'],password=PIPE_MYSQL_CONFIG['password'],db=PIPE_MYSQL_CONFIG['db'])

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            if is_fetchone:
                result = cursor.fetchone()
                return result
            else:
                result = cursor.fetchall()
                return result
    except:
        connection.rollback()
    finally:
        connection.close()


def redis_execute():
    """
    redis执行器
    :return:
    """
    r = redis.Redis(host=REDIS_CONFIG['host'], port=REDIS_CONFIG['port'], db=REDIS_CONFIG['db'], password=REDIS_CONFIG['password'])
    return r


def query_customer_detail(user_mobile):
    """
    查询用户信息
    :param mobile:
    :return:
    """
    try:
        detail = mysql_execute('select * from tbl_trade_customer where mobile=%s', params=(user_mobile))
    except:
        detail = None
    if detail:
        return detail
    else:
        return None
    
    
def create_phone_number():
    """
    生成数据库中不存在的新手机号码
    :return:
    """
    while True:
        mobile = fake.phone_number()
        user_detail = query_customer_detail(mobile)
        if user_detail == None:
            break
    return mobile
    
    
def trade_random_login(user_mobile=None):
    """
    Trade端随机登录
    :return:
    """
    token = None
    login_url = 'http://testzx.ywsk.cn:38000/netCar/page/customer/login'
    if user_mobile:
        data = {'respCode':'0000','respMsg':'','interfaceId':'','version':'','resDateTime':'','signType':'','sign':'',
            'outUuId':'','data.code':user_mobile,'data.bizParams':''}
    else:
        random_mobile = create_phone_number()
        data = {'respCode': '0000','respMsg': '','interfaceId': '','version': '','resDateTime': '','signType': '','sign': '','outUuId': '','data.code': random_mobile,'data.bizParams': ''}
    response = requests.post(url=login_url, data=data, headers={'Content-Type':'application/x-www-form-urlencoded'})
    redirect_url = response.url
    response_code = str(re.findall(r"code=(.+?)&", str(redirect_url))[0])
    if response_code == '0':
        token = str(re.findall(r"token=(.+?)&", str(redirect_url))[0])
    return token
    

def clean_user_contact(user_mobile):
    """
    清除用户常用联系人
    :param args:
    :return:
    """
    cus_id = mysql_execute(sql='select id from tbl_trade_customer where mobile=%s', params=(user_mobile))
    mysql_execute('delete from tbl_trade_contact where cus_id=%s', params=cus_id['id'])
    
def clean_user_common_address(user_mobile):
    """
    清除用户常用地址
    :param args:
    :return:
    """
    cus_id = mysql_execute(sql='select id from tbl_trade_customer where mobile=%s', params=(user_mobile))
    mysql_execute('delete from tbl_trade_common_address where cus_id=%s', params=cus_id['id'])
    redis_execute().delete('netCar:CUSTOMER_COMMON_ADDRESS:{0}'.format(cus_id['id']))

def sleep(t):
    """
    等待时间
    """
    time.sleep(t)
    
def close_user_sign_force_pay(user_mobile):
    """
    关闭用户强制扣款
    :param args:
    :return:
    """
    cus_id = mysql_execute(sql='select id from tbl_trade_customer where mobile=%s', params=(user_mobile))['id']
    mysql_execute(sql='update tbl_trade_customer set force_pay_flag=1 where mobile=%s', params=(user_mobile))
    redis_execute().delete('netCar:USERINFO:{0}'.format(cus_id))
