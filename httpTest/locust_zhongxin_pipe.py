# -*- coding:utf-8 -*-
from locust import HttpLocust, TaskSet, task
import json,random,time

def on_report_to_master(client_id, data):
    data['mars'] = 'loo'
    print("Slave: Client %s, data " % client_id, data)

def on_slave_report(client_id, data):
    print("Master Recive: Client %s, data " % client_id, data)

class WebTasks(TaskSet):

    @task(3)
    def get_order_car_details(self):
        """
        登录操作封装
        :return:
        """
        url = '/auth/login'
        request_data = {'username':'8lu4XRkZoVfn658E39KtNg==','password':'eNwcIeeCEGJMY32S0pL//g=='}
        with self.client.get(url,params=request_data,timeout=20,catch_response=True,verify='/Users/gaoyinglong/test2.cer') as response:
            print('Pipe Login Response Text: {0}'.format(response.text))


class WebsiteUser(HttpLocust):
    host = "https://citictest.ywsk.cn"  # 被测系统的host，在终端中启动locust时没有指定--host参数时才会用到
    task_set = WebTasks  # TaskSet类，该类定义用户任务信息，必填。这里就是:WebsiteTasks类名,因为该类继承TaskSet；
    min_wait = 500  # 每个用户执行两个任务间隔时间的上下限（毫秒）,具体数值在上下限中随机取值，若不指定默认间隔时间固定为1秒
    max_wait = 1000
