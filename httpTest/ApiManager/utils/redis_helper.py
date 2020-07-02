# -*- coding:utf-8 -*-
from HttpRunnerManager.settings import PLATFORM_REDIS_CONFIG
from ApiManager.utils.base_logger import BaseLogger
import redis


logger = BaseLogger(__name__).get_logger()


def redis_execute(trade=False,pipe=False):
    """
    redis执行器
    :return:
    """
    if trade:
        r = redis.Redis(host='111.202.106.110', port=18011, db=0,password='5W4Jl6MN')
    elif pipe:
        r = redis.Redis(host='111.202.106.110', port=18011, db=1, password='5W4Jl6MN')
    else:
        r = redis.Redis(host=PLATFORM_REDIS_CONFIG['host'], port=PLATFORM_REDIS_CONFIG['port'], db=PLATFORM_REDIS_CONFIG['db'], password=PLATFORM_REDIS_CONFIG['password'])
    logger.info('Connect redis success!')
    return r

# Spdb支付最大轮循次数
SPDB_PAYCB_ROUNT_MAX_NUMBER_KEY = 'spdb_paycb_round_max_number'
# Spdb支付当前轮循次数
SPDB_PAYCB_ROUNT_CURRENT_NUMBER_KEY = 'spdb_paycb_round_current_number'
# 首汽订单乘客上车时间
SQ_START_SERVICE_TIME_KEY = 'sq_start_service_time_'
# 首汽订单乘客下车时间
SQ_END_SERVICE_TIME_KEY = 'sq_end_service_time_'
# 测试套件存储
TEST_SUITE_KEY = 'test_suite_list'
# 曹操司机端APP指令KEY
CAOCAO_DRIVER_COMMAND = 'cc_driver_command'

# 相关监控key
KEY_LIST = []
MONITORING_RUNNING_KEY = 'monitoring_running'
FORBIDDEN_CREATE_ORDER_MONITORING_KEY = 'forbidden_create_order_monitoring'
KEY_LIST.append(FORBIDDEN_CREATE_ORDER_MONITORING_KEY)
NOTICE_MANAGER_MONITORING_KEY = 'notice_manager_monitoring'
KEY_LIST.append(NOTICE_MANAGER_MONITORING_KEY)
ACTIVITY_RULE_MANAGER_MONITORING_KEY = 'activity_rule_manager_monitoring'
KEY_LIST.append(ACTIVITY_RULE_MANAGER_MONITORING_KEY)
ACTIVITY_MANAGER_MONITORING_KEY = 'activity_manager_monitoring'
KEY_LIST.append(ACTIVITY_MANAGER_MONITORING_KEY)
CONTACT_MONITORING_KEY = 'contact_monitoring'
KEY_LIST.append(CONTACT_MONITORING_KEY)
BLACKLIST_MONITORING_KEY = 'blacklist_manager_monitoring'
KEY_LIST.append(BLACKLIST_MONITORING_KEY)
COUPON_RECHARGE_MONITORING_KEY = 'coupon_recharge_monitoring'
KEY_LIST.append(COUPON_RECHARGE_MONITORING_KEY)
IMAGE_MONITORING_KEY = 'image_manager_monitoring'
KEY_LIST.append(IMAGE_MONITORING_KEY)
ACTIVITY_DISPLAY_MANAGER_MONITORING_KEY = 'activity_display_manager_monitoring'
KEY_LIST.append(ACTIVITY_DISPLAY_MANAGER_MONITORING_KEY)
FLIGHT_INFO_MONITORING = 'flight_info_monitoring'
KEY_LIST.append(FLIGHT_INFO_MONITORING)
SYSTEM_CANCEL_ORDER_MONITORING_KEY = 'system_cancel_order_monitoring'
KEY_LIST.append(FLIGHT_INFO_MONITORING)
COMMON_ADDRESS_MONITORING_KEY = 'common_address_monitoring'
KEY_LIST.append(COMMON_ADDRESS_MONITORING_KEY)

