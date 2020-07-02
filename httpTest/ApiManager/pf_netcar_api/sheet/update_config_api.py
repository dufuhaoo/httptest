# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class UpdateConfigApi(SheetLoginBaseApi):
    """
    基础配置管理接口
    """
    url = '/netCarAdminAuth/config/updateConfig'

    def build_custom_param(self, data):
        return {'id':data['id'],'configSetting':data['configSetting']}
