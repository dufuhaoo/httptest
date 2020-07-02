# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class QueryOrderApi(SheetLoginBaseApi):
    """
    订单查询接口
    """
    url = '/netCarAdminAuth/orders/getOrder'

    def build_custom_param(self, data):
        return {'orderStatus': data['orderStatus'], # 订单状态
                'orderCreateBegTime': data['orderCreateBegTime'], # 订单创建开始时间
                'orderCreateEndTime': data['orderCreateEndTime'], # 订单创建结束时间
                'tripStartBegTime': data['tripStartBegTime'], # 行程开始时间
                'tripStartEndTime': data['tripStartEndTime'], # 行程结束时间
                'mobile': data['mobile'], # 手机号
                'id': data['id'], # 订单号
                'orderType': data['orderType'] # 订单类型
                }#


class QueryOrderDetailApi(SheetLoginBaseApi):
    """
    查询订单详情接口
    """
    url = '/netCarAdminAuth/orders/getOrderDetail'

    def build_custom_param(self, params):
        return {'orderId':params['orderId']}


class ExportOrderListApi(SheetLoginBaseApi):
    """
    导出订单接口
    """
    url = '/netCarAdminAuth/orders/exportOrderList'

    def build_custom_param(self, data):
        return {'orderStatus': data['orderStatus'], # 订单状态
                'orderCreateBegTime': data['orderCreateBegTime'], # 订单创建开始时间
                'orderCreateEndTime': data['orderCreateEndTime'], # 订单创建结束时间
                'tripStartBegTime': data['tripStartBegTime'], # 行程开始时间
                'tripStartEndTime': data['tripStartEndTime'], # 行程结束时间
                'mobile': data['mobile'], # 手机号
                'id': data['id'], # 订单号
                'orderType': data['orderType'] # 订单类型
                }#