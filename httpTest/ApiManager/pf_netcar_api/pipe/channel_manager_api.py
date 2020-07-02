# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import PipeLoginBaseApi


class ChannelManagerApi(PipeLoginBaseApi):
    """
    渠道管理接口
    """
    url = '/auth/channel/isOpenSwitch'

    def build_custom_param(self, data):
        return {'id':data['id'],'isOpen':data['isOpen'],'channelType':data['channelType']}
