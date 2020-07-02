# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class AddRulesConfigApi(SheetLoginBaseApi):
    """
    添加活动细则接口
    """
    url = '/netCarAdminAuth/activityRulesController/addRulesConfig'

    def build_custom_param(self, data):
        return {"activityContent":data['activityContent'],"begTime":data['begTime'],"endTime":data['endTime'],"startTime":data['startTime'],"activityTitle":data['activityTitle']}


class RefreshRuleCacheApi(SheetLoginBaseApi):
    """
    刷新活动细则缓存接口
    """
    url = '/netCarAdminAuth/activityRulesController/refreshRuleCache'


class GetRulesListApi(SheetLoginBaseApi):
    """
    获取活动细则列表接口
    """
    url = '/netCarAdminAuth/activityRulesController/getRulesConfigList'


class EditRulesConfigApi(SheetLoginBaseApi):
    """
    修改活动细则接口
    """
    url = '/netCarAdminAuth/activityRulesController/editRulesConfig'

    def build_custom_param(self, data):
        return {"startTime":data['startTime'],"begTime":data['begTime'],"endTime":data['endTime'],"activityContent":data['activityContent'],"activityTitle":data['activityTitle'],"id":data['id']}


class DelRulesConfigApi(SheetLoginBaseApi):
    """
    删除活动细则接口
    """
    url = '/netCarAdminAuth/activityRulesController/delRulesConfig'

    def build_custom_param(self, data):
        return {"id":data['id']}
