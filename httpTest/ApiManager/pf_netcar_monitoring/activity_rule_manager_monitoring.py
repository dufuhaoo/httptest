# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.pf_netcar_api.sheet.acticity_rule_api import AddRulesConfigApi,DelRulesConfigApi,EditRulesConfigApi,GetRulesListApi,RefreshRuleCacheApi
from ApiManager.pf_netcar_api.trade.get_activity_rules_list_api import GetActivityRulesListApi,GetActivityRulesListNotLoginApi
from ApiManager.pf_netcar_api.trade.get_activity_rule_detail_api import GetActivityRulesDetailApi,GetActivityRulesDetailNoLoginApi
from ApiManager.utils import hooks
from ApiManager.utils.redis_helper import ACTIVITY_RULE_MANAGER_MONITORING_KEY
import datetime




class NoticeManagerMonitoring(BaseMonitoring):
    """
    通知管理监控
    """

    def setUp(self):
        super(NoticeManagerMonitoring,self).setUp()
        hooks.clean_activity_rule()
        self.now_time = datetime.datetime.now()
        self.start_time = (self.now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
        self.end_time = (self.now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        self.start_time_format = (self.now_time + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M")
        self.end_time_format = (self.now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M")

    def add_activity_rule_title(self):
        """
        测试添加活动细则接口title边界值
        :return:
        """
        # 测试添加活动细则标题12个字
        add_rule_config_api = AddRulesConfigApi()
        add_rule_config_api.post({"activityContent":"<p>1111111111</p>","begTime":self.start_time,"endTime":self.end_time,"startTime":self.start_time,"activityTitle":"一二三四五六七八九十已二"})
        assert add_rule_config_api.get_status_code() == 200
        assert add_rule_config_api.get_resp_code() == 100128
        assert add_rule_config_api.get_resp_message() == '更新成功 请刷新缓存按钮'
        # 测试添加活动细则标题13个字
        add_rule_config_api = AddRulesConfigApi()
        add_rule_config_api.post({"activityContent":"<p>1111111111</p>","begTime":self.start_time,"endTime":self.end_time,"startTime":self.start_time,"activityTitle":"一二三四五六七八九十已二三"})
        assert add_rule_config_api.get_status_code() == 200
        assert add_rule_config_api.get_resp_code() == 100101
        assert add_rule_config_api.get_resp_message() == '请检查输入项'

    def activity_rule_list_sort(self):
        """
        测试活动细则展示顺序
        :return:
        """
        # 添加两个活动细则
        add_rule_config_api = AddRulesConfigApi()
        add_rule_config_api.post({"activityContent":"<p>1111111111</p>","begTime":self.start_time,"endTime":self.end_time,"startTime":self.start_time,"activityTitle":"测试细则展示顺序01"})
        assert add_rule_config_api.get_status_code() == 200
        assert add_rule_config_api.get_resp_code() == 100128
        assert add_rule_config_api.get_resp_message() == '更新成功 请刷新缓存按钮'
        add_rule_config_api = AddRulesConfigApi()
        add_rule_config_api.post({"activityContent":"<p>2222222222</p>","begTime":self.start_time,"endTime":self.end_time,"startTime":self.start_time,"activityTitle":"测试细则展示顺序02"})
        assert add_rule_config_api.get_status_code() == 200
        assert add_rule_config_api.get_resp_code() == 100128
        assert add_rule_config_api.get_resp_message() == '更新成功 请刷新缓存按钮'
        # 刷新缓存
        refresh_rule_api = RefreshRuleCacheApi()
        refresh_rule_api.get()
        assert refresh_rule_api.get_status_code() == 200
        assert refresh_rule_api.get_resp_code() == 0
        assert refresh_rule_api.get_resp_message() == 'OK'
        # 获取活动细则管理列表
        get_rule_list_api = GetRulesListApi()
        get_rule_list_api.get()
        assert get_rule_list_api.get_status_code() ==  200
        assert get_rule_list_api.get_resp_code() ==  0
        assert get_rule_list_api.get_resp_message() ==  'OK'
        rule_list_data = get_rule_list_api.get_resp_data()
        assert len(rule_list_data['list']) == 2
        assert rule_list_data['list'][0]['activityTitle'] == '测试细则展示顺序02'
        assert rule_list_data['list'][0]['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        assert rule_list_data['list'][0]['activityContent'] == '<p>2222222222</p>'
        assert rule_list_data['list'][0]['startTime'] == self.start_time
        assert rule_list_data['list'][0]['sort'] == 2
        assert rule_list_data['list'][1]['activityTitle'] == '测试细则展示顺序01'
        assert rule_list_data['list'][1]['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        assert rule_list_data['list'][1]['activityContent'] == '<p>1111111111</p>'
        assert rule_list_data['list'][1]['startTime'] == self.start_time
        assert rule_list_data['list'][1]['sort'] == 1
        # 校验trade段展示顺序-已登录
        trade_get_rule_list_api = GetActivityRulesListApi()
        trade_get_rule_list_api.get()
        assert trade_get_rule_list_api.get_status_code() == 200
        assert trade_get_rule_list_api.get_resp_code() == 0
        assert trade_get_rule_list_api.get_resp_message() == 'OK'
        rule_list_data = trade_get_rule_list_api.get_resp_data()
        assert len(rule_list_data) == 2
        assert rule_list_data[0]['activityTitle'] == '测试细则展示顺序02'
        assert rule_list_data[0]['activityContent'] == None
        assert rule_list_data[0]['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        assert rule_list_data[1]['activityTitle'] == '测试细则展示顺序01'
        assert rule_list_data[1]['activityContent'] == None
        assert rule_list_data[1]['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        activity_rule_id = rule_list_data[0]['ruleId']
        # 校验trade段详情-已登录
        trade_get_rule_detail_api = GetActivityRulesDetailApi()
        trade_get_rule_detail_api.get({'id':activity_rule_id})
        assert trade_get_rule_detail_api.get_status_code() ==  200
        assert trade_get_rule_detail_api.get_resp_code() ==  0
        assert trade_get_rule_detail_api.get_resp_message() ==  'OK'
        rule_detail_data = trade_get_rule_detail_api.get_resp_data()
        assert rule_detail_data['activityTitle'] == '测试细则展示顺序02'
        assert rule_detail_data['activityContent'] == '<p>2222222222</p>'
        assert rule_detail_data['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        # 校验trade段展示顺序-未登录
        trade_get_rule_list_api_no_login = GetActivityRulesListNotLoginApi()
        trade_get_rule_list_api_no_login.get()
        assert trade_get_rule_list_api_no_login.get_status_code() == 200
        assert trade_get_rule_list_api_no_login.get_resp_code() == 0
        assert trade_get_rule_list_api_no_login.get_resp_message() == 'OK'
        rule_list_data = trade_get_rule_list_api_no_login.get_resp_data()
        assert len(rule_list_data) == 2
        assert rule_list_data[0]['activityTitle'] == '测试细则展示顺序02'
        assert rule_list_data[0]['activityContent'] == None
        assert rule_list_data[0]['activityTime'] == '{0}--{1}'.format(self.start_time_format, self.end_time_format)
        assert rule_list_data[1]['activityTitle'] == '测试细则展示顺序01'
        assert rule_list_data[1]['activityContent'] == None
        assert rule_list_data[1]['activityTime'] == '{0}--{1}'.format(self.start_time_format, self.end_time_format)
        # 校验trade段详情-未登录
        trade_get_rule_detail_api = GetActivityRulesDetailNoLoginApi()
        trade_get_rule_detail_api.get({'id':activity_rule_id})
        assert trade_get_rule_detail_api.get_status_code() ==  200
        assert trade_get_rule_detail_api.get_resp_code() ==  0
        assert trade_get_rule_detail_api.get_resp_message() ==  'OK'
        rule_detail_data = trade_get_rule_detail_api.get_resp_data()
        assert rule_detail_data['activityTitle'] == '测试细则展示顺序02'
        assert rule_detail_data['activityContent'] == '<p>2222222222</p>'
        assert rule_detail_data['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)

    def edit_activity_rule(self):
        """
        测试修改活动细则
        :return:
        """
        add_rule_config_api = AddRulesConfigApi()
        add_rule_config_api.post({"activityContent":"<p>1111111111</p>","begTime":self.start_time,"endTime":self.end_time,"startTime":self.start_time,"activityTitle":"添加一个活动细则"})
        assert add_rule_config_api.get_status_code() ==200
        assert add_rule_config_api.get_resp_code() ==100128
        assert add_rule_config_api.get_resp_message() =='更新成功 请刷新缓存按钮'
        # 刷新缓存
        refresh_rule_api = RefreshRuleCacheApi()
        refresh_rule_api.get()
        assert refresh_rule_api.get_status_code() ==200
        assert refresh_rule_api.get_resp_code() ==0
        assert refresh_rule_api.get_resp_message() =='OK'
        # 获取活动细则管理列表
        get_rule_list_api = GetRulesListApi()
        get_rule_list_api.get()
        assert get_rule_list_api.get_status_code() == 200
        assert get_rule_list_api.get_resp_code() == 0
        assert get_rule_list_api.get_resp_message() == 'OK'
        rule_list_data = get_rule_list_api.get_resp_data()
        assert len(rule_list_data['list']) == 1
        assert rule_list_data['list'][0]['activityTitle'] == '添加一个活动细则'
        assert rule_list_data['list'][0]['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        assert rule_list_data['list'][0]['activityContent'] == '<p>1111111111</p>'
        assert rule_list_data['list'][0]['startTime'] == self.start_time
        assert rule_list_data['list'][0]['sort'] == 1
        rule_id = rule_list_data['list'][0]['id']
        # 修改细则内容
        start_time = (self.now_time + datetime.timedelta(hours=-5)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = (self.now_time + datetime.timedelta(hours=+2)).strftime("%Y-%m-%d %H:%M:%S")
        start_time_format = (self.now_time + datetime.timedelta(hours=-5)).strftime("%Y-%m-%d %H:%M")
        end_time_format = (self.now_time + datetime.timedelta(hours=+2)).strftime("%Y-%m-%d %H:%M")
        edit_activity_rule_api = EditRulesConfigApi()
        edit_activity_rule_api.post({"startTime":start_time,"begTime":start_time,"endTime":end_time,"activityContent":'<p>修改细则内容</p>',"activityTitle":'测试修改细则',"id":rule_id})
        assert edit_activity_rule_api.get_status_code() == 200
        assert edit_activity_rule_api.get_resp_code() == 100128
        assert edit_activity_rule_api.get_resp_message() == '更新成功 请刷新缓存按钮'
        # 刷新缓存
        refresh_rule_api = RefreshRuleCacheApi()
        refresh_rule_api.get()
        assert refresh_rule_api.get_status_code() == 200
        assert refresh_rule_api.get_resp_code() == 0
        assert refresh_rule_api.get_resp_message() == 'OK'
        # 获取活动细则管理列表
        get_rule_list_api = GetRulesListApi()
        get_rule_list_api.get()
        assert get_rule_list_api.get_status_code() ==  200
        assert get_rule_list_api.get_resp_code() ==  0
        assert get_rule_list_api.get_resp_message() ==  'OK'
        rule_list_data = get_rule_list_api.get_resp_data()
        assert len(rule_list_data['list']) == 1
        assert rule_list_data['list'][0]['activityTitle'] == '测试修改细则'
        assert rule_list_data['list'][0]['activityTime'] == '{0}--{1}'.format(start_time_format,end_time_format)
        assert rule_list_data['list'][0]['activityContent'] == '<p>修改细则内容</p>'
        assert rule_list_data['list'][0]['startTime'] == start_time
        assert rule_list_data['list'][0]['sort'] == 1
        # 校验trade端列表展示
        trade_get_rule_list_api = GetActivityRulesListApi()
        trade_get_rule_list_api.get()
        assert trade_get_rule_list_api.get_status_code() == 200
        assert trade_get_rule_list_api.get_resp_code() == 0
        assert trade_get_rule_list_api.get_resp_message() == 'OK'
        rule_list_data = trade_get_rule_list_api.get_resp_data()
        assert len(rule_list_data) == 1
        assert rule_list_data[0]['activityTitle'] == '测试修改细则'
        assert rule_list_data[0]['activityContent'] == None
        assert rule_list_data[0]['activityTime'] == '{0}--{1}'.format(start_time_format,end_time_format)
        activity_rule_id = rule_list_data[0]['ruleId']
        # 校验trade端详情
        trade_get_rule_detail_api = GetActivityRulesDetailApi()
        trade_get_rule_detail_api.get({'id':activity_rule_id})
        assert trade_get_rule_detail_api.get_status_code() ==  200
        assert trade_get_rule_detail_api.get_resp_code() ==  0
        assert trade_get_rule_detail_api.get_resp_message() ==  'OK'
        rule_detail_data = trade_get_rule_detail_api.get_resp_data()
        assert rule_detail_data['activityTitle'] == '测试修改细则'
        assert rule_detail_data['activityContent'] == '<p>修改细则内容</p>'
        assert rule_detail_data['activityTime'] == '{0}--{1}'.format(start_time_format,end_time_format)


    def add_activity_not_to_time(self):
        """
        测试活动细则未到发布时间
        :return:
        """
        add_rule_config_api = AddRulesConfigApi()
        add_rule_config_api.post({"activityContent":"<p>1111111111</p>","begTime":self.start_time,"endTime":self.end_time,"startTime":(self.now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S"),"activityTitle":"测试未到发布时间"})
        assert add_rule_config_api.get_status_code() == 200
        assert add_rule_config_api.get_resp_code() == 100128
        assert add_rule_config_api.get_resp_message() == '更新成功 请刷新缓存按钮'
        # 刷新缓存
        refresh_rule_api = RefreshRuleCacheApi()
        refresh_rule_api.get()
        assert refresh_rule_api.get_status_code() == 200
        assert refresh_rule_api.get_resp_code() == 0
        assert refresh_rule_api.get_resp_message() == 'OK'
        # 获取活动细则管理列表
        get_rule_list_api = GetRulesListApi()
        get_rule_list_api.get()
        assert get_rule_list_api.get_status_code() ==  200
        assert get_rule_list_api.get_resp_code() ==  0
        assert get_rule_list_api.get_resp_message() ==  'OK'
        rule_list_data = get_rule_list_api.get_resp_data()
        assert len(rule_list_data['list']) == 1
        assert rule_list_data['list'][0]['activityTitle'] == '测试未到发布时间'
        assert rule_list_data['list'][0]['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        assert rule_list_data['list'][0]['activityContent'] == '<p>1111111111</p>'
        assert rule_list_data['list'][0]['startTime'] == (self.now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
        assert rule_list_data['list'][0]['sort'] == 1
        # 校验trade端列表展示
        trade_get_rule_list_api = GetActivityRulesListApi()
        trade_get_rule_list_api.get()
        assert trade_get_rule_list_api.get_status_code() == 200
        assert trade_get_rule_list_api.get_resp_code() == 0
        assert trade_get_rule_list_api.get_resp_message() == 'OK'
        rule_list_data = trade_get_rule_list_api.get_resp_data()
        assert len(rule_list_data) == 0

    def delete_activity_rule(self):
        """
        测试活动细则管理删除
        :return:
        """
        add_rule_config_api = AddRulesConfigApi()
        add_rule_config_api.post({"activityContent":"<p>1111111111</p>","begTime":self.start_time,"endTime":self.end_time,"startTime":self.start_time,"activityTitle":"添加一个活动细则"})
        assert add_rule_config_api.get_status_code() == 200
        assert add_rule_config_api.get_resp_code() == 100128
        assert add_rule_config_api.get_resp_message() == '更新成功 请刷新缓存按钮'
        # 刷新缓存
        refresh_rule_api = RefreshRuleCacheApi()
        refresh_rule_api.get()
        assert refresh_rule_api.get_status_code() == 200
        assert refresh_rule_api.get_resp_code() == 0
        assert refresh_rule_api.get_resp_message() == 'OK'
        # 获取活动细则管理列表
        get_rule_list_api = GetRulesListApi()
        get_rule_list_api.get()
        assert get_rule_list_api.get_status_code() ==  200
        assert get_rule_list_api.get_resp_code() ==  0
        assert get_rule_list_api.get_resp_message() ==  'OK'
        rule_list_data = get_rule_list_api.get_resp_data()
        assert len(rule_list_data['list']) == 1
        assert rule_list_data['list'][0]['activityTitle'] == '添加一个活动细则'
        assert rule_list_data['list'][0]['activityTime'] == '{0}--{1}'.format(self.start_time_format,self.end_time_format)
        assert rule_list_data['list'][0]['activityContent'] == '<p>1111111111</p>'
        assert rule_list_data['list'][0]['startTime'] == self.start_time
        assert rule_list_data['list'][0]['sort'] == 1
        rule_id = rule_list_data['list'][0]['id']
        # 删除活动细则
        delete_activity_rule_api = DelRulesConfigApi()
        delete_activity_rule_api.post({'id':rule_id})
        assert delete_activity_rule_api.get_status_code() == 200
        assert delete_activity_rule_api.get_resp_code() == 100128
        assert delete_activity_rule_api.get_resp_message() == '更新成功 请刷新缓存按钮'
        # 刷新缓存
        refresh_rule_api = RefreshRuleCacheApi()
        refresh_rule_api.get()
        assert refresh_rule_api.get_status_code() == 200
        assert refresh_rule_api.get_resp_code() == 0
        assert refresh_rule_api.get_resp_message() == 'OK'
        # 获取活动细则管理列表
        get_rule_list_api = GetRulesListApi()
        get_rule_list_api.get()
        assert get_rule_list_api.get_status_code() ==  200
        assert get_rule_list_api.get_resp_code() ==  0
        assert get_rule_list_api.get_resp_message() ==  'OK'
        rule_list_data = get_rule_list_api.get_resp_data()
        assert len(rule_list_data['list']) == 0
        # 校验trade端列表展示
        trade_get_rule_list_api = GetActivityRulesListApi()
        trade_get_rule_list_api.get()
        assert trade_get_rule_list_api.get_status_code() == 200
        assert trade_get_rule_list_api.get_resp_code() == 0
        assert trade_get_rule_list_api.get_resp_message() == 'OK'
        rule_list_data = trade_get_rule_list_api.get_resp_data()
        assert len(rule_list_data) == 0

    def tearDown(self):
        super(NoticeManagerMonitoring,self).tearDown()
        hooks.clean_activity_rule()



if __name__ == '__main__':
    api = NoticeManagerMonitoring()
    api.run_method(monitoring_name='活动细则管理监控',monitoring_class=api,redis_key=ACTIVITY_RULE_MANAGER_MONITORING_KEY)