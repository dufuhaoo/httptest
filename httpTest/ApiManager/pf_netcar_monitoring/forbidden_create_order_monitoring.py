# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.login_api import TradeLoginApi
from ApiManager.pf_netcar_monitoring.base_pf_netcar import create_order,create_transfer_drop_off_order,create_transfer_pick_up_order
from ApiManager.pf_netcar_api.sheet.update_config_api import UpdateConfigApi
from ApiManager.utils import hooks
from ApiManager.utils.redis_helper import FORBIDDEN_CREATE_ORDER_MONITORING_KEY
import datetime,time



class ForbiddenCreateOrder(BaseMonitoring):
    """
    禁止下单监控
    """


    def forbidden_create_order_for_card_type_10(self):
        """
        测试绑卡类型为10时无法下单
        :return:
        """
        login_result = TradeLoginApi().login(user_type=10)
        create_order_result = create_order(user_mobile=login_result['mobile'],user_type=10,random_channel=True,open_sign_force=True)
        assert create_order_result['order_id'] == None
        assert create_order_result['resp_code'] == 901
        assert create_order_result['message'] == 'customer_do_not_have_default_card'

    def forbidden_create_order_for_card_type_20(self):
        """
        测试绑卡类型为20时无法下单
        :return:
        """
        login_result = TradeLoginApi().login(user_type=20)
        create_order_result = create_order(user_mobile=login_result['mobile'],user_type=20,random_channel=True,open_sign_force=True)
        assert create_order_result['order_id'] == None
        assert create_order_result['resp_code'] == 901
        assert create_order_result['message'] == 'customer_do_not_have_default_card'

    def forbidden_create_order_for_card_type_30(self):
        """
        测试绑卡类型为30时无法下单
        :return:
        """
        login_result = TradeLoginApi().login(user_type=30)
        create_order_result = create_order(user_mobile=login_result['mobile'],user_type=30,random_channel=True,open_sign_force=True)
        assert create_order_result['order_id'] == None
        assert create_order_result['resp_code'] == 901
        assert create_order_result['message'] == 'customer_do_not_have_default_card'

    def forbidden_create_order_for_not_open_sign_force(self):
        """
        测试未开通强制付款无法下单
        :return:
        """
        login_result = TradeLoginApi().login(open_sign_force=False)
        create_order_result = create_order(user_mobile=login_result['mobile'],random_channel=True,open_sign_force=False)
        assert create_order_result['order_id'] == None
        assert create_order_result['resp_code'] == 902
        assert create_order_result['message'] == 'customer_do_not_sign_force_payment'

    def forbidden_create_order_for_open_switch(self):
        """
        测试开启禁止下单按钮后无法下单
        :return:
        """
        config_detail = hooks.get_sheet_config_settings_detail(config_name='禁止下单开关')
        # 开启禁止下单开关
        update_settings_api = UpdateConfigApi()
        update_settings_api.post({'id':config_detail['id'],'configSetting':0})
        assert update_settings_api.get_status_code() == 200
        assert update_settings_api.get_resp_code() == 0
        time.sleep(3)

        # 验证实时单无法下单
        login_result = TradeLoginApi().login(open_sign_force=True)
        create_order_result = create_order(user_mobile=login_result['mobile'],random_channel=True,open_sign_force=False)
        assert create_order_result['order_id'] == None
        assert create_order_result['resp_code'] == 611
        assert create_order_result['message'] == 'limit_create_order'

        # 验证接机订单无法下单
        now_time = datetime.datetime.now()
        flight_date = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d")
        create_transfer_pick_up_order_result = create_transfer_pick_up_order(channel_name='cc',flight_date=flight_date,passenger_mobile='13501077762',passenger_name='张三')
        assert create_transfer_pick_up_order_result['order_id'] == None
        assert create_transfer_pick_up_order_result['resp_code'] == 611
        assert create_transfer_pick_up_order_result['message'] == 'limit_create_order'

        # 验证接机订单无法下单
        booking_date = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d 20:00:00")
        create_transfer_pick_up_order_result = create_transfer_drop_off_order(channel_name='cc', booking_date=booking_date,passenger_mobile='13501077762',passenger_name='张三')
        assert create_transfer_pick_up_order_result['order_id'] == None
        assert create_transfer_pick_up_order_result['resp_code'] == 611
        assert create_transfer_pick_up_order_result['message'] == 'limit_create_order'

    def tearDown(self):
        config_detail = hooks.get_sheet_config_settings_detail(config_name='禁止下单开关')
        # 关闭禁止下单开关
        update_settings_api = UpdateConfigApi()
        update_settings_api.post({'id':config_detail['id'],'configSetting':1})
        assert update_settings_api.get_status_code() == 200
        assert update_settings_api.get_resp_code() == 0


if __name__ == '__main__':
    monitoring = ForbiddenCreateOrder()
    monitoring.run_method(monitoring_name='禁止下单场景监控',monitoring_class=monitoring,redis_key=FORBIDDEN_CREATE_ORDER_MONITORING_KEY)
    # monitoring.forbidden_create_order_for_open_switch()
    # monitoring.tearDown()




