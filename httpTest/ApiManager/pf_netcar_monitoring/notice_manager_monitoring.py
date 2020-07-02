# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.sheet.notice_manager_api import AddNoticeApi,GetNoticeApi,EditNoticeApi,DeleteNoticeApi
from ApiManager.pf_netcar_api.trade.get_notice_list_api import GetNoticeListApi,GetNoticeListNotLoginApi
from ApiManager.utils import hooks
from ApiManager.utils.redis_helper import NOTICE_MANAGER_MONITORING_KEY
import datetime,time




class NoticeManagerMonitoring(BaseMonitoring):
    """
    通知管理监控
    """

    def setUp(self):
        super(NoticeManagerMonitoring,self).setUp()
        hooks.clean_notice()
        now_time = datetime.datetime.now()
        self.now_time = datetime.datetime.now()
        self.start_time = (now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")

    def add_notice_open_success(self):
        """
        测试添加通知状态为开启
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":'中秋节打车活动',"state":1,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # trade端验证-未登录
        trade_get_notice_api_not_login = GetNoticeListNotLoginApi()
        trade_get_notice_api_not_login.get()
        assert trade_get_notice_api_not_login.get_status_code() == 200
        assert trade_get_notice_api_not_login.get_resp_code() == 0
        assert trade_get_notice_api_not_login.get_resp_message() == 'OK'
        trade_notice_data = trade_get_notice_api_not_login.get_resp_data()
        assert len(trade_notice_data) == 1
        assert trade_notice_data[0]['content'] == '中秋节打车活动'
        assert trade_notice_data[0]['jumpType'] == None
        assert trade_notice_data[0]['url'] == None
        # trade端验证-已登录
        trade_get_notice_api = GetNoticeListApi()
        trade_get_notice_api.get()
        assert trade_get_notice_api.get_status_code() == 200
        assert trade_get_notice_api.get_resp_code() == 0
        assert trade_get_notice_api.get_resp_message() == 'OK'
        trade_notice_data = trade_get_notice_api.get_resp_data()
        assert len(trade_notice_data) == 1
        assert trade_notice_data[0]['content'] == '中秋节打车活动'
        assert trade_notice_data[0]['jumpType'] == None
        assert trade_notice_data[0]['url'] == None

    def add_notice_close_success(self):
        """
        测试添加通知状态为关闭
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":'中秋节打车活动',"state":0,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'

    def add_notice_open_content_20(self):
        """
        测试添加通知内容20个字
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":'一二三四五六七八九十一二三四五六七八九十',"state":1,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'

    def add_notice_open_content_21(self):
        """
        测试添加通知内容21个字
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":'一二三四五六七八九十一二三四五六七八九十一',"state":1,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 100101
        assert add_notice_api.get_resp_message() == '请检查输入项'
        assert add_notice_api.get_resp_data() == '字段[content]格式错误！'

    def add_notice_open_content_is_null(self):
        """
        测试添加通知内容为空
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":None,"state":1,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'

    def add_notice_open_content_state_null(self):
        """
        测试添加通知状态为空
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":'123',"state":None,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'

    def add_notice_outside_link(self):
        """
        测试添加通知外链
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":"添加外链","url":"http://www.baidu.com","state":1,"jumpType":1})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # 查询通知
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': 1})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '添加外链'
        assert resp_data['list'][0]['startTime'] == self.start_time
        assert resp_data['list'][0]['state'] == 1
        assert resp_data['list'][0]['url'] == 'http://www.baidu.com'
        assert resp_data['list'][0]['jumpType'] == 1
        assert resp_data['list'][0]['endTime'] == self.end_time
        assert resp_data['list'][0]['sort'] == ''
        # trade端验证-已登录
        trade_get_notice_api = GetNoticeListApi()
        trade_get_notice_api.get()
        assert trade_get_notice_api.get_status_code() == 200
        assert trade_get_notice_api.get_resp_code() == 0
        assert trade_get_notice_api.get_resp_message() == 'OK'
        trade_notice_data = trade_get_notice_api.get_resp_data()
        assert len(trade_notice_data) == 1
        assert trade_notice_data[0]['content'] == '添加外链'
        assert trade_notice_data[0]['jumpType'] == 1
        assert trade_notice_data[0]['url'] == 'http://www.baidu.com'

    def add_notice_in_link(self):
        """
        测试添加通知内链
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":"添加内链","url":"8888888888","state":1,"jumpType":2})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # 查询通知
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': 1})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '添加内链'
        assert resp_data['list'][0]['startTime'] == self.start_time
        assert resp_data['list'][0]['state'] == 1
        assert resp_data['list'][0]['url'] == '8888888888'
        assert resp_data['list'][0]['jumpType'] == 2
        assert resp_data['list'][0]['endTime'] == self.end_time
        assert resp_data['list'][0]['sort'] == ''
        # trade端验证-已登录
        trade_get_notice_api = GetNoticeListApi()
        trade_get_notice_api.get()
        assert trade_get_notice_api.get_status_code() == 200
        assert trade_get_notice_api.get_resp_code() == 0
        assert trade_get_notice_api.get_resp_message() == 'OK'
        trade_notice_data = trade_get_notice_api.get_resp_data()
        assert len(trade_notice_data) == 1
        assert trade_notice_data[0]['content'] == '添加内链'
        assert trade_notice_data[0]['jumpType'] == 2
        assert trade_notice_data[0]['url'] == '8888888888'


    def query_notice_list(self):
        """
        测试查询通知列表
        :return:
        """
        # 添加状态为开启的通知
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":'中秋节打车活动',"state":1,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # 添加状态为关闭的通知
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":'元宵节打车活动',"state":0,"url":None,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # 查询状态为开启
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': 1})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '中秋节打车活动'
        assert resp_data['list'][0]['startTime'] == self.start_time
        assert resp_data['list'][0]['state'] == 1
        assert resp_data['list'][0]['url'] == ''
        assert resp_data['list'][0]['jumpType'] == ''
        assert resp_data['list'][0]['endTime'] == self.end_time
        assert resp_data['list'][0]['sort'] == ''
        # 查询状态为关闭
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': 0})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '元宵节打车活动'
        assert resp_data['list'][0]['startTime'] == self.start_time
        assert resp_data['list'][0]['state'] == 0
        assert resp_data['list'][0]['url'] == ''
        assert resp_data['list'][0]['jumpType'] == ''
        assert resp_data['list'][0]['endTime'] == self.end_time
        assert resp_data['list'][0]['sort'] == ''
        # 查询状态为全部
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': None})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '元宵节打车活动'
        assert resp_data['list'][0]['startTime'] == self.start_time
        assert resp_data['list'][0]['state'] == 0
        assert resp_data['list'][0]['url'] == ''
        assert resp_data['list'][0]['jumpType'] == ''
        assert resp_data['list'][0]['endTime'] == self.end_time
        assert resp_data['list'][0]['sort'] == ''
        assert resp_data['list'][1]['content'] == '中秋节打车活动'
        assert resp_data['list'][1]['startTime'] == self.start_time
        assert resp_data['list'][1]['state'] == 1
        assert resp_data['list'][1]['url'] == ''
        assert resp_data['list'][1]['jumpType'] == ''
        assert resp_data['list'][1]['endTime'] == self.end_time
        assert resp_data['list'][1]['sort'] == ''

    def edit_notice(self):
        """
        测试修改通知状态为关闭
        :return:
        """
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":"添加通知状态为开启","url":None,"state":1,"jumpType":None})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # 查询通知
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': 1})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        notice_id = resp_data['list'][0]['id']
        # 修改通知状态为关闭
        edit_notice_api = EditNoticeApi()
        edit_notice_api.post({"id":notice_id,"state":0,"content":"测试修改状态为关闭"})
        assert edit_notice_api.get_status_code() == 200
        assert edit_notice_api.get_resp_code() == 0
        assert edit_notice_api.get_resp_message() == 'OK'
        # 查询状态为全部
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': None})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '测试修改状态为关闭'
        assert resp_data['list'][0]['startTime'] == self.start_time
        assert resp_data['list'][0]['state'] == 0
        assert resp_data['list'][0]['url'] == ''
        assert resp_data['list'][0]['jumpType'] == ''
        assert resp_data['list'][0]['endTime'] == self.end_time
        assert resp_data['list'][0]['sort'] == ''
        # trade端验证-已登录
        trade_get_notice_api = GetNoticeListApi()
        trade_get_notice_api.get()
        assert trade_get_notice_api.get_status_code() == 200
        assert trade_get_notice_api.get_resp_code() == 0
        assert trade_get_notice_api.get_resp_message() == 'OK'
        trade_notice_data = trade_get_notice_api.get_resp_data()
        assert len(trade_notice_data) == 0
        # 修改通知状态为开启
        edit_notice_api = EditNoticeApi()
        edit_notice_api.post({"id":notice_id,"state":1,"content":"测试修改状态为开启"})
        assert edit_notice_api.get_status_code() == 200
        assert edit_notice_api.get_resp_code() == 0
        assert edit_notice_api.get_resp_message() == 'OK'
        # 查询状态为全部
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': None})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '测试修改状态为开启'
        assert resp_data['list'][0]['startTime'] == self.start_time
        assert resp_data['list'][0]['state'] == 1
        assert resp_data['list'][0]['url'] == ''
        assert resp_data['list'][0]['jumpType'] == ''
        assert resp_data['list'][0]['endTime'] == self.end_time
        assert resp_data['list'][0]['sort'] == ''
        # trade端验证-已登录
        trade_get_notice_api = GetNoticeListApi()
        trade_get_notice_api.get()
        assert trade_get_notice_api.get_status_code() == 200
        assert trade_get_notice_api.get_resp_code() == 0
        assert trade_get_notice_api.get_resp_message() == 'OK'
        trade_notice_data = trade_get_notice_api.get_resp_data()
        assert len(trade_notice_data) == 1
        assert trade_notice_data[0]['content'] == '测试修改状态为开启'
        assert trade_notice_data[0]['jumpType'] == None
        assert trade_notice_data[0]['url'] == None


    def delete_notice(self):
        """
        测试删除通知
        :return:
        """
        # 添加通知状态为开启
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":"通知状态开启","url":"http://www.baidu.com","state":1,"jumpType":1})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # 添加通知状态为关闭
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":self.start_time,"endTime":self.end_time,"content":"通知状态关闭","url":"http://www.baidu.com","state":0,"jumpType":1})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        time.sleep(1)
        # 查询通知
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': None})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert resp_data['list'][0]['content'] == '通知状态关闭'
        assert resp_data['list'][1]['content'] == '通知状态开启'
        open_notice_id = resp_data['list'][1]['id']
        close_notice_id = resp_data['list'][0]['id']
        # 删除通知状态为开启
        delete_notice_api = DeleteNoticeApi()
        delete_notice_api.post({"id":open_notice_id,"state":1})
        assert delete_notice_api.get_status_code() == 200
        assert delete_notice_api.get_resp_code() == 0
        assert delete_notice_api.get_resp_message() == 'OK'
        # 删除通知状态为关闭
        delete_notice_api = DeleteNoticeApi()
        delete_notice_api.post({"id":close_notice_id,"state":0})
        assert delete_notice_api.get_status_code() == 200
        assert delete_notice_api.get_resp_code() == 0
        assert delete_notice_api.get_resp_message() == 'OK'
        # 查询通知
        get_notice_list_api = GetNoticeApi()
        get_notice_list_api.get({'state': 1})
        assert get_notice_list_api.get_status_code() == 200
        assert get_notice_list_api.get_resp_code() == 0
        assert get_notice_list_api.get_resp_message() == 'OK'
        resp_data = get_notice_list_api.get_resp_data()
        assert len(resp_data['list']) == 0

    def trade_query_notice_overdue(self):
        """
        测试trade端不显示已过期的通知
        :return:
        """
        start_time = (self.now_time+datetime.timedelta(hours=-2)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (self.now_time+datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        # 添加通知状态为开启
        add_notice_api = AddNoticeApi()
        add_notice_api.post({"startTime":start_time,"endTime":end_time,"content":"通知过期","url":"http://www.baidu.com","state":1,"jumpType":1})
        assert add_notice_api.get_status_code() == 200
        assert add_notice_api.get_resp_code() == 0
        assert add_notice_api.get_resp_message() == 'OK'
        # trade端验证-已登录
        trade_get_notice_api = GetNoticeListApi()
        trade_get_notice_api.get()
        assert trade_get_notice_api.get_status_code() == 200
        assert trade_get_notice_api.get_resp_code() == 0
        assert trade_get_notice_api.get_resp_message() == 'OK'
        trade_notice_data = trade_get_notice_api.get_resp_data()
        assert len(trade_notice_data) == 0

    def tearDown(self):
        super(NoticeManagerMonitoring,self).tearDown()
        hooks.clean_notice()



if __name__ == '__main__':
    api = NoticeManagerMonitoring()
    api.run_method(monitoring_name='通知管理监控',monitoring_class=api,redis_key=NOTICE_MANAGER_MONITORING_KEY)