# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.base_api import BaseApi


class QueryAirPortInfoApi(BaseApi):
    """
    查询航站楼接口
    """
    url = '/netCar/page/query/queryAirPortInfo'