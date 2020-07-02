# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi
from ApiManager.pf_netcar_api.base_api import BaseApi


class QueryLoginCustomerCanUseCouponApi(LoginBaseApi):
    """
    已登录用户是否可使用优惠券接口
    """
    url = '/netCar/page/activity/queryLoginCustomerCanUseCoupon'


class QueryCanUseCouponApi(BaseApi):
    """
    未登录用户是否可使用优惠券接口
    """
    url = '/netCar/page/query/queryCanUseCoupon'

