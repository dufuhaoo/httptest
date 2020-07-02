# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.base_api import BaseApi


class FlightInfoApi(BaseApi):
    """
    查询航班信息接口
    """
    url = '/netCar/page/query/flightInfo'

    def build_custom_param(self, data):
        return {'departDate': data['departDate'], 'arriveAirportCode': data['arriveAirportCode'], 'departAirportCode': data['departAirportCode'],
                'flightNo': data['flightNo']}