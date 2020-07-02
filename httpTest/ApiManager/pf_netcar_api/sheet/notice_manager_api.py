# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class AddNoticeApi(SheetLoginBaseApi):
    """
    添加通知接口
    """
    url = '/netCarAdminAuth/noticeController/addNotice'

    def build_custom_param(self, data):
        return {"startTime":data['startTime'],"endTime":data['endTime'],"content":data['content'],"state":data['state'],'url':data['url'],'jumpType':data['jumpType']}


class GetNoticeApi(SheetLoginBaseApi):
    """
    获取通知列表
    """
    url = '/netCarAdminAuth/noticeController/getNotice'

    def build_custom_param(self, data):
        """
        state 状态 1为开启，0为关闭
        :param data:
        :return:
        """
        return {'pageNum': 1,'state': data['state']}


class EditNoticeApi(SheetLoginBaseApi):
    """
    修改通知
    """
    url = '/netCarAdminAuth/noticeController/editNotice'

    def build_custom_param(self, data):
        return {"id":data['id'],"state":data['state'],"content":data['content']}



class DeleteNoticeApi(SheetLoginBaseApi):
    """
    删除通知
    """
    url = '/netCarAdminAuth/noticeController/delNotice'

    def build_custom_param(self, data):
        return {"id":data['id'],"state":data['state']}
