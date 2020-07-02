# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi
import requests,json



class DownloadBlackListApi(SheetLoginBaseApi):
    """
    下载模板接口
    """
    url = '/netCarAdminAuth/blackList/downloadBlackListTemplate'

class ImportBlackListApi(SheetLoginBaseApi):
    """
    上传文件接口
    """
    url = '/netCarAdminAuth/blackList/importBlack'

    def request_api(self,file):
        cookie_value = self.get_cookie()
        s = requests.session()
        s.headers.setdefault('Cookie', cookie_value)
        response = s.post(url=self.api_url(),files=file)
        print(response.text)
        return json.loads(response.text)


class DeleteBlackListApi(SheetLoginBaseApi):
    """删除黑名单接口"""

    url = '/netCarAdminAuth/blackList/deleteBlack'

    def build_custom_param(self, params):
        return {'passId':params['passId'],'userId':params['userId']}

class GetBlackListApi(SheetLoginBaseApi):

    """获取黑名单的列表"""
    url = '/netCarAdminAuth/blackList/getBlackList'
