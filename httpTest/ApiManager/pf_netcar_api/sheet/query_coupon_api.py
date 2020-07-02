# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class QueryCouponApi(SheetLoginBaseApi):
    """
    用户优惠券查询
    """
    url = '/netCarAdminAuth/coupons/getCoupon'

    def build_custom_param(self, data):
        return {'couponStatus': data['couponStatus'], 'mobile': data['mobile'], 'userId': data['userId'],
                'orderId': data['orderId'], 'begTime': None, 'endTime': None}
