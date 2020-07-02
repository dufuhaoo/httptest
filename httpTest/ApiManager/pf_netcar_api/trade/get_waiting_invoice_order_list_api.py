# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class GetWaitingInvoiceListApi(LoginBaseApi):
    """
    查询可开具发票行程列表
    """
    url = '/netCar/page/invoice/getWaitingInvoiceOrderList'

    def build_custom_param(self, params):
        return {'pageNum': 1,'pageSize':10,'channelId':params['channelId']}

