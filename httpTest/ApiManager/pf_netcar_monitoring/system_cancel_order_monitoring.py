# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.login_api import TradeLoginApi
from ApiManager.pf_netcar_monitoring.base_pf_netcar import create_order
from ApiManager.pf_netcar_api.trade.get_un_done_order_api import GetUnDoneOrderApi
from ApiManager.pf_netcar_api.trade.get_order_list_api import GetOrderListApi
from ApiManager.pf_netcar_api.trade.get_order_detail_info_api import GetOrderDetailInfoApi
from ApiManager.pf_netcar_api.trade.get_order_status_real_time_data_api import GetOrderStatusRealTimeDataApi
from ApiManager.utils.redis_helper import SYSTEM_CANCEL_ORDER_MONITORING_KEY
import time



class SystemCancelOrderMonitoring(BaseMonitoring):
    """
    订单无司机接单超时取消监控

    1114版本后需补充：
    1、曹操、首汽同时下单超时取消
    2、曹操、阳光同时下单超时取消
    3、曹操、神州同时下单超时取消
    4、首汽、阳光同时下单超时取消
    5、首汽、神州同时下单超时取消
    6、阳光、神州同时下单超时取消
    7、曹操、首汽、阳光同时下单超时取消
    8、曹操、首汽、神州同时下单超时取消
    9、曹操、阳光、神州同时下单超时取消
    10、首汽、阳光、神州同时下单超时取消
    11、曹操、阳光、神州、首汽同时下单超时取消

    12、并发执行该测试案例，用时巨长
    """

    # def system_cancel_order_yg(self):
    #     """
    #     测试阳光实时单无司机接单自动取消
    #     :return:
    #     """
    #     # 实时单下单
    #     login_result = TradeLoginApi().login()
    #     create_order_result = create_order(user_mobile=login_result['mobile'],channel_name='yg')
    #     assert create_order_result['resp_code'] == 0
    #     assert create_order_result['message'] == 'OK'
    #     order_id = create_order_result['order_id']
    #     # 查询未完成订单列表
    #     get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
    #     get_un_done_order_api.get()
    #     assert get_un_done_order_api.get_resp_code() == 0
    #     assert get_un_done_order_api.get_resp_message() == 'OK'
    #     assert get_un_done_order_api.get_resp_data()['orderId'] == order_id
    #     # 查询我的行程列表
    #     get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
    #     get_order_list_api.get()
    #     assert get_order_list_api.get_resp_code() == 0
    #     assert get_order_list_api.get_resp_message() == 'OK'
    #     order_list_data = get_order_list_api.get_resp_data()
    #     assert order_list_data['total'] == 1
    #     order_list = order_list_data['list']
    #     assert len(order_list) == 1
    #     assert order_list[0]['id'] == order_id
    #     assert order_list[0]['channelId'] == 5
    #     assert order_list[0]['orderType'] == 1
    #     assert order_list[0]['channelName'] == '阳光出行'
    #     assert order_list[0]['startPoint'] == '公益西桥'
    #     assert order_list[0]['endPoint'] == '天通苑'
    #     assert order_list[0]['orderStatus'] == 1
    #     assert order_list[0]['payState'] == None
    #     assert order_list[0]['payPrice'] == 0
    #     assert time.strftime('%Y-%m-%d') in order_list[0]['createTime']
    #     # 查询行程详情
    #     get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
    #     get_order_detail_info_api.get({'orderId': order_id})
    #     assert get_order_detail_info_api.get_resp_code() == 0
    #     assert get_order_detail_info_api.get_resp_message() == 'OK'
    #     order_detail_data = get_order_detail_info_api.get_resp_data()
    #     assert order_detail_data['orderState'] == 1
    #     assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
    #     assert order_detail_data['channelName'] == '阳光出行'
    #     assert order_detail_data['payPrice'] == 0
    #     assert order_detail_data['actualPayPrice'] == 0
    #     assert order_detail_data['discountPrice'] == 0
    #     assert order_detail_data['refundPrice'] == 0
    #     assert order_detail_data['orignDiscountPrice'] == 0
    #     assert order_detail_data['driveMileage'] == None
    #     assert order_detail_data['driveTime'] == None
    #     assert order_detail_data['feeInfo'] == None
    #     address_info = order_detail_data['addressInfo']
    #     assert address_info['startAddName'] == '公益西桥'
    #     assert address_info['endAddName'] == '天通苑'
    #     assert address_info['startLng'] == '116.369840'
    #     assert address_info['startLat'] == '39.831240'
    #     assert address_info['endLng'] == '116.419670'
    #     assert address_info['endLat'] == '40.063590'
    #     # 查询订单实时状态
    #     count = 1
    #     max_count = 60
    #     while count < max_count:
    #         get_order_status_real_time_data_api = GetOrderStatusRealTimeDataApi(mobile=login_result['mobile'])
    #         get_order_status_real_time_data_api.get({'orderId':order_id})
    #         assert get_order_status_real_time_data_api.get_resp_code() == 0
    #         assert get_order_status_real_time_data_api.get_resp_message() == 'OK'
    #         order_status_real_time_data = get_order_status_real_time_data_api.get_resp_data()
    #         if order_status_real_time_data['orderState'] == 1:
    #             assert order_status_real_time_data['orderId'] == order_id
    #             assert order_status_real_time_data['tradeOrderFlag'] == False
    #             assert order_status_real_time_data['channelName'] == '阳光出行'
    #             assert order_status_real_time_data['carTypeName'] == None
    #             assert order_status_real_time_data['payPrice'] == 0
    #             assert order_status_real_time_data['actualPayPrice'] == 0
    #             assert order_status_real_time_data['discountPrice'] == 0
    #             assert order_status_real_time_data['orignDiscountPrice'] == 0
    #             assert order_status_real_time_data['driveMileage'] == None
    #             assert order_status_real_time_data['driveTime'] == None
    #             assert order_status_real_time_data['feeInfo'] == None
    #             assert order_status_real_time_data['driverInfo'] == None
    #             address_info = order_status_real_time_data['addressInfo']
    #             assert address_info['startAddName'] == '公益西桥'
    #             assert address_info['endAddName'] == '天通苑'
    #             assert address_info['startLng'] == '116.369840'
    #             assert address_info['startLat'] == '39.831240'
    #             assert address_info['endLng'] == '116.419670'
    #             assert address_info['endLat'] == '40.063590'
    #             time.sleep(10)
    #             count += 1
    #         else:
    #             assert order_status_real_time_data['orderId'] == order_id
    #             assert order_status_real_time_data['tradeOrderFlag'] == False
    #             assert int(time.time()) * 1000 - int(order_status_real_time_data['orderCreateTime']) < 600000
    #             assert order_status_real_time_data['channelName'] == '阳光出行'
    #             assert order_status_real_time_data['carTypeName'] == None
    #             assert order_status_real_time_data['payPrice'] == 0
    #             assert order_status_real_time_data['actualPayPrice'] == 0
    #             assert order_status_real_time_data['discountPrice'] == 0
    #             assert order_status_real_time_data['orignDiscountPrice'] == 0
    #             assert order_status_real_time_data['driveMileage'] == None
    #             assert order_status_real_time_data['driveTime'] == None
    #             assert order_status_real_time_data['feeInfo'] == None
    #             assert order_status_real_time_data['driverInfo'] == None
    #             assert order_status_real_time_data['orderState'] == 10
    #             address_info = order_status_real_time_data['addressInfo']
    #             assert address_info['startAddName'] == '公益西桥'
    #             assert address_info['endAddName'] == '天通苑'
    #             assert address_info['startLng'] == '116.369840'
    #             assert address_info['startLat'] == '39.831240'
    #             assert address_info['endLng'] == '116.419670'
    #             assert address_info['endLat'] == '40.063590'
    #             break
    #     assert count < max_count
    #     # 查询未完成订单列表
    #     get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
    #     get_un_done_order_api.get()
    #     assert get_un_done_order_api.get_resp_code() == 0
    #     assert get_un_done_order_api.get_resp_message() == 'OK'
    #     assert get_un_done_order_api.get_resp_data() == None
    #     # 查询我的行程列表
    #     get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
    #     get_order_list_api.get()
    #     assert get_order_list_api.get_resp_code() == 0
    #     assert get_order_list_api.get_resp_message() == 'OK'
    #     order_list_data = get_order_list_api.get_resp_data()
    #     assert order_list_data['total'] == 1
    #     order_list = order_list_data['list']
    #     assert len(order_list) == 1
    #     assert order_list[0]['id'] == order_id
    #     assert order_list[0]['channelId'] == 5
    #     assert order_list[0]['orderType'] == 1
    #     assert order_list[0]['channelName'] == '阳光出行'
    #     assert order_list[0]['startPoint'] == '公益西桥'
    #     assert order_list[0]['endPoint'] == '天通苑'
    #     assert order_list[0]['orderStatus'] == 10
    #     assert order_list[0]['payState'] == None
    #     assert order_list[0]['payPrice'] == 0
    #     assert time.strftime('%Y-%m-%d') in order_list[0]['createTime']
    #     # 查询行程详情
    #     get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
    #     get_order_detail_info_api.get({'orderId': order_id})
    #     assert get_order_detail_info_api.get_resp_code() == 0
    #     assert get_order_detail_info_api.get_resp_message() == 'OK'
    #     order_detail_data = get_order_detail_info_api.get_resp_data()
    #     assert order_detail_data['orderState'] == 10
    #     assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
    #     assert order_detail_data['channelName'] == '阳光出行'
    #     assert order_detail_data['payPrice'] == 0
    #     assert order_detail_data['actualPayPrice'] == 0
    #     assert order_detail_data['discountPrice'] == 0
    #     assert order_detail_data['refundPrice'] == 0
    #     assert order_detail_data['orignDiscountPrice'] == 0
    #     assert order_detail_data['driveMileage'] == None
    #     assert order_detail_data['driveTime'] == None
    #     assert order_detail_data['feeInfo'] == None
    #     address_info = order_detail_data['addressInfo']
    #     assert address_info['startAddName'] == '公益西桥'
    #     assert address_info['endAddName'] == '天通苑'
    #     assert address_info['startLng'] == '116.369840'
    #     assert address_info['startLat'] == '39.831240'
    #     assert address_info['endLng'] == '116.419670'
    #     assert address_info['endLat'] == '40.063590'

    def system_cancel_order_cc(self):
        """
        测试曹操实时单无司机接单自动取消
        :return:
        """
        # 实时单下单
        login_result = TradeLoginApi().login()
        create_order_result = create_order(user_mobile=login_result['mobile'],channel_name='cc')
        assert create_order_result['resp_code'] == 0
        assert create_order_result['message'] == 'OK'
        order_id = create_order_result['order_id']
        # 查询未完成订单列表
        get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
        get_un_done_order_api.get()
        assert get_un_done_order_api.get_resp_code() == 0
        assert get_un_done_order_api.get_resp_message() == 'OK'
        assert get_un_done_order_api.get_resp_data()['orderId'] == order_id
        # 查询我的行程列表
        get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
        get_order_list_api.get()
        assert get_order_list_api.get_resp_code() == 0
        assert get_order_list_api.get_resp_message() == 'OK'
        order_list_data = get_order_list_api.get_resp_data()
        assert order_list_data['total'] == 1
        order_list = order_list_data['list']
        assert len(order_list) == 1
        assert order_list[0]['id'] == order_id
        assert order_list[0]['channelId'] == 1
        assert order_list[0]['orderType'] == 1
        assert order_list[0]['channelName'] == '曹操'
        assert order_list[0]['startPoint'] == '公益西桥'
        assert order_list[0]['endPoint'] == '天通苑'
        assert order_list[0]['orderStatus'] == 1
        assert order_list[0]['payState'] == None
        assert order_list[0]['payPrice'] == 0
        assert time.strftime('%Y-%m-%d %H') in order_list[0]['createTime']
        # 查询行程详情
        get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
        get_order_detail_info_api.get({'orderId': order_id})
        assert get_order_detail_info_api.get_resp_code() == 0
        assert get_order_detail_info_api.get_resp_message() == 'OK'
        order_detail_data = get_order_detail_info_api.get_resp_data()
        assert order_detail_data['orderState'] == 1
        assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
        assert order_detail_data['channelName'] == '曹操'
        assert order_detail_data['payPrice'] == 0
        assert order_detail_data['actualPayPrice'] == 0
        assert order_detail_data['discountPrice'] == 0
        assert order_detail_data['refundPrice'] == 0
        assert order_detail_data['orignDiscountPrice'] == 0
        assert order_detail_data['driveMileage'] == None
        assert order_detail_data['driveTime'] == None
        assert order_detail_data['feeInfo'] == None
        address_info = order_detail_data['addressInfo']
        assert address_info['startAddName'] == '公益西桥'
        assert address_info['endAddName'] == '天通苑'
        assert address_info['startLng'] == '116.369840'
        assert address_info['startLat'] == '39.831240'
        assert address_info['endLng'] == '116.419670'
        assert address_info['endLat'] == '40.063590'
        # 查询订单实时状态
        count = 1
        max_count = 60
        while count < max_count:
            get_order_status_real_time_data_api = GetOrderStatusRealTimeDataApi(mobile=login_result['mobile'])
            get_order_status_real_time_data_api.get({'orderId':order_id})
            assert get_order_status_real_time_data_api.get_resp_code() == 0
            assert get_order_status_real_time_data_api.get_resp_message() == 'OK'
            order_status_real_time_data = get_order_status_real_time_data_api.get_resp_data()
            if order_status_real_time_data['orderState'] == 1:
                assert order_status_real_time_data['orderId'] == order_id
                assert order_status_real_time_data['tradeOrderFlag'] == False
                assert order_status_real_time_data['channelName'] == '曹操'
                assert order_status_real_time_data['carTypeName'] == None
                assert order_status_real_time_data['payPrice'] == 0
                assert order_status_real_time_data['actualPayPrice'] == 0
                assert order_status_real_time_data['discountPrice'] == 0
                assert order_status_real_time_data['orignDiscountPrice'] == 0
                assert order_status_real_time_data['driveMileage'] == None
                assert order_status_real_time_data['driveTime'] == None
                assert order_status_real_time_data['feeInfo'] == None
                assert order_status_real_time_data['driverInfo'] == None
                address_info = order_status_real_time_data['addressInfo']
                assert address_info['startAddName'] == '公益西桥'
                assert address_info['endAddName'] == '天通苑'
                assert address_info['startLng'] == '116.369840'
                assert address_info['startLat'] == '39.831240'
                assert address_info['endLng'] == '116.419670'
                assert address_info['endLat'] == '40.063590'
                time.sleep(10)
                count += 1
            else:
                assert order_status_real_time_data['orderId'] == order_id
                assert order_status_real_time_data['tradeOrderFlag'] == False
                assert int(time.time()) * 1000 - int(order_status_real_time_data['orderCreateTime']) < 600000
                assert order_status_real_time_data['channelName'] == '曹操'
                assert order_status_real_time_data['carTypeName'] == None
                assert order_status_real_time_data['payPrice'] == 0
                assert order_status_real_time_data['actualPayPrice'] == 0
                assert order_status_real_time_data['discountPrice'] == 0
                assert order_status_real_time_data['orignDiscountPrice'] == 0
                assert order_status_real_time_data['driveMileage'] == None
                assert order_status_real_time_data['driveTime'] == None
                assert order_status_real_time_data['feeInfo'] == None
                assert order_status_real_time_data['driverInfo'] == None
                assert order_status_real_time_data['orderState'] == 10
                address_info = order_status_real_time_data['addressInfo']
                assert address_info['startAddName'] == '公益西桥'
                assert address_info['endAddName'] == '天通苑'
                assert address_info['startLng'] == '116.369840'
                assert address_info['startLat'] == '39.831240'
                assert address_info['endLng'] == '116.419670'
                assert address_info['endLat'] == '40.063590'
                break
        assert count < max_count
        # 查询未完成订单列表
        get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
        get_un_done_order_api.get()
        assert get_un_done_order_api.get_resp_code() == 0
        assert get_un_done_order_api.get_resp_message() == 'OK'
        assert get_un_done_order_api.get_resp_data() == None
        # 查询我的行程列表
        get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
        get_order_list_api.get()
        assert get_order_list_api.get_resp_code() == 0
        assert get_order_list_api.get_resp_message() == 'OK'
        order_list_data = get_order_list_api.get_resp_data()
        assert order_list_data['total'] == 1
        order_list = order_list_data['list']
        assert len(order_list) == 1
        assert order_list[0]['id'] == order_id
        assert order_list[0]['channelId'] == 1
        assert order_list[0]['orderType'] == 1
        assert order_list[0]['channelName'] == '曹操'
        assert order_list[0]['startPoint'] == '公益西桥'
        assert order_list[0]['endPoint'] == '天通苑'
        assert order_list[0]['orderStatus'] == 10
        assert order_list[0]['payState'] == None
        assert order_list[0]['payPrice'] == 0
        assert time.strftime('%Y-%m-%d %H') in order_list[0]['createTime']
        # 查询行程详情
        get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
        get_order_detail_info_api.get({'orderId': order_id})
        assert get_order_detail_info_api.get_resp_code() == 0
        assert get_order_detail_info_api.get_resp_message() == 'OK'
        order_detail_data = get_order_detail_info_api.get_resp_data()
        assert order_detail_data['orderState'] == 10
        assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
        assert order_detail_data['channelName'] == '曹操'
        assert order_detail_data['payPrice'] == 0
        assert order_detail_data['actualPayPrice'] == 0
        assert order_detail_data['discountPrice'] == 0
        assert order_detail_data['refundPrice'] == 0
        assert order_detail_data['orignDiscountPrice'] == 0
        assert order_detail_data['driveMileage'] == None
        assert order_detail_data['driveTime'] == None
        assert order_detail_data['feeInfo'] == None
        address_info = order_detail_data['addressInfo']
        assert address_info['startAddName'] == '公益西桥'
        assert address_info['endAddName'] == '天通苑'
        assert address_info['startLng'] == '116.369840'
        assert address_info['startLat'] == '39.831240'
        assert address_info['endLng'] == '116.419670'
        assert address_info['endLat'] == '40.063590'

    def system_cancel_order_sq(self):
        """
        测试首汽实时单无司机接单自动取消
        :return:
        """
        # 实时单下单
        login_result = TradeLoginApi().login()
        create_order_result = create_order(user_mobile=login_result['mobile'],channel_name='sq')
        assert create_order_result['resp_code'] == 0
        assert create_order_result['message'] == 'OK'
        order_id = create_order_result['order_id']
        # 查询未完成订单列表
        get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
        get_un_done_order_api.get()
        assert get_un_done_order_api.get_resp_code() == 0
        assert get_un_done_order_api.get_resp_message() == 'OK'
        assert get_un_done_order_api.get_resp_data()['orderId'] == order_id
        # 查询我的行程列表
        get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
        get_order_list_api.get()
        assert get_order_list_api.get_resp_code() == 0
        assert get_order_list_api.get_resp_message() == 'OK'
        order_list_data = get_order_list_api.get_resp_data()
        assert order_list_data['total'] == 1
        order_list = order_list_data['list']
        assert len(order_list) == 1
        assert order_list[0]['id'] == order_id
        assert order_list[0]['channelId'] == 2
        assert order_list[0]['orderType'] == 1
        assert order_list[0]['channelName'] == '首汽约车'
        assert order_list[0]['startPoint'] == '公益西桥'
        assert order_list[0]['endPoint'] == '天通苑'
        assert order_list[0]['orderStatus'] == 1
        assert order_list[0]['payState'] == None
        assert order_list[0]['payPrice'] == 0
        assert time.strftime('%Y-%m-%d') in order_list[0]['createTime']
        # 查询行程详情
        get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
        get_order_detail_info_api.get({'orderId': order_id})
        assert get_order_detail_info_api.get_resp_code() == 0
        assert get_order_detail_info_api.get_resp_message() == 'OK'
        order_detail_data = get_order_detail_info_api.get_resp_data()
        assert order_detail_data['orderState'] == 1
        assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
        assert order_detail_data['channelName'] == '首汽约车'
        assert order_detail_data['payPrice'] == 0
        assert order_detail_data['actualPayPrice'] == 0
        assert order_detail_data['discountPrice'] == 0
        assert order_detail_data['refundPrice'] == 0
        assert order_detail_data['orignDiscountPrice'] == 0
        assert order_detail_data['driveMileage'] == None
        assert order_detail_data['driveTime'] == None
        assert order_detail_data['feeInfo'] == None
        address_info = order_detail_data['addressInfo']
        assert address_info['startAddName'] == '公益西桥'
        assert address_info['endAddName'] == '天通苑'
        assert address_info['startLng'] == '116.369840'
        assert address_info['startLat'] == '39.831240'
        assert address_info['endLng'] == '116.419670'
        assert address_info['endLat'] == '40.063590'
        # 查询订单实时状态
        count = 1
        max_count = 60
        while count < max_count:
            get_order_status_real_time_data_api = GetOrderStatusRealTimeDataApi(mobile=login_result['mobile'])
            get_order_status_real_time_data_api.get({'orderId':order_id})
            assert get_order_status_real_time_data_api.get_resp_code() == 0
            assert get_order_status_real_time_data_api.get_resp_message() == 'OK'
            order_status_real_time_data = get_order_status_real_time_data_api.get_resp_data()
            if order_status_real_time_data['orderState'] == 1:
                assert order_status_real_time_data['orderId'] == order_id
                assert order_status_real_time_data['tradeOrderFlag'] == False
                assert order_status_real_time_data['channelName'] == '首汽约车'
                assert order_status_real_time_data['carTypeName'] == None
                assert order_status_real_time_data['payPrice'] == 0
                assert order_status_real_time_data['actualPayPrice'] == 0
                assert order_status_real_time_data['discountPrice'] == 0
                assert order_status_real_time_data['orignDiscountPrice'] == 0
                assert order_status_real_time_data['driveMileage'] == None
                assert order_status_real_time_data['driveTime'] == None
                assert order_status_real_time_data['feeInfo'] == None
                assert order_status_real_time_data['driverInfo'] == None
                address_info = order_status_real_time_data['addressInfo']
                assert address_info['startAddName'] == '公益西桥'
                assert address_info['endAddName'] == '天通苑'
                assert address_info['startLng'] == '116.369840'
                assert address_info['startLat'] == '39.831240'
                assert address_info['endLng'] == '116.419670'
                assert address_info['endLat'] == '40.063590'
                time.sleep(10)
                count += 1
            else:
                assert order_status_real_time_data['orderId'] == order_id
                assert order_status_real_time_data['tradeOrderFlag'] == False
                assert int(time.time()) * 1000 - int(order_status_real_time_data['orderCreateTime']) < 600000
                assert order_status_real_time_data['channelName'] == '首汽约车'
                assert order_status_real_time_data['carTypeName'] == None
                assert order_status_real_time_data['payPrice'] == 0
                assert order_status_real_time_data['actualPayPrice'] == 0
                assert order_status_real_time_data['discountPrice'] == 0
                assert order_status_real_time_data['orignDiscountPrice'] == 0
                assert order_status_real_time_data['driveMileage'] == None
                assert order_status_real_time_data['driveTime'] == None
                assert order_status_real_time_data['feeInfo'] == None
                assert order_status_real_time_data['driverInfo'] == None
                assert order_status_real_time_data['orderState'] == 10
                address_info = order_status_real_time_data['addressInfo']
                assert address_info['startAddName'] == '公益西桥'
                assert address_info['endAddName'] == '天通苑'
                assert address_info['startLng'] == '116.369840'
                assert address_info['startLat'] == '39.831240'
                assert address_info['endLng'] == '116.419670'
                assert address_info['endLat'] == '40.063590'
                break
        assert count < max_count
        # 查询未完成订单列表
        get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
        get_un_done_order_api.get()
        assert get_un_done_order_api.get_resp_code() == 0
        assert get_un_done_order_api.get_resp_message() == 'OK'
        assert get_un_done_order_api.get_resp_data() == None
        # 查询我的行程列表
        get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
        get_order_list_api.get()
        assert get_order_list_api.get_resp_code() == 0
        assert get_order_list_api.get_resp_message() == 'OK'
        order_list_data = get_order_list_api.get_resp_data()
        assert order_list_data['total'] == 1
        order_list = order_list_data['list']
        assert len(order_list) == 1
        assert order_list[0]['id'] == order_id
        assert order_list[0]['channelId'] == 2
        assert order_list[0]['orderType'] == 1
        assert order_list[0]['channelName'] == '首汽约车'
        assert order_list[0]['startPoint'] == '公益西桥'
        assert order_list[0]['endPoint'] == '天通苑'
        assert order_list[0]['orderStatus'] == 10
        assert order_list[0]['payState'] == None
        assert order_list[0]['payPrice'] == 0
        assert time.strftime('%Y-%m-%d') in order_list[0]['createTime']
        # 查询行程详情
        get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
        get_order_detail_info_api.get({'orderId': order_id})
        assert get_order_detail_info_api.get_resp_code() == 0
        assert get_order_detail_info_api.get_resp_message() == 'OK'
        order_detail_data = get_order_detail_info_api.get_resp_data()
        assert order_detail_data['orderState'] == 10
        assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
        assert order_detail_data['channelName'] == '首汽约车'
        assert order_detail_data['payPrice'] == 0
        assert order_detail_data['actualPayPrice'] == 0
        assert order_detail_data['discountPrice'] == 0
        assert order_detail_data['refundPrice'] == 0
        assert order_detail_data['orignDiscountPrice'] == 0
        assert order_detail_data['driveMileage'] == None
        assert order_detail_data['driveTime'] == None
        assert order_detail_data['feeInfo'] == None
        address_info = order_detail_data['addressInfo']
        assert address_info['startAddName'] == '公益西桥'
        assert address_info['endAddName'] == '天通苑'
        assert address_info['startLng'] == '116.369840'
        assert address_info['startLat'] == '39.831240'
        assert address_info['endLng'] == '116.419670'
        assert address_info['endLat'] == '40.063590'

    def system_cancel_order_sz(self):
        """
        测试神州实时单无司机接单自动取消
        :return:
        """
        # 实时单下单
        login_result = TradeLoginApi().login()
        create_order_result = create_order(user_mobile=login_result['mobile'],channel_name='sz')
        assert create_order_result['resp_code'] == 0
        assert create_order_result['message'] == 'OK'
        order_id = create_order_result['order_id']
        # 查询未完成订单列表
        get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
        get_un_done_order_api.get()
        assert get_un_done_order_api.get_resp_code() == 0
        assert get_un_done_order_api.get_resp_message() == 'OK'
        assert get_un_done_order_api.get_resp_data()['orderId'] == order_id
        # 查询我的行程列表
        get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
        get_order_list_api.get()
        assert get_order_list_api.get_resp_code() == 0
        assert get_order_list_api.get_resp_message() == 'OK'
        order_list_data = get_order_list_api.get_resp_data()
        assert order_list_data['total'] == 1
        order_list = order_list_data['list']
        assert len(order_list) == 1
        assert order_list[0]['id'] == order_id
        assert order_list[0]['channelId'] == 4
        assert order_list[0]['orderType'] == 1
        assert order_list[0]['channelName'] == '神州'
        assert order_list[0]['startPoint'] == '公益西桥'
        assert order_list[0]['endPoint'] == '天通苑'
        assert order_list[0]['orderStatus'] == 1
        assert order_list[0]['payState'] == None
        assert order_list[0]['payPrice'] == 0
        assert time.strftime('%Y-%m-%d') in order_list[0]['createTime']
        # 查询行程详情
        get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
        get_order_detail_info_api.get({'orderId': order_id})
        assert get_order_detail_info_api.get_resp_code() == 0
        assert get_order_detail_info_api.get_resp_message() == 'OK'
        order_detail_data = get_order_detail_info_api.get_resp_data()
        assert order_detail_data['orderState'] == 1
        assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
        assert order_detail_data['channelName'] == '神州'
        assert order_detail_data['payPrice'] == 0
        assert order_detail_data['actualPayPrice'] == 0
        assert order_detail_data['discountPrice'] == 0
        assert order_detail_data['refundPrice'] == 0
        assert order_detail_data['orignDiscountPrice'] == 0
        assert order_detail_data['driveMileage'] == None
        assert order_detail_data['driveTime'] == None
        assert order_detail_data['feeInfo'] == None
        address_info = order_detail_data['addressInfo']
        assert address_info['startAddName'] == '公益西桥'
        assert address_info['endAddName'] == '天通苑'
        assert address_info['startLng'] == '116.369840'
        assert address_info['startLat'] == '39.831240'
        assert address_info['endLng'] == '116.419670'
        assert address_info['endLat'] == '40.063590'
        # 查询订单实时状态
        count = 1
        max_count = 60
        while count < max_count:
            get_order_status_real_time_data_api = GetOrderStatusRealTimeDataApi(mobile=login_result['mobile'])
            get_order_status_real_time_data_api.get({'orderId':order_id})
            assert get_order_status_real_time_data_api.get_resp_code() == 0
            assert get_order_status_real_time_data_api.get_resp_message() == 'OK'
            order_status_real_time_data = get_order_status_real_time_data_api.get_resp_data()
            if order_status_real_time_data['orderState'] == 1:
                assert order_status_real_time_data['orderId'] == order_id
                assert order_status_real_time_data['tradeOrderFlag'] == False
                assert order_status_real_time_data['channelName'] == '神州'
                assert order_status_real_time_data['carTypeName'] == None
                assert order_status_real_time_data['payPrice'] == 0
                assert order_status_real_time_data['actualPayPrice'] == 0
                assert order_status_real_time_data['discountPrice'] == 0
                assert order_status_real_time_data['orignDiscountPrice'] == 0
                assert order_status_real_time_data['driveMileage'] == None
                assert order_status_real_time_data['driveTime'] == None
                assert order_status_real_time_data['feeInfo'] == None
                assert order_status_real_time_data['driverInfo'] == None
                address_info = order_status_real_time_data['addressInfo']
                assert address_info['startAddName'] == '公益西桥'
                assert address_info['endAddName'] == '天通苑'
                assert address_info['startLng'] == '116.369840'
                assert address_info['startLat'] == '39.831240'
                assert address_info['endLng'] == '116.419670'
                assert address_info['endLat'] == '40.063590'
                time.sleep(10)
                count += 1
            else:
                assert order_status_real_time_data['orderId'] == order_id
                assert order_status_real_time_data['tradeOrderFlag'] == False
                assert int(time.time()) * 1000 - int(order_status_real_time_data['orderCreateTime']) < 600000
                assert order_status_real_time_data['channelName'] == '神州'
                assert order_status_real_time_data['carTypeName'] == None
                assert order_status_real_time_data['payPrice'] == 0
                assert order_status_real_time_data['actualPayPrice'] == 0
                assert order_status_real_time_data['discountPrice'] == 0
                assert order_status_real_time_data['orignDiscountPrice'] == 0
                assert order_status_real_time_data['driveMileage'] == None
                assert order_status_real_time_data['driveTime'] == None
                assert order_status_real_time_data['feeInfo'] == None
                assert order_status_real_time_data['driverInfo'] == None
                assert order_status_real_time_data['orderState'] == 10
                address_info = order_status_real_time_data['addressInfo']
                assert address_info['startAddName'] == '公益西桥'
                assert address_info['endAddName'] == '天通苑'
                assert address_info['startLng'] == '116.369840'
                assert address_info['startLat'] == '39.831240'
                assert address_info['endLng'] == '116.419670'
                assert address_info['endLat'] == '40.063590'
                break
        assert count < max_count
        # 查询未完成订单列表
        get_un_done_order_api = GetUnDoneOrderApi(mobile=login_result['mobile'])
        get_un_done_order_api.get()
        assert get_un_done_order_api.get_resp_code() == 0
        assert get_un_done_order_api.get_resp_message() == 'OK'
        assert get_un_done_order_api.get_resp_data() == None
        # 查询我的行程列表
        get_order_list_api = GetOrderListApi(mobile=login_result['mobile'])
        get_order_list_api.get()
        assert get_order_list_api.get_resp_code() == 0
        assert get_order_list_api.get_resp_message() == 'OK'
        order_list_data = get_order_list_api.get_resp_data()
        assert order_list_data['total'] == 1
        order_list = order_list_data['list']
        assert len(order_list) == 1
        assert order_list[0]['id'] == order_id
        assert order_list[0]['channelId'] == 4
        assert order_list[0]['orderType'] == 1
        assert order_list[0]['channelName'] == '神州'
        assert order_list[0]['startPoint'] == '公益西桥'
        assert order_list[0]['endPoint'] == '天通苑'
        assert order_list[0]['orderStatus'] == 10
        assert order_list[0]['payState'] == None
        assert order_list[0]['payPrice'] == 0
        assert time.strftime('%Y-%m-%d') in order_list[0]['createTime']
        # 查询行程详情
        get_order_detail_info_api = GetOrderDetailInfoApi(mobile=login_result['mobile'])
        get_order_detail_info_api.get({'orderId': order_id})
        assert get_order_detail_info_api.get_resp_code() == 0
        assert get_order_detail_info_api.get_resp_message() == 'OK'
        order_detail_data = get_order_detail_info_api.get_resp_data()
        assert order_detail_data['orderState'] == 10
        assert int(time.time()) * 1000 - int(order_detail_data['orderCreateTime']) < 600000
        assert order_detail_data['channelName'] == '神州'
        assert order_detail_data['payPrice'] == 0
        assert order_detail_data['actualPayPrice'] == 0
        assert order_detail_data['discountPrice'] == 0
        assert order_detail_data['refundPrice'] == 0
        assert order_detail_data['orignDiscountPrice'] == 0
        assert order_detail_data['driveMileage'] == None
        assert order_detail_data['driveTime'] == None
        assert order_detail_data['feeInfo'] == None
        address_info = order_detail_data['addressInfo']
        assert address_info['startAddName'] == '公益西桥'
        assert address_info['endAddName'] == '天通苑'
        assert address_info['startLng'] == '116.369840'
        assert address_info['startLat'] == '39.831240'
        assert address_info['endLng'] == '116.419670'
        assert address_info['endLat'] == '40.063590'


if __name__ == '__main__':
    monitoring = SystemCancelOrderMonitoring()
    monitoring.run_method(monitoring_class=monitoring,monitoring_name='实时单超时取消监控',redis_key=SYSTEM_CANCEL_ORDER_MONITORING_KEY)
    # monitoring.yangguang_system_cancel_order()
    # monitoring.tearDown()




