# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class QueryRefundApi(SheetLoginBaseApi):
    """
    退款明细查询接口
    """
    url = '/netCarAdminAuth/pay/geRefund'

    def build_custom_param(self, data):
        return {'refundBeginTime': data['refundBeginTime'], # 开始时间
                'refundEndTime': data['refundEndTime'], # 结束时间
                'userId': data['userId'], # 用户ID
                'orderId': data['orderId'], # 订单号
                'refundReqNo': data['refundReqNo'], # 退款单号
                }