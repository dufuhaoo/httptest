# -*- coding:utf-8 -*-
import datetime,time
import os,requests
from ApiManager.pf_netcar_api.sheet.image_manager_api import AddImageApi, GetIamgeListApi, EditImageApi,RefreshImageApi,DelImageApi,UpdateImageSortApi
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from HttpRunnerManager.settings import BASE_DIR
from ApiManager.pf_netcar_api.trade.banner_screen_image_api import BannerImageApi,ScreenImageApi
from ApiManager.utils.redis_helper import IMAGE_MONITORING_KEY
from ApiManager.utils import hooks


class ImagerManagerMonitoring(BaseMonitoring):
    """图片配置管理"""
    banner_excel_file_path = os.path.join(BASE_DIR, './ApiManager/pf_netcar_monitoring/hengtu.jpg')
    screen_excel_file_path = os.path.join(BASE_DIR, './ApiManager/pf_netcar_monitoring/shutu.jpeg')
    startTime = None
    endTime = None
    edit_start_time = None
    edit_future_start_time = None
    edit_end_time = None


    def setUp(self):
        self.startTime = str((datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S'))
        self.endTime = str((datetime.datetime.now() + datetime.timedelta(days=+3)).strftime('%Y-%m-%d %H:%M:%S'))
        self.edit_start_time = str((datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S'))
        self.edit_future_start_time = str((datetime.datetime.now() + datetime.timedelta(days=+2)).strftime('%Y-%m-%d %H:%M:%S'))
        self.edit_end_time = str((datetime.datetime.now() + datetime.timedelta(days=+2)).strftime('%Y-%m-%d %H:%M:%S'))


    def _get_banner_path(self):
        """获取banner路径"""
        excel_file_path = self.banner_excel_file_path
        files = {'imageFile': ('image.jpg', open(excel_file_path, 'rb'), 'image/jpeg')}
        return files

    def _get_screen_path(self):
        """获取screen路径"""
        excel_file_path = self.screen_excel_file_path
        files = {'imageFile': ('image.jpg', open(excel_file_path, 'rb'), 'image/jpeg')}
        return files

    def _refresh_api(self):
        """获取banner图片刷新的接口"""
        for x in [1,2]:
            refresh_api = RefreshImageApi()
            refresh_api.get({'type': x})
            assert refresh_api.get_status_code() == 200
            assert refresh_api.get_resp_code() == 0
            assert refresh_api.get_resp_message() == 'OK'

    def _create_banner_image(self):
        """创建banner图片"""
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime,'endTime': self.endTime, 'state': 1, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 获取列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

    def _create_screen_image(self):
        # 创建弹屏
        screen_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime,'endTime': self.endTime, 'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 查询列表
        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'


    def add_banner_image_abnormal(self):
        """测试banner图片"""

        # 测试banner图片跳转类型为空
        banner_image_api = AddImageApi()
        request_data = {'jumpType': None, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': self.endTime, 'state': 1, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试banner url类型为空
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': None, 'startTime': self.startTime, 'endTime': self.endTime, 'state': 1,'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试banner图片开始时间为空
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': '', 'endTime': self.endTime,'state': 1, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试banner图片结束时间为空
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': '','state': 1, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试banner图片类型为空
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': self.endTime, 'state': 1, 'type': ''}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

    def edit_banner_image(self):
        """
        修改banner图片
        :return:
        """
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime,'endTime': self.endTime, 'state': 1, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'
        """banner图片请求验证"""
        page_image = get_res_data['data']['list'][0]['pageImage']
        assert requests.get(url=page_image).status_code == 200
        id = get_res_data['data']['list'][0]['id']
        # 刷新缓存
        self._refresh_api()
        # trade端验证
        trade_banner_image_api = BannerImageApi()
        trade_banner_image_api.get()
        assert trade_banner_image_api.get_status_code() == 200
        assert trade_banner_image_api.get_resp_code() == 0
        assert trade_banner_image_api.get_resp_message() == 'OK'
        trade_banner_image_data = trade_banner_image_api.get_resp_data()
        assert trade_banner_image_data[0]['pageImage'] == page_image
        assert trade_banner_image_data[0]['jumpType'] == 1
        assert trade_banner_image_data[0]['url'] == 'http://www.baidu.com'
        screen_image_api = ScreenImageApi()
        screen_image_api.get()
        assert screen_image_api.get_status_code() == 200
        assert screen_image_api.get_resp_code() == 0
        assert screen_image_api.get_resp_message() == 'OK'
        screen_image_data = screen_image_api.get_resp_data()
        assert screen_image_data == []

        # 修改banner跳转类型为空
        banner_image_api = EditImageApi()
        request_data = {'jumpType': '', 'url': 'http://www.baidu.com', 'startTime': self.startTime,'endTime': self.endTime, 'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改banner url为空
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': None, 'startTime': self.startTime, 'endTime': self.endTime, 'id': id,'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改banner 开始时间为空
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': '', 'endTime': self.endTime,'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改banner 结束时间为空
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': None, 'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改banner图片类型为空
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': self.endTime, 'id': id, 'type': ''}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改banner跳转类型成功
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 2, 'url': 'http://www.baidu.com', 'startTime': self.startTime,'endTime': self.endTime, 'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 2
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'
        assert get_res_data['data']['list'][0]['state'] == 1
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200

        # 修改banner url成功
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': '123456xxx', 'startTime': self.startTime, 'endTime': self.endTime,  'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == '123456xxx'
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200

        # 修改banner开始时间成功
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.edit_start_time,'endTime': self.endTime, 'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.edit_start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200


        # 修改banner结束时间成功
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime,'endTime': self.edit_end_time, 'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.edit_end_time
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200


        # 修改banner图片所有数据成功
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 2, 'url': '123456xxx', 'startTime': self.edit_start_time,'endTime': self.edit_end_time, 'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.edit_end_time
        assert get_res_data['data']['list'][0]['startTime'] == self.edit_start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int( time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 2
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == '123456xxx'
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200

        # trade端验证
        trade_banner_image_api = BannerImageApi()
        trade_banner_image_api.get()
        assert trade_banner_image_api.get_status_code() == 200
        assert trade_banner_image_api.get_resp_code() == 0
        assert trade_banner_image_api.get_resp_message() == 'OK'
        trade_banner_image_data = trade_banner_image_api.get_resp_data()
        assert trade_banner_image_data[0]['pageImage'] == get_res_data['data']['list'][0]['pageImage']
        assert trade_banner_image_data[0]['jumpType'] == 2
        assert trade_banner_image_data[0]['url'] == '123456xxx'

        screen_image_api = ScreenImageApi()
        screen_image_api.get()
        assert screen_image_api.get_status_code() == 200
        assert screen_image_api.get_resp_code() == 0
        assert screen_image_api.get_resp_message() == 'OK'
        screen_image_data = screen_image_api.get_resp_data()
        assert screen_image_data == []

        # 修改banner开始时间为明天
        banner_image_api = EditImageApi()
        request_data = {'jumpType': 2, 'url': '123456xxx', 'startTime': self.edit_future_start_time,'endTime': self.edit_end_time, 'id': id, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.edit_end_time
        assert get_res_data['data']['list'][0]['startTime'] == self.edit_future_start_time
        create_time = int(
            time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(
            time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 2
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == '123456xxx'
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200

        # trade端验证
        trade_banner_image_api = BannerImageApi()
        trade_banner_image_api.get()
        assert trade_banner_image_api.get_status_code() == 200
        assert trade_banner_image_api.get_resp_code() == 0
        assert trade_banner_image_api.get_resp_message() == 'OK'
        trade_banner_image_data = trade_banner_image_api.get_resp_data()
        assert trade_banner_image_data == []


        screen_image_api = ScreenImageApi()
        screen_image_api.get()
        assert screen_image_api.get_status_code() == 200
        assert screen_image_api.get_resp_code() == 0
        assert screen_image_api.get_resp_message() == 'OK'
        screen_image_data = screen_image_api.get_resp_data()
        assert screen_image_data == []

        # 删除banner图片
        del_image = DelImageApi()
        del_image.post({'id': id})
        assert del_image.get_resp_code() == 0
        assert del_image.get_resp_message() == 'OK'
        self._refresh_api()
        # 查询列表
        get_banner_image_api = GetIamgeListApi()
        get_banner_image_api.get({'type': 2})
        get_res_data = get_banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'] == []

        #trade登录，验证是否删除
        screen_image_trade = ScreenImageApi()
        screen_image_trade.get()
        get_res_data = screen_image_trade.get_resp_content()
        assert get_res_data['data'] == []
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        # trade登录，验证是否删除
        banner_image_trade_login = BannerImageApi()
        banner_image_trade_login.get()
        get_res_data = banner_image_trade_login.get_resp_content()
        assert get_res_data['data'] == []
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'

    def banner_image_sort(self):
        """banner的上下移动
        """
        # 创建三张banner
        for x in ['http://www.baidu.com','http://www.google.com','http://www.zrong.cn']:
            banner_image_api = AddImageApi()
            request_data = {'jumpType': 1, 'url': x, 'startTime': self.startTime,'endTime': self.endTime, 'state': 1, 'type': 2}
            response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
            assert response_result['code'] == 0
            assert response_result['msg'] == 'OK'
            time.sleep(2)
        # 刷新缓存
        self._refresh_api()
        # 验证列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['data']['list'][0]['url'] == 'http://www.zrong.cn'
        assert get_res_data['data']['list'][0]['sort'] == 3
        three_id = get_res_data['data']['list'][0]['id']
        assert get_res_data['data']['list'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data']['list'][1]['sort'] == 2
        two_id = get_res_data['data']['list'][1]['id']
        assert get_res_data['data']['list'][2]['url'] == 'http://www.baidu.com'
        assert get_res_data['data']['list'][2]['sort'] == 1
        # 验证trade端
        banner_image_trade_login = BannerImageApi()
        banner_image_trade_login.get()
        get_res_data = banner_image_trade_login.get_resp_content()
        assert get_res_data['data'][2]['url'] == 'http://www.baidu.com'
        assert get_res_data['data'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data'][0]['url'] == 'http://www.zrong.cn'
        # 调用需改顺序接口
        update_image_api = UpdateImageSortApi()
        update_image_api.post({'nowId':three_id,'sort':2,'swId':two_id,'swSort':3,'type':2})
        assert update_image_api.get_resp_code() == 0
        assert update_image_api.get_resp_message() == 'OK'
        # 刷新缓存
        self._refresh_api()
        # 验证列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['data']['list'][0]['url'] == 'http://www.zrong.cn'
        assert get_res_data['data']['list'][0]['sort'] == 3
        assert get_res_data['data']['list'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data']['list'][1]['sort'] == 2
        assert get_res_data['data']['list'][2]['url'] == 'http://www.baidu.com'
        assert get_res_data['data']['list'][2]['sort'] == 1

        # 验证trade端
        banner_image_trade_login = BannerImageApi()
        banner_image_trade_login.get()
        get_res_data = banner_image_trade_login.get_resp_content()
        assert get_res_data['data'][0]['url'] == 'http://www.zrong.cn'
        assert get_res_data['data'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data'][2]['url'] == 'http://www.baidu.com'

    def screen_image_sort(self):
        """弹屏的上下移动
        """
        # 创建三张弹屏
        for x in ['http://www.baidu.com', 'http://www.google.com', 'http://www.zrong.cn']:
            image_api = AddImageApi()
            request_data = {'jumpType': 1, 'url': x, 'startTime': self.startTime, 'endTime': self.endTime, 'state': 1,
                            'type': 1}
            response_result = image_api.request_api(data=request_data, file=self._get_banner_path())
            assert response_result['code'] == 0
            assert response_result['msg'] == 'OK'
            time.sleep(2)
        # 刷新缓存
        self._refresh_api()
        # 验证列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['data']['list'][0]['url'] == 'http://www.zrong.cn'
        assert get_res_data['data']['list'][0]['sort'] == 3
        three_id = get_res_data['data']['list'][0]['id']
        assert get_res_data['data']['list'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data']['list'][1]['sort'] == 2
        two_id = get_res_data['data']['list'][1]['id']
        assert get_res_data['data']['list'][2]['url'] == 'http://www.baidu.com'
        assert get_res_data['data']['list'][2]['sort'] == 1
        # 验证trade端
        screen_image_trade_login = ScreenImageApi()
        screen_image_trade_login.get()
        get_res_data = screen_image_trade_login.get_resp_content()
        assert get_res_data['data'][2]['url'] == 'http://www.baidu.com'
        assert get_res_data['data'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data'][0]['url'] == 'http://www.zrong.cn'
        # 调用需改顺序接口
        update_image_api = UpdateImageSortApi()
        update_image_api.post({'nowId': three_id, 'sort': 2, 'swId': two_id, 'swSort': 3, 'type': 2})
        assert update_image_api.get_resp_code() == 0
        assert update_image_api.get_resp_message() == 'OK'
        # 刷新缓存
        self._refresh_api()
        # 验证列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['data']['list'][0]['url'] == 'http://www.zrong.cn'
        assert get_res_data['data']['list'][0]['sort'] == 3
        assert get_res_data['data']['list'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data']['list'][1]['sort'] == 2
        assert get_res_data['data']['list'][2]['url'] == 'http://www.baidu.com'
        assert get_res_data['data']['list'][2]['sort'] == 1

        # 验证trade端
        screen_image_trade_login = ScreenImageApi()
        screen_image_trade_login.get()
        get_res_data = screen_image_trade_login.get_resp_content()
        assert get_res_data['data'][0]['url'] == 'http://www.zrong.cn'
        assert get_res_data['data'][1]['url'] == 'http://www.google.com'
        assert get_res_data['data'][2]['url'] == 'http://www.baidu.com'

    def add_screen_image_abnormal(self):
        # 测试广告弹屏跳转类型为空
        screen_image_api = AddImageApi()
        request_data = {'jumpType': '', 'url': '123456', 'startTime': self.startTime, 'endTime': self.endTime, 'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试广告弹屏地址为空
        screen_image_api = AddImageApi()
        request_data = {'jumpType': 2, 'url': '', 'startTime': self.startTime, 'endTime': self.endTime, 'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试广告弹屏开始时间为空
        screen_image_api = AddImageApi()
        request_data = {'jumpType': 2, 'url': '123456', 'startTime': '', 'endTime': self.endTime, 'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试广告弹屏结束时间为空
        screen_image_api = AddImageApi()
        request_data = {'jumpType': 2, 'url': '123456', 'startTime': self.startTime, 'endTime': '', 'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试广告弹屏图片类型为空
        screen_image_api = AddImageApi()
        request_data = {'jumpType': 2, 'url': '123456', 'startTime': self.startTime, 'endTime': self.endTime, 'state': 1, 'type': ''}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 测试广告弹屏跳转类型为空
        screen_image_api = AddImageApi()
        request_data = {'jumpType': '', 'url': '123456', 'startTime': self.startTime, 'endTime': self.endTime,
                        'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

    def edit_screen_image(self):
        """
        修改screen图片
        :return:
        """
        screen_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime,'endTime': self.endTime, 'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'],"%Y-%m-%d %H:%M:%S")))
        assert create_time-int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'
        """screen图片请求验证"""
        page_image = get_res_data['data']['list'][0]['pageImage']
        assert requests.get(url=page_image).status_code == 200
        id = get_res_data['data']['list'][0]['id']
        self._refresh_api()
        time.sleep(5)

        # trade端验证
        trade_screen_image_api = ScreenImageApi()
        trade_screen_image_api.get()
        assert trade_screen_image_api.get_status_code() == 200
        assert trade_screen_image_api.get_resp_code() == 0
        assert trade_screen_image_api.get_resp_message() == 'OK'
        trade_screen_image_data = trade_screen_image_api.get_resp_data()
        assert trade_screen_image_data[0]['pageImage'] == page_image
        assert trade_screen_image_data[0]['jumpType'] == 1
        assert trade_screen_image_data[0]['url'] == 'http://www.baidu.com'
        banner_image_api = BannerImageApi()
        banner_image_api.get()
        assert banner_image_api.get_status_code() == 200
        assert banner_image_api.get_resp_code() == 0
        assert banner_image_api.get_resp_message() == 'OK'
        screen_image_data = banner_image_api.get_resp_data()
        assert screen_image_data == []


        # 修改screen跳转类型为空
        screen_image_api = EditImageApi()
        request_data = {'jumpType': '', 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': self.endTime, 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改screen url为空
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': '', 'startTime': self.startTime, 'endTime': self.endTime, 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改screen 开始时间为空
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': '', 'endTime': self.endTime, 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改screen 结束时间为空
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': '', 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改screen图片类型为空
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime,  'endTime': self.endTime, 'id': id, 'type': ''}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 100101
        assert response_result['msg'] == '请检查输入项'

        # 修改screen跳转类型成功
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 2, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': self.endTime, 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 2
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 修改screen url成功
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': '123456xxx', 'startTime': self.startTime, 'endTime': self.endTime,'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == '123456xxx'

        # 修改screen开始时间成功
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.edit_start_time, 'endTime': self.endTime, 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.endTime
        assert get_res_data['data']['list'][0]['startTime'] == self.edit_start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int( time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 修改screen结束时间成功
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': self.startTime, 'endTime': self.edit_end_time, 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.edit_end_time
        assert get_res_data['data']['list'][0]['startTime'] == self.startTime
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 修改screen图片所有数据成功
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 2, 'url': '123456xxx', 'startTime': self.edit_start_time, 'endTime': self.edit_end_time,'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.edit_end_time
        assert get_res_data['data']['list'][0]['startTime'] == self.edit_start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 2
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == '123456xxx'
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200

        # trade端验证
        trade_screen_image_api = ScreenImageApi()
        trade_screen_image_api.get()
        assert trade_screen_image_api.get_status_code() == 200
        assert trade_screen_image_api.get_resp_code() == 0
        assert trade_screen_image_api.get_resp_message() == 'OK'
        trade_screen_image_data = trade_screen_image_api.get_resp_data()
        assert trade_screen_image_data[0]['pageImage'] == get_res_data['data']['list'][0]['pageImage']
        assert trade_screen_image_data[0]['jumpType'] == 2
        assert trade_screen_image_data[0]['url'] == '123456xxx'
        banner_image_api = BannerImageApi()
        banner_image_api.get()
        assert banner_image_api.get_status_code() == 200
        assert banner_image_api.get_resp_code() == 0
        assert banner_image_api.get_resp_message() == 'OK'
        screen_image_data = banner_image_api.get_resp_data()
        assert screen_image_data == []


        #修改开始时间为未来时间
        screen_image_api = EditImageApi()
        request_data = {'jumpType': 2, 'url': '123456xxx', 'startTime': self.edit_future_start_time, 'endTime': self.edit_end_time, 'id': id, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        self._refresh_api()

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == self.edit_end_time
        assert get_res_data['data']['list'][0]['startTime'] == self.edit_future_start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        update_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['updateTime'], "%Y-%m-%d %H:%M:%S")))
        assert update_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 2
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == '123456xxx'
        assert get_res_data['data']['list'][0]['pageImage'] != None
        assert requests.get(url=get_res_data['data']['list'][0]['pageImage']).status_code == 200

        # trade端验证
        trade_screen_image_api = ScreenImageApi()
        trade_screen_image_api.get()
        assert trade_screen_image_api.get_status_code() == 200
        assert trade_screen_image_api.get_resp_code() == 0
        assert trade_screen_image_api.get_resp_message() == 'OK'
        trade_screen_image_data = trade_screen_image_api.get_resp_data()
        assert trade_screen_image_data == []
        banner_image_api = BannerImageApi()
        banner_image_api.get()
        assert banner_image_api.get_status_code() == 200
        assert banner_image_api.get_resp_code() == 0
        assert banner_image_api.get_resp_message() == 'OK'
        screen_image_data = banner_image_api.get_resp_data()
        assert screen_image_data == []

        # 删除screen图片
        del_image = DelImageApi()
        del_image.post({'id': id})
        assert del_image.get_resp_code() == 0
        assert del_image.get_resp_message() == 'OK'
        self._refresh_api()

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'] == []

        # trade登录，验证是否删除
        screen_image_trade = ScreenImageApi()
        screen_image_trade.get()
        get_res_data = screen_image_trade.get_resp_content()
        assert get_res_data['data'] == []
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        # trade登录，验证是否删除
        banner_image_trade_login = BannerImageApi()
        banner_image_trade_login.get()
        get_res_data = banner_image_trade_login.get_resp_content()
        assert get_res_data['data'] == []
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'

    def query_banner_image_auto_overdue(self):
        """查询trade图片自动过期"""
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(minutes=+1)).strftime("%Y-%m-%d %H:%M:%S")

        #创建banner图片
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': start_time,'endTime': end_time, 'state': 1, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        # 查询列表
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'
        """banner图片请求验证"""
        page_image = get_res_data['data']['list'][0]['pageImage']
        assert requests.get(url=page_image).status_code == 200
        # 刷新缓存
        self._refresh_api()

        trade_banner_image_api = BannerImageApi()
        trade_banner_image_api.get()

        assert trade_banner_image_api.get_status_code() == 200
        assert trade_banner_image_api.get_resp_code() == 0
        assert trade_banner_image_api.get_resp_message() == 'OK'
        trade_banner_image_data = trade_banner_image_api.get_resp_data()
        assert trade_banner_image_data[0]['pageImage'] == page_image
        assert trade_banner_image_data[0]['jumpType'] == 1
        assert trade_banner_image_data[0]['url'] == 'http://www.baidu.com'
        screen_image_api = ScreenImageApi()
        screen_image_api.get()
        assert screen_image_api.get_status_code() == 200
        assert screen_image_api.get_resp_code() == 0
        assert screen_image_api.get_resp_message() == 'OK'
        screen_image_data = screen_image_api.get_resp_data()
        assert screen_image_data == []

        count = 1
        max_count = 200
        while count < max_count:
        # trade端验证
            trade_banner_image_api.get()
            query_trade_banner_image_data = trade_banner_image_api.get_resp_data()
            if len(query_trade_banner_image_data) == 1:
                count += 1
                time.sleep(5)
                continue
            else:
                assert trade_banner_image_api.get_status_code() == 200
                assert trade_banner_image_api.get_resp_code() == 0
                assert trade_banner_image_api.get_resp_message() == 'OK'
                trade_banner_image_data = trade_banner_image_api.get_resp_data()
                assert trade_banner_image_data == []
                screen_image_api.get()
                assert screen_image_api.get_status_code() == 200
                assert screen_image_api.get_resp_code() == 0
                assert screen_image_api.get_resp_message() == 'OK'
                screen_image_data = screen_image_api.get_resp_data()
                assert screen_image_data == []
                break
        assert count < max_count

    def query_screen_image_auto_overdue(self):
        """查询弹屏图片自动过期"""
        now_time = datetime.datetime.now()
        start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (now_time + datetime.timedelta(minutes=+1)).strftime("%Y-%m-%d %H:%M:%S")

        screen_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': start_time,'endTime': end_time, 'state': 1, 'type': 1}
        response_result = screen_image_api.request_api(data=request_data, file=self._get_screen_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'

        screen_image_api = GetIamgeListApi()
        screen_image_api.get({'type': 1})
        get_res_data = screen_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(
            time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'
        """screen图片请求验证"""
        page_image = get_res_data['data']['list'][0]['pageImage']
        assert requests.get(url=page_image).status_code == 200
        self._refresh_api()

        # trade端验证
        trade_screen_image_api = ScreenImageApi()
        trade_screen_image_api.get()
        assert trade_screen_image_api.get_status_code() == 200
        assert trade_screen_image_api.get_resp_code() == 0
        assert trade_screen_image_api.get_resp_message() == 'OK'
        trade_screen_image_data = trade_screen_image_api.get_resp_data()
        assert trade_screen_image_data[0]['pageImage'] == page_image
        assert trade_screen_image_data[0]['jumpType'] == 1
        assert trade_screen_image_data[0]['url'] == 'http://www.baidu.com'
        banner_image_api = BannerImageApi()
        banner_image_api.get()
        assert banner_image_api.get_status_code() == 200
        assert banner_image_api.get_resp_code() == 0
        assert banner_image_api.get_resp_message() == 'OK'
        screen_image_data = banner_image_api.get_resp_data()
        assert screen_image_data == []

        count = 1
        max_count = 200
        while count < max_count:
            # trade端验证
            trade_screen_image_api.get()
            query_trade_screen_image_data = trade_screen_image_api.get_resp_data()
            if len(query_trade_screen_image_data) == 1:
                count += 1
                time.sleep(5)
                continue
            else:
                assert trade_screen_image_api.get_status_code() == 200
                assert trade_screen_image_api.get_resp_code() == 0
                assert trade_screen_image_api.get_resp_message() == 'OK'
                trade_screen_image_data = trade_screen_image_api.get_resp_data()
                assert trade_screen_image_data == []
                banner_image_api.get()
                assert banner_image_api.get_status_code() == 200
                assert banner_image_api.get_resp_code() == 0
                assert banner_image_api.get_resp_message() == 'OK'
                banner_image_data = banner_image_api.get_resp_data()
                assert banner_image_data == []
                break
        assert count < max_count

    def query_banner_image_time(self):

        start_time = str((datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))
        future_start_time = str((datetime.datetime.now() + datetime.timedelta(days=+2)).strftime('%Y-%m-%d %H:%M:%S'))
        end_time = str((datetime.datetime.now() + datetime.timedelta(days=+3)).strftime('%Y-%m-%d %H:%M:%S'))
        ago_start_time = str((datetime.datetime.now() + datetime.timedelta(days=-2)).strftime('%Y-%m-%d %H:%M:%S'))
        future_end_time = str((datetime.datetime.now() + datetime.timedelta(days=+4)).strftime('%Y-%m-%d %H:%M:%S'))

        #创建banner图片
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': start_time, 'endTime': end_time, 'state': 1, 'type': 2}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
       #按当前的开始时间和三天后的结束时间查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2,'begTime':start_time,'endTime':end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int( time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 按开始时间查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': start_time, 'endTime': ''})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 按结束时间查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': '', 'endTime': end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        #按开始时间之前和结束时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime':ago_start_time , 'endTime': future_end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        #按照开始时间之前和结束时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': ago_start_time, 'endTime': future_start_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0


        #按开始时间之后和结束时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': future_start_time, 'endTime': future_end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        #按开始时间之后和结束时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': future_start_time, 'endTime': future_start_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        #开始时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': ago_start_time, 'endTime': ''})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int( time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        #开始时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': future_start_time, 'endTime': ''})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        #结束时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': '', 'endTime': future_start_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        #结束时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 2, 'begTime': '', 'endTime': future_end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(
            time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 2
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'


    def query_screen_image_time(self):
        start_time = str((datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))
        future_start_time = str((datetime.datetime.now() + datetime.timedelta(days=+2)).strftime('%Y-%m-%d %H:%M:%S'))
        end_time = str((datetime.datetime.now() + datetime.timedelta(days=+3)).strftime('%Y-%m-%d %H:%M:%S'))
        ago_start_time = str((datetime.datetime.now() + datetime.timedelta(days=-2)).strftime('%Y-%m-%d %H:%M:%S'))
        future_end_time = str((datetime.datetime.now() + datetime.timedelta(days=+4)).strftime('%Y-%m-%d %H:%M:%S'))

        # 创建screen图片
        banner_image_api = AddImageApi()
        request_data = {'jumpType': 1, 'url': 'http://www.baidu.com', 'startTime': start_time, 'endTime': end_time,'state': 1, 'type': 1}
        response_result = banner_image_api.request_api(data=request_data, file=self._get_banner_path())
        assert response_result['code'] == 0
        assert response_result['msg'] == 'OK'
        # 按当前的开始时间和三天后的结束时间查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': start_time, 'endTime': end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int( time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 按开始时间查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': start_time, 'endTime': ''})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(
            time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 按结束时间查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': '', 'endTime': end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 按开始时间之前和结束时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': ago_start_time, 'endTime': future_end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 按照开始时间之前和结束时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': ago_start_time, 'endTime': future_start_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        # 按开始时间之后和结束时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': future_start_time, 'endTime': future_end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        # 按开始时间之后和结束时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': future_start_time, 'endTime': future_start_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        # 开始时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': ago_start_time, 'endTime': ''})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

        # 开始时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': future_start_time, 'endTime': ''})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        # 结束时间之前查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': '', 'endTime': future_start_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 0

        # 结束时间之后查询
        banner_image_api = GetIamgeListApi()
        banner_image_api.get({'type': 1, 'begTime': '', 'endTime': future_end_time})
        get_res_data = banner_image_api.get_resp_content()
        assert get_res_data['code'] == 0
        assert get_res_data['msg'] == 'OK'
        assert len(get_res_data['data']['list']) == 1
        assert get_res_data['data']['list'][0]['endTime'] == end_time
        assert get_res_data['data']['list'][0]['startTime'] == start_time
        create_time = int(time.mktime(time.strptime(get_res_data['data']['list'][0]['createTime'], "%Y-%m-%d %H:%M:%S")))
        assert create_time - int(time.time()) < 120
        assert get_res_data['data']['list'][0]['jumpType'] == 1
        assert get_res_data['data']['list'][0]['type'] == 1
        assert get_res_data['data']['list'][0]['url'] == 'http://www.baidu.com'

    def tearDown(self):
        super(ImagerManagerMonitoring, self).tearDown()
        hooks.delete_image()



if __name__ == '__main__':

    api = ImagerManagerMonitoring()
    # api.setUp()
    # api.tearDown()
    # api.screen_image_sort()
    # api.tearDown()
    api.run_method(monitoring_name='图片配置管理监控', monitoring_class=api, redis_key=IMAGE_MONITORING_KEY)
