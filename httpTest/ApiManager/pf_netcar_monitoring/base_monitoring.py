# -*- coding:utf-8 -*-
from ApiManager.utils.base_logger import BaseLogger
from ApiManager.utils.redis_helper import *
import time,json,traceback,sys,platform,psutil,os,socket
from ApiManager.utils.mysql_helper import mysql_execute


logger = BaseLogger(__name__).get_logger()


class BaseMonitoring(object):
    """
    监控类基类
    """


    def methods(self):
        """
        获取类中所有方法名称，返回list
        :return:
        """
        all_methods = list(filter(lambda m: not m.startswith("__") and not m.endswith("__") and callable(getattr(self, m)), dir(self)))
        # 移除基类中基础方法
        for i in ['methods','run_method','get_system_usage_info','drop_system_cache','setUp','tearDown','get_host_ip','record_result']:
            all_methods.remove(i)
        logger.info('all methods:{0}'.format(all_methods))
        return all_methods


    def record_result(self,result_dict):
        """
        执行结果记录
        :param result_json:
        :return:
        """
        monitoring_name = result_dict['monitoring_name']
        result_list = result_dict['result']
        redis_key = result_dict['redis_key']
        run_result_flag = 0
        error_msg = {}
        for x in result_list:
            if x['result'] == False:
                error_msg.update({'method':x['method'],'message':x['message']})
                run_result_flag = 1
        mysql_execute('insert into test_http.pf_monitoring (monitoring_name,result,message,redis_key) values (%s,%s,%s,%s)',params=(monitoring_name,run_result_flag,json.dumps(error_msg),redis_key),platform=True)


    def run_method(self,monitoring_class,redis_key,monitoring_name=None,time_diff=1800):
        """
        执行监控类中所有方法，将执行结果存在redis中
        :return:
        """
        result_list = []
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        logger.info('Monitoring Start!')
        logger.info('Name:{0}'.format(monitoring_name))
        logger.info('Now Time:{0}'.format(now_time))
        redis_value = {'monitoring_name':monitoring_name,'redis_key':redis_key,'result':result_list,'run_time':now_time,'time_diff':int(int(time_diff) / 60)}
        start_time = int(time.time())
        for x in self.methods():
            error_msg = None
            if x[0] == '_': # 过滤掉私有方法
                logger.info('Private methods do not execute!')
                logger.info(x)
                continue
            logger.info('---' * 30)
            logger.info('running: {0}'.format(x))
            # 执行监控类中方法
            monitoring_class.__getattribute__('setUp')()
            try:
                monitoring_class.__getattribute__(x)()
                result = True
            except Exception:
                logger.info('method {0} run failed!'.format(x))
                traceback.print_exc()
                exc_type, exc_value, exc_traceback = sys.exc_info()
                # 将异常信息转为字符串
                error_msg = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
                result = False
            monitoring_class.__getattribute__('tearDown')()
            if error_msg:
                error_msg = error_msg + ' || ' + str(time.strftime('%Y-%m-%d %H:%M:%S'))
            result_list.append({'method': x, 'result': result, 'message': error_msg})
            logger.info('***' * 30)
        logger.info(redis_value)
        end_time = int(time.time())
        running_time = end_time - start_time
        redis_value.update({'running_time':running_time})
        if redis_key:
            redis_execute().set(name=redis_key,value=json.dumps(redis_value))
        # 将执行结果写入数据库
        self.record_result(redis_value)
        logger.info('Write to database successfully！')
        # 执行完成后，将该任务在待执行队列中删除
        suite_detail = json.loads(redis_execute().get(TEST_SUITE_KEY))
        logger.info(suite_detail)
        suite_list = suite_detail['down_job_list']
        monitoring_name_list = []
        for suite in suite_list:
            monitoring_name_list.append(suite['monitoring_name'])
        # 获取该任务在待执行队列中的索引位置
        monitoring_index = monitoring_name_list.index(redis_key)
        logger.info('monitoring index:{0}'.format(monitoring_index))
        # 待执行列表中删除该任务
        suite_detail['down_job_list'].pop(monitoring_index)
        redis_execute().set(name=TEST_SUITE_KEY,value=json.dumps(suite_detail))
        logger.info('Update queue successful')
        logger.info(suite_detail)


    def get_system_usage_info(self):
        """
        获取系统使用情况
        :return:
        """
        # 获取系统内存使用情况
        virtual_memory = psutil.virtual_memory()
        used_memory = virtual_memory.used / 1024 / 1024 / 1024
        free_memory = virtual_memory.free / 1024 / 1024 / 1024
        memory_percent = virtual_memory.percent
        memory_info = "usage:%0.2fG , percent:%0.1f , free:%0.2fG" % (used_memory, memory_percent, free_memory)
        logger.info('Memory Info:')
        logger.info(memory_info)

        # 获取系统CPU使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_info = "percent:%i%%" % cpu_percent
        logger.info('CPU Info:')
        logger.info(cpu_info)
        return {'memory_info':{'usage':used_memory,'percent':memory_percent,'free':free_memory},'cpu_info':{'percent':cpu_percent}}

    def drop_system_cache(self):
        """
        释放系统内存
        :return:
        """
        system_type = platform.system()
        if system_type == 'Linux':
            command = 'echo 1 > /proc/sys/vm/drop_caches'
            os.popen(command)

    # def round_robin(self,monitoring_name,monitoring_class,redis_key):
    #     """
    #     轮循执行类中方法
    #     :param time_diff: 两次执行之间时间差，单位：秒
    #     :return:
    #     """
    #     while True:
    #         self.run_method(monitoring_class,redis_key,monitoring_name)
    #         # 查询执行完成后系统资源使用情况
    #         system_detail = self.get_system_usage_info()
    #         # 当系统内存使用大于90%时，执行释放内存操作
    #         if int(system_detail['memory_info']['percent']) > 70:
    #             self.drop_system_cache()
    #         time_diff = json.loads(redis_execute().get(redis_key))['time_diff']
    #         time.sleep(time_diff)

    def setUp(self):
        """
        前置函数
        :return:
        """
        logger.info('exec SetUp!')
        pass

    def tearDown(self):
        """
        后置函数
        :return:
        """
        logger.info('exec Teardown!')
        pass

    def get_host_ip(self):
        """
        获取本机IP地址
        :return:
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip