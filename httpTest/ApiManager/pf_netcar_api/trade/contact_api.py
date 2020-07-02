# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi
from ApiManager.pf_netcar_api.base_api import BaseApi

class AddContactApi(LoginBaseApi):
    """
    添加常用联系人
    """
    url =  '/netCar/page/contact/addContact'

    def build_custom_param(self,data):
        return {'data': {'mobile': data['mobile'],'name':data['name']},'signStr': 'string'}

class AddContactApiNoLogin(BaseApi):
    """
    测试未登录添加常用联系人
    """
    url = '/netCar/page/contact/addContact'

    def build_custom_param(self, data):
        return {'data': {'mobile': data['mobile'],'name':data['name']},"signStr": "string"}

class GetAddcontactApiNoLogin(BaseApi):
    """测试未登录查询常用联系人"""
    url = '/netCar/page/contact/getCustomerContactInfo'

    def build_custom_param(self, params):
        return {'pageNum': params['pageNum'], 'pageSize': params['pageSize']}

class GetAddcontactApi(LoginBaseApi):
    """测试登录查询常用联系人"""
    url = '/netCar/page/contact/getCustomerContactInfo'

    def build_custom_param(self,params):
        return {'pageNum': params['pageNum'],'pageSize': params['pageSize']}

class EditAddcontactApi(LoginBaseApi):
    """测试修改联系人"""
    url = '/netCar/page/contact/editContactInfo'

    def build_custom_param(self, data):
        return {'data': {'contactId': data['contactId'],'mobile': data['mobile'],'name': data['name']},'signStr': 'string'}














