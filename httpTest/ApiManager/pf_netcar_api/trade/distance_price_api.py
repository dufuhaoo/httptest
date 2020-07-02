# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.base_api import BaseApi


class DistancePriceApi(BaseApi):
    """
    实时约车查询行程预估价格
    """
    url = '/netCar/page/query/distancePrice'

    def build_custom_param(self, data):
        return {'cityCode': data['cityCode'], 'fromLat': data['fromLat'], 'fromLng': data['fromLng'],
                'orderType': data['orderType'], 'toLat': data['toLat'], 'toLng': data['toLng'],
                'cityName': data['cityName'],'startAddr':data['startAddr'],'endAddr':data['endAddr']}


class TransferDistancePriceApi(BaseApi):
    """
    接送机查询行程预估价格
    """
    url = '/netCar/page/query/distancePrice'

    def build_custom_param(self, data):
        return data
