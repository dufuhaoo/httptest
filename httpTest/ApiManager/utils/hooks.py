# -*- coding:utf-8 -*-
from ApiManager.utils.mysql_helper import mysql_execute
from ApiManager.utils.redis_helper import redis_execute
from ApiManager.utils.faker_data import BaseFaker
import time,random



def pipe_open_all_channel():
    """
    pipe平台开启全部渠道
    :return:
    """
    mysql_execute('update tbl_platform_channel_sort set isOpen=1')


def get_channel_manager_detail(channel_mark,channel_type=None,vehicle_type=None):
    """
    获取渠道管理详情
    :return:
    """
    if not channel_type and not vehicle_type:
        result = mysql_execute('select * from tbl_platform_channel_sort where channelMark=%s',params=(channel_mark), is_fetchone=False)
    elif not vehicle_type:
        result = mysql_execute('select * from tbl_platform_channel_sort where channelMark=%s and channelType=%s', params=(channel_mark,channel_type),is_fetchone=False)
    elif not channel_type:
        result = mysql_execute('select * from tbl_platform_channel_sort where channelMark=%s and vehicleType=%s', params=(channel_mark,vehicle_type),is_fetchone=False)
    else:
        result = mysql_execute('select * from tbl_platform_channel_sort where channelMark=%s and channelType=%s and vehicleType=%s',params=(channel_mark,channel_type,vehicle_type))
    return result


def get_sheet_config_settings_detail(config_name):
    """
    获取sheet平台基础配置管理项详情
    :param name:
    :return:
    """
    detail = mysql_execute('SELECT * FROM tbl_trade_config_setting WHERE config_name=%s',params=(config_name),trade=True)
    return detail


def clean_notice():
    """
    清除通知管理数据
    :return:
    """
    mysql_execute('truncate tbl_trade_notice',trade=True)
    redis_execute().delete('netCar:NOTICE_REDIS_CACHE_KEY:')


def clean_activity_rule():
    """
    清除活动细则
    :return:
    """
    mysql_execute('truncate tbl_trade_activity_rules_config',trade=True)
    redis_execute().delete('netCar:IMAGE_CACHE_KEY:1')
    redis_execute().delete('netCar:IMAGE_CACHE_KEY:2')

def get_active_activity_list():
    """
    获取当前生效的活动
    :return:
    """
    activity_list = mysql_execute('select * from tbl_trade_activity where activity_status=1',is_fetchone=False)
    return activity_list

def fix_activity_status(activity_id,status):
    """
    修改活动状态
    :param activity_id:
    :param status:
    :return:
    """
    mysql_execute('update tbl_trade_activity set activity_status=%s where activity_id=%s',params=(status,activity_id))

def delete_activity(activity_id,sign_id):
    """
    删除活动
    :param activity_id:
    :param status:
    :return:
    """
    detail = mysql_execute('select * from tbl_trade_activity where activity_id=%s',params=(activity_id),trade=True)
    if detail:
        redis_execute(trade=True).delete('netCar:ACTIVITY:ACTIVITY_ID_{0}'.format(detail['id']))
        mysql_execute('delete from tbl_trade_activity where activity_id=%s',params=(activity_id),trade=True)
        redis_execute(trade=True).delete('netCar:ACTIVITY:ACTIVITY_INFO')
        mysql_execute('delete from tbl_trade_activity_config where sign_id=%s',params=(sign_id),trade=True)
        mysql_execute('delete from tbl_trade_activity_detail where activity_id=%s',params=(activity_id),trade=True)
        mysql_execute('delete from tbl_trade_activity_customer_relation where activity_id=%s',params=(activity_id),trade=True)
        mysql_execute('delete from tbl_trade_activity_customer_record where activity_id=%s',params=(activity_id),trade=True)
        mysql_execute('delete from tbl_trade_coupon_recharge_record where activity_id=%s',params=(activity_id),trade=True)


def get_random_activity_id():
    """
    随机生成数据库中不存在的活动ID
    :return:
    """
    now_time = int(time.time())
    while True:
        activity_id = str(now_time) + str(random.randint(1000,9999))
        query_result = mysql_execute('select * from tbl_trade_activity where activity_id=%s',params=(activity_id))
        if query_result is None:
            return activity_id


def get_trade_customer(number):
    """
    获取数据库中已存在的用户信息
    :return:
    """
    customer_list = mysql_execute('select * from tbl_trade_customer as c left join tbl_trade_order as a on c.mobile = a.mobile where order_status in (11,28,24,21) order by c.create_time DESC LIMIT %s ',params=(number),trade=True,is_fetchone=False)
    print(customer_list)

    return customer_list


def get_new_mobile():
    """
    获取新手机号，确保数据库中该手机号不存在
    :return:
    """
    while True:
        user_mobile = BaseFaker().create_phone_number()
        try:
            user_detail = mysql_execute('select * from tbl_trade_customer where mobile=%s', params=(user_mobile))
        except:
            user_detail = None
        if user_detail:
            continue
        else:
            return user_mobile

def get_coupon_recharge_record(batch_id):
    """
    根据批次号查询充值记录
    :param batch_id:
    :return:
    """
    result = mysql_execute('select * from tbl_trade_coupon_recharge_record where batch_id=%s',params=(batch_id),trade=True,is_fetchone=False)
    return result

def clean_user_contact(mobile):
    """
    清除用户常用联系人
    :param args:
    :return:
    """
    cus_id = mysql_execute(sql='select id from tbl_trade_customer where mobile=%s', params=(mobile),trade=True)
    if cus_id:
        mysql_execute('delete from tbl_trade_contact where cus_id=%s', params=cus_id['id'],trade=True)

def get_activity_id_for_bank_activity_id(bank_activity_id):
    """
    根据银行活动ID查询活动ID
    :param bank_activity_id:
    :return:
    """
    activity_detail = mysql_execute('select * from tbl_trade_activity where activity_id=%s', params=(bank_activity_id),trade=True)
    return activity_detail


def delete_blacklist():
    """
    删除黑名单中的数据
    :return:
    """

    mysql_execute('delete from tbl_trade_black_list',trade=True)

def delete_image():
    """
    删除图片
    :return:
    """

    mysql_execute('delete from tbl_trade_image',trade=True)
    redis_execute(trade=True).delete('netCar:IMAGE_CACHE_KEY')

def delete_activity_display():
    """
    删除活动展示管理数据
    :param activity_display_id:
    :return:
    """
    mysql_execute('TRUNCATE `netCar`.`tbl_trade_activity_display_manage`',trade=True)
    redis_execute().delete('netCar:ACTIVITY_DISPLAY_MANAGE_KEY:')


def fix_random_activity_use_num(activity_id,type,number):
    """
    修改随机立减活动使用数量
    :param activity_id:
    :return:
    """
    if type == 'cycle':
        redis_execute(trade=True).set(name='netCar:ACTIVITY:ACTIVITY_ID_CYCLE_{0}'.format(activity_id),value=number)
    else:
        redis_execute(trade=True).set(name='netCar:ACTIVITY:ACTIVITY_ID_{0}'.format(activity_id),value=number)

