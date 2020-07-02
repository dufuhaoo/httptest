# -*- coding:utf-8 -*-
from ApiManager.pf_netcar_api.login_base_api import SheetLoginBaseApi


class AddActivityDisplayApi(SheetLoginBaseApi):
    """
    添加活动展示接口
    """
    url = '/netCarAdminAuth/activityDisplayManage/addActivityDisplay'

    def build_custom_param(self, params):
        return {"orderPrice":params['orderPrice'],"reducePrice":params['reducePrice'],"limitCount":params['limitCount'],"state":params['state']}


class RefreshActivityDisplayCacheApi(SheetLoginBaseApi):
    """
    刷新缓存接口
    """
    url = '/netCarAdminAuth/activityDisplayManage/refreshActivityDisplayCache'


class GetActivityDisplayApi(SheetLoginBaseApi):
    """
    获取活动展示列表
    """
    url = '/netCarAdminAuth/activityDisplayManage/getActivityDisplay'

    def build_custom_param(self, params):
        # state   1开启   0关闭   None全部
        return {'state':params['state']}


class EditActivityDisplayApi(SheetLoginBaseApi):
    """
    修改活动展示
    """
    url = '/netCarAdminAuth/activityDisplayManage/editActivityDisplay'

    def build_custom_param(self, params):
        return {"orderPrice":params['orderPrice'],"reducePrice":params['reducePrice'],"limitCount":params['limitCount'],"state":params['state'],'id':params['id']}