# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class CreateOrderApi(LoginBaseApi):
    """
    实时约车下单接口
    """
    url = '/netCar/page/order/createOrder'

    def build_custom_param(self, data):
        return {
            "data": {
                "startPoint": data['startPoint'],
                "endPoint": data['endPoint'],
                "fromLng": data['fromLng'],
                "fromLat": data['fromLat'],
                "toLng": data['toLng'],
                "toLat": data['toLat'],
                "cityCode": data['cityCode'],
                "cityName": data['cityName'],
                "vehicleDTOList": data['vehicleDTOList'],
                "passengerMobile": self.mobile,
                "passengerName": "本人"
            },
            "signStr": "signStr"
        }



class CreateTransferOrderApi(LoginBaseApi):
    """
    接送机下单接口
    """
    url = '/netCar/page/transfer/createOrder'

    def build_custom_param(self, data):
        return {
            "data": {
                "arrCode": data['arrCode'],
                "brand": data['brand'],
                "cityCode": data['cityCode'],
                "cityName": data['cityName'],
                "couponId": data['couponId'],
                "depCode": data['depCode'],
                "departureTime": data['departureTime'],
                "endName": data['endName'],
                "estimatedAmount": data['estimatedAmount'],
                "flightDelayTime": data['flightDelayTime'],
                "flightTime": data["flightTime"],
                "flt":data['flt'],
                "fromLat":data['fromLat'],
                "fromLng":data['fromLng'],
                "groupName":data['groupName'],
                "orderType":data['orderType'],
                "passenger":{
                    "mobile":data['passenger']['mobile'],
                    "name":data['passenger']['name']
                },
                "priceToken":data['priceToken'],
                "startName":data['startName'],
                "toLat":data['toLat'],
                "toLng":data['toLng'],
                "type":data['type']
            },
            "signStr": "signStr"
        }