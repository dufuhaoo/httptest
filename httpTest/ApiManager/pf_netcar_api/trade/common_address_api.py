# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi
from ApiManager.pf_netcar_api.base_api import BaseApi

class AddCommonAdresstApi(LoginBaseApi):
    """
    添加常用地址
    """
    url =  '/netCar/page/address/addCustomerCommonAddress'
    def build_custom_param(self, data):
        return data

class DelCommonAdressApi(LoginBaseApi):
    """
    删除常用地址
    """
    url = '/netCar/page/address/deleteCustomerCommonAddress'

    def build_custom_param(self, data):
        return data

class EditCommonAddressApi(LoginBaseApi):
    """
    修改常用地址
    """
    url = '/netCar/page/address/editCommonAddress'

    def build_custom_param(self, data):
        return data
class GetCommonAdress(LoginBaseApi):
    """
    查询添加地址
    """
    url = '/netCar/page/address/getCustomerAddressData'

