# -*- coding:utf-8 -*-
from locust import HttpLocust, TaskSet, task
import json,random,time

def on_report_to_master(client_id, data):
    data['mars'] = 'loo'
    print("Slave: Client %s, data " % client_id, data)

def on_slave_report(client_id, data):
    print("Master Recive: Client %s, data " % client_id, data)

class WebTasks(TaskSet):


    @task(5)  # 通过@task()装饰的方法为一个事务，方法的参数用于指定该行为的执行权重，参数越大每次被虚拟用户执行的概率越高，默认为1
    def near_car_api(self):
        """
        查询附近车辆接口请求
        :return:
        """
        request_url = '/platformApi/basic/nearbyDrivers'
        request_headers = {'Content-Type': 'application/json'}
        # 创建临时文件，记录网络状态码与接口响应结果
        result_file = open('./locust_near_car_result.txt','a+',encoding='utf-8')
        coordinates = [] # 坐标点列表
        # 北京市西单大悦城
        coordinates.append({'lng':'116.379488','lat':'39.916902'})
        # 南京市夫子庙
        coordinates.append({'lng':'118.795758','lat':'32.027757'})
        # 上海市外滩
        coordinates.append({'lng':'121.511969','lat':'31.25539'})
        # 成都市成都火车站
        coordinates.append({'lng':'104.079853','lat':'30.703259'})
        # 青岛五四广场
        coordinates.append({'lng':'120.386944','lat':'36.069199'})
        # 深圳市远望科技城
        coordinates.append({'lng':'114.116389','lat':'22.563179'})
        # 杭州市杭州东站
        coordinates.append({'lng':'120.219396','lat':'30.297149'})
        # 广州市东山湖公园
        coordinates.append({'lng':'113.298465','lat':'23.122361'})
        # 南宁市广西大学
        coordinates.append({'lng':'108.29703','lat':'22.850984'})
        # 哈尔滨市世纪广场
        coordinates.append({'lng':'126.690798','lat':'45.757155'})
        # 生成随机索引获取地址坐标点
        random_index = random.randint(0,len(coordinates) - 1)
        print(random_index)
        random_coordinate = coordinates[random_index]
        print(random_coordinate)
        # 组装请求参数
        request_data = {}
        request_data.update(random_coordinate)
        request_data.update({'radius':10000})
        print(request_data)
        print('Test Url:{0}'.format(request_url))
        print('Request Data:{0}'.format(request_data))
        print('Request Headers:{0}'.format(request_headers))
        request_time = time.time()
        with self.client.post(request_url,json=request_data,headers=request_headers,timeout=10,catch_response=True) as response:
            print('Resopnse Text:{0}'.format(response.text))
            result_file.write(str({'status_code':response.status_code,'response':response.text,'request_time':request_time}))
            result_file.close()
            if response.status_code == 200:  # 对http响应码是否200进行判断
                response.success()
            else:
                response.failure("Abnormal network status!")

            if json.loads(response.text)['code'] == 200:
                response.success()
            else:
                response.failure("Interface response exception!")


    @task(4)
    def distance_price_api(self):
        """
        实时单查询预估价格接口
        :return:
        """
        request_url = '/platformApi/basic/cityVehicle'
        request_headers = {'content-type': 'application/json'}
        # 创建临时文件，记录网络状态码与接口响应结果
        result_file = open('./locust_distance_price_result.txt', 'a+', encoding='utf-8')
        request_data = 'eWVtSUU4d2loVkMr4Ap0Z/1zM4eZmoc8Iw02MbKRRwvkPHKqyKdhs2jrLbEFCTmVVG5fKGuW5HgJCTB8mHztgUvvzaeIFNhmUeSQWOs4caVdBEy6zNis2J4ZA6mjp30y30j+mWl2BQK/jaWLzX5ameBfRySaqnyst3lTVqyj6gyo867cLMZ4D7XOoTflS3Aa52KDA7/oF9nXmTwW1m2q5HNnKhxYy+AADpBsDzhjvgJndyxzTeIQ+ViD6TVYjenkJCvnsbZHMi66iw643oNdWGj8aIdjdCEDxuTQT8dpGxEzIusyCndrjRlczcmGfaxbTLoTsgsuRbBenQHafFD5BBTP+dHteyC0ctO8IUkeQbW80oDoNzgExQ=='
        print('Test Url:{0}'.format(request_url))
        print('Request Data:{0}'.format(request_data))
        print('Request Headers:{0}'.format(request_headers))
        request_time = time.time()
        with self.client.post(request_url, data=request_data, headers=request_headers,timeout=20,catch_response=True) as response:
            print('Resopnse Text:{0}'.format(response.text))
            result_file.write(str({'status_code':response.status_code,'response':response.text,'request_time':request_time}))
            result_file.close()
            if response.status_code == 200:  # 对http响应码是否200进行判断
                response.success()
            else:
                response.failure("Abnormal network status!")

            if json.loads(response.text)['code'] == 200:
                response.success()
            else:
                response.failure("Interface response exception!")

class WebsiteUser(HttpLocust):
    host = "http://pipe.ywsk.cn:80"  # 被测系统的host，在终端中启动locust时没有指定--host参数时才会用到
    task_set = WebTasks  # TaskSet类，该类定义用户任务信息，必填。这里就是:WebsiteTasks类名,因为该类继承TaskSet；
    min_wait = 500  # 每个用户执行两个任务间隔时间的上下限（毫秒）,具体数值在上下限中随机取值，若不指定默认间隔时间固定为1秒
    max_wait = 1000

