# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class QueryUserInfoApi(SheetLoginBaseApi):
    """
    用户信息查询
    """
    url = '/netCarAdminAuth/customers/getUser'

    def build_custom_param(self, data):
        return {'userId':data['userId'],'mobile':data['mobile']}
