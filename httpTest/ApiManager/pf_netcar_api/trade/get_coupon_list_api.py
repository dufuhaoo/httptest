# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import LoginBaseApi


class GetCouponListApi(LoginBaseApi):
    """
    获取用户优惠券列表
    """
    url = '/netCar/page/coupon/getCouponsList'

    def build_custom_param(self, params):
        return {"couponStatus": params['couponStatus'], 'pageNum': 1, 'pageSize': 10,'orderFlag':params['orderFlag']}
