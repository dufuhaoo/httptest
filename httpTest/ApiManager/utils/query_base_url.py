# -*- coding:utf-8 -*-
from HttpRunnerManager.settings import DATABASES
from ApiManager.utils.base_logger import BaseLogger
import pymysql,json


logger = BaseLogger(__name__).get_logger()



def _testplatform_mysql_execute(sql, params=None, is_fetchone=True):
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

    connection = mysql_connect(host=DATABASES['default']['HOST'],port=int(DATABASES['default']['PORT']),user=DATABASES['default']['USER'],password=DATABASES['default']['PASSWORD'],db=DATABASES['default']['NAME'])
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


def _query_base_url(env_name):
    """
    根据环境名称查询地址
    :param env_name:
    :return:
    """
    base_url = _testplatform_mysql_execute('select base_url from EnvInfo where env_name=%s',params=(env_name))
    return base_url['base_url']


# PF_API_BASE_URL = _query_base_url('pf-sit-接口地址前缀')
# # SPDB支付回调接口地址
# SPDB_PAYCB_URL = _query_base_url('pf-sit-支付回调接口地址')
# # SPDB全员免密接口地址
# SPDB_SECRET_SETTINGS_URL = _query_base_url('pf-sit-全员免密接口地址')
# # 首汽订单回调地址
# SQ_CHANNEL_CALLBACK_URL = _query_base_url('sit-首汽订单回调地址')
# # 首汽工单回调地址
# SQ_CHANNEL_COMPLAINT_CALLBACK_URL = _query_base_url('sit-首汽工单回调地址')
# # 神州回调加密地址
# SZ_ENCRYPTION_URL = _query_base_url('sit-神州工单回调加密地址')
# # 神州工单回调地址
# SZ_CHANNEL_COMPLAINT_CALLBACK_URL = _query_base_url('sit-神州工单回调地址')
# # 神州订单变更请求地址
# SZ_CHANGE_ORDER_STATUS_URL = _query_base_url('sit-神州订单变更请求地址')
# # 神州获取access_token地址
# SZ_ACCESS_TOKEN_URL = _query_base_url('pf-神州获取Token地址')
# # SPDB红包充值接口地址
# SPDB_COUPON_RECHARGE_API_URL = _query_base_url('pf-sit-红包充值接口地址')
# # trade端redis配置
# TRADE_REDIS_CONFIG = eval(_query_base_url('pf-sit-trade-redis配置'))
# # pipe端redis配置
# PIPE_REDIS_CONFIG = eval(_query_base_url('pf-sit-pipe-redis配置'))
# # trade端数据库配置
# TRADE_MYSQL_CONFIG = eval(_query_base_url('pf-sit-trade数据库配置'))
# # pipe端数据库配置
# PIPE_MYSQL_CONFIG = eval(_query_base_url('pf-sit-pipe数据库配置'))
# # 中信trade端redis配置
# ZX_TRADE_REDIS_CONFIG = eval(_query_base_url('zx-sit-trade-redis配置'))
# # 中信pipe端redis配置
# ZX_PIPE_REDIS_CONFIG = eval(_query_base_url('zx-sit-pipe-redis配置'))
# # 中信trade端数据库配置
# ZX_TRADE_MYSQL_CONFIG = eval(_query_base_url('zx-sit-trade数据库配置'))
# # 中信pipe端数据库配置
# ZX_PIPE_MYSQL_CONFIG = eval(_query_base_url('zx-sit-pipe数据库配置'))
# # 神州pipe回调地址
# SZ_CHANNEL_CALLBACK_URL = _query_base_url('sit-神州pipe订单回调地址')
#
