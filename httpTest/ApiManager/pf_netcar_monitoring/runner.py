# -*- coding:utf-8 -*-
from ApiManager.utils.base_logger import BaseLogger
from ApiManager.utils.redis_helper import *
import time,json,traceback,sys,platform,psutil,os,socket
from ApiManager.utils.mysql_helper import mysql_execute
from ApiManager.utils.redis_helper import *
from HttpRunnerManager import settings
import heapq


logger = BaseLogger(__name__).get_logger()


class Runner(object):
    """
    执行器类
    """

    def run_suite(self):
        """
        执行测试套件
        :return:
        """
        while True:
            suite_detail = None
            redis_suit_detail = redis_execute().get(TEST_SUITE_KEY)
            if redis_suit_detail:
                suite_detail = json.loads(redis_suit_detail)
            if suite_detail:
                down_job_list = suite_detail['down_job_list']
                if down_job_list:
                    # 判断当前是否有正在执行的任务
                    if '运行中' in str(down_job_list):
                        logger.info('There are currently tasks executing on the queue!')
                        logger.info(down_job_list)
                        time.sleep(15)
                    else:
                        # 获取待执行任务队列中添加时间
                        join_time_list = []
                        for job in down_job_list:
                            join_time_list.append(job['join_time'])
                        logger.info('List of current queue times to execute:{0}'.format(join_time_list))
                        # 获取最早添加到队列的任务索引
                        min_num_index_join_time_list = map(join_time_list.index, heapq.nsmallest(1, join_time_list))
                        min_num_index = list(min_num_index_join_time_list)[0]
                        logger.info('Min number index is:{0}'.format(min_num_index))
                        # 将该任务状态修改为运行中
                        suite_detail['down_job_list'][min_num_index]['status_desc'] = '运行中'
                        redis_execute().set(name=TEST_SUITE_KEY,value=json.dumps(suite_detail))
                        logger.info('Update redis down job list success!')
                        # 根据时间获取的索引获取任务详情
                        next_job_detail = suite_detail['down_job_list'][min_num_index]
                        next_job_name = next_job_detail['monitoring_name']
                        # 执行任务
                        logger.info('Start Spdb {0}!'.format(next_job_name))
                        command = "cd {0} && export PYTHONPATH=. && nohup {1} {2}&".format(settings.BASE_DIR,settings.SERVER_PYTHON_PATH,os.path.join(settings.BASE_DIR,'ApiManager/pf_netcar_monitoring/{0}.py'.format(next_job_name)))
                        logger.info('Execute system commands: {0}'.format(command))
                        os.system(command)
                        time.sleep(0.3)
                else:
                    logger.info('There are no pending tasks in the current queue!')
                    logger.info('Sleep 10 seconds!')
                    time.sleep(10)
            else:
                logger.info('test suite no key!')
                break
        logger.info('end！')


if __name__ == '__main__':
    Runner().run_suite()