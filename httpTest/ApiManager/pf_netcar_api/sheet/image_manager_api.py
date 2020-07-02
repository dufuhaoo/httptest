from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi
import requests,json


class AddImageApi(SheetLoginBaseApi):

    """添加图片接口"""


    url = '/netCarAdminAuth/ImageController/addImage'

    def build_custom_param(self, data):
        return {'jumpType': data['jumpType'], 'url':data['url'], 'startTime': data['startTime'],'endTime': data['endTime'], 'state': data['state'], 'type': data['type']}

    def request_api(self, data, file=None):
        cookie_value = self.get_cookie()
        s = requests.session()
        s.headers.setdefault('Cookie', cookie_value)
        response = s.post(url=self.api_url(), data=data,files=file)
        return json.loads(response.text)


class EditImageApi(SheetLoginBaseApi):

    """修改图片接口"""
    url = '/netCarAdminAuth/ImageController/editImage'

    def build_custom_param(self, data):
        return {'jumpType': data['jumpType'], 'url':data['url'], 'startTime': data['startTime'],'endTime': data['endTime'], 'id': data['id'], 'type': data['type']}

    def request_api(self, data, file):
        cookie_value = self.get_cookie()
        s = requests.session()
        s.headers.setdefault('Cookie', cookie_value)
        response = s.post(url=self.api_url(), data=data,files=file)
        return json.loads(response.text)



class GetIamgeListApi(SheetLoginBaseApi):

    """获取图片接口"""

    url = '/netCarAdminAuth/ImageController/getAdList'
    def build_custom_param(self, params):
        return params

class RefreshImageApi(SheetLoginBaseApi):

    """刷新图片接口"""

    url = '/netCarAdminAuth/ImageController/refreshImageCache'

    def build_custom_param(self, data):
        return {'type': data['type']}

class DelImageApi(SheetLoginBaseApi):

    """删除图片接口"""

    url = '/netCarAdminAuth/ImageController/delImage'

    def build_custom_param(self, data):
        return {'id': data['id']}

class UpdateImageSortApi(SheetLoginBaseApi):

    """图片排序接口"""

    url = '/netCarAdminAuth/ImageController/updateImageSort'

    def build_custom_param(self, data):
        return {'nowId':data['nowId'],'sort':data['sort'],'swId':data['swId'],'swSort':data['swSort'],'type':data['type']}




