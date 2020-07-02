import datetime
import logging
import os, random
import requests
import json, time, hashlib
from HttpRunnerManager import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError
from ApiManager import separator
from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo, EnvInfo, TestReports, DebugTalk, \
    TestSuite
from ApiManager.utils.mysql_helper import mysql_execute
from ApiManager.utils.redis_helper import *

logger = logging.getLogger('HttpRunnerManager')


def string_to_md5(string):
    """
    创建md5加密字符串
    :param string:
    :return:
    """
    m = hashlib.md5()
    m.update(string.encode(encoding='UTF-8'))
    return m.hexdigest()


def add_register_data(**kwargs):
    """
    用户注册信息逻辑判断及落地
    :param kwargs: dict
    :return: ok or tips
    """
    user_info = UserInfo.objects
    try:
        username = kwargs.pop('account')
        password = kwargs.pop('password')
        email = kwargs.pop('email')

        if user_info.filter(username__exact=username).filter(status=1).count() > 0:
            logger.debug('{username} 已被其他用户注册'.format(username=username))
            return '该用户名已被注册，请更换用户名'
        if user_info.filter(email__exact=email).filter(status=1).count() > 0:
            logger.debug('{email} 昵称已被其他用户注册'.format(email=email))
            return '邮箱已被其他用户注册，请更换邮箱'
        user_info.create(username=username, password=password, email=email)
        logger.info('新增用户：{user_info}'.format(user_info=user_info))
        return 'ok'
    except DataError:
        logger.error('信息输入有误：{user_info}'.format(user_info=user_info))
        return '字段长度超长，请重新编辑'


def add_project_data(type, **kwargs):
    """
    项目信息落地 新建时必须默认添加debugtalk.py
    :param type: true: 新增， false: 更新
    :param kwargs: dict
    :return: ok or tips
    """
    project_opt = ProjectInfo.objects
    project_name = kwargs.get('project_name')
    if type:
        if project_opt.get_pro_name(project_name) < 1:
            try:
                project_opt.insert_project(**kwargs)
                belong_project = project_opt.get(project_name=project_name)
                DebugTalk.objects.create(belong_project=belong_project, debugtalk='# debugtalk.py')
            except DataError:
                return '项目信息过长'
            except Exception:
                logging.error('项目添加异常：{kwargs}'.format(kwargs=kwargs))
                return '添加失败，请重试'
            logger.info('项目添加成功：{kwargs}'.format(kwargs=kwargs))
        else:
            return '该项目已存在，请重新编辑'
    else:
        if project_name != project_opt.get_pro_name('', type=False, id=kwargs.get(
                'index')) and project_opt.get_pro_name(project_name) > 0:
            return '该项目已存在， 请重新命名'
        try:
            project_opt.update_project(kwargs.pop('index'), **kwargs)  # testcaseinfo的belong_project也得更新，这个字段设计的有点坑了
        except DataError:
            return '项目信息过长'
        except Exception:
            logging.error('更新失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'
        logger.info('项目更新成功：{kwargs}'.format(kwargs=kwargs))

    return 'ok'


'''模块数据落地'''


def add_module_data(type, **kwargs):
    """
    模块信息落地
    :param type: boolean: true: 新增， false: 更新
    :param kwargs: dict
    :return: ok or tips
    """
    module_opt = ModuleInfo.objects
    belong_project = kwargs.pop('belong_project')
    module_name = kwargs.get('module_name')
    if type:
        if module_opt.filter(belong_project__project_name__exact=belong_project) \
                .filter(module_name__exact=module_name).count() < 1:
            try:
                belong_project = ProjectInfo.objects.get_pro_name(belong_project, type=False)
            except ObjectDoesNotExist:
                logging.error('项目信息读取失败：{belong_project}'.format(belong_project=belong_project))
                return '项目信息读取失败，请重试'
            kwargs['belong_project'] = belong_project
            try:
                module_opt.insert_module(**kwargs)
            except DataError:
                return '模块信息过长'
            except Exception:
                logging.error('模块添加异常：{kwargs}'.format(kwargs=kwargs))
                return '添加失败，请重试'
            logger.info('模块添加成功：{kwargs}'.format(kwargs=kwargs))
        else:
            return '该模块已在项目中存在，请重新编辑'
    else:
        if module_name != module_opt.get_module_name('', type=False, id=kwargs.get('index')) \
                and module_opt.filter(belong_project__project_name__exact=belong_project) \
                .filter(module_name__exact=module_name).count() > 0:
            return '该模块已存在，请重新命名'
        try:
            module_opt.update_module(kwargs.pop('index'), **kwargs)
        except DataError:
            return '模块信息过长'
        except Exception:
            logging.error('更新失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'
        logger.info('模块更新成功：{kwargs}'.format(kwargs=kwargs))
    return 'ok'


'''用例数据落地'''


def add_case_data(type, **kwargs):
    """
    用例信息落地
    :param type: boolean: true: 添加新用例， false: 更新用例
    :param kwargs: dict
    :return: ok or tips
    """
    case_info = kwargs.get('test').get('case_info')
    case_opt = TestCaseInfo.objects
    name = kwargs.get('test').get('name')
    module = case_info.get('module')
    project = case_info.get('project')
    belong_module = ModuleInfo.objects.get_module_name(module, type=False)
    config = case_info.get('config', '')
    if config != '':
        case_info.get('include')[0] = eval(config)

    try:
        if type:

            if case_opt.get_case_name(name, module, project) < 1:
                case_opt.insert_case(belong_module, **kwargs)
                logger.info('{name}用例添加成功: {kwargs}'.format(name=name, kwargs=kwargs))
            else:
                return '用例或配置已存在，请重新编辑'
        else:
            index = case_info.get('test_index')
            if name != case_opt.get_case_by_id(index, type=False) \
                    and case_opt.get_case_name(name, module, project) > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            case_opt.update_case(belong_module, **kwargs)
            logger.info('{name}用例更新成功: {kwargs}'.format(name=name, kwargs=kwargs))

    except DataError:
        logger.error('用例信息：{kwargs}过长！！'.format(kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'


'''配置数据落地'''


def add_config_data(type, **kwargs):
    """
    配置信息落地
    :param type: boolean: true: 添加新配置， fasle: 更新配置
    :param kwargs: dict
    :return: ok or tips
    """
    case_opt = TestCaseInfo.objects
    config_info = kwargs.get('config').get('config_info')
    name = kwargs.get('config').get('name')
    module = config_info.get('module')
    project = config_info.get('project')
    belong_module = ModuleInfo.objects.get_module_name(module, type=False)

    try:
        if type:
            if case_opt.get_case_name(name, module, project) < 1:
                case_opt.insert_config(belong_module, **kwargs)
                logger.info('{name}配置添加成功: {kwargs}'.format(name=name, kwargs=kwargs))
            else:
                return '用例或配置已存在，请重新编辑'
        else:
            index = config_info.get('test_index')
            if name != case_opt.get_case_by_id(index, type=False) \
                    and case_opt.get_case_name(name, module, project) > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            case_opt.update_config(belong_module, **kwargs)
            logger.info('{name}配置更新成功: {kwargs}'.format(name=name, kwargs=kwargs))
    except DataError:
        logger.error('{name}配置信息过长：{kwargs}'.format(name=name, kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'


def add_suite_data(**kwargs):
    belong_project = kwargs.pop('project')
    suite_name = kwargs.get('suite_name')
    kwargs['belong_project'] = ProjectInfo.objects.get(project_name=belong_project)

    try:
        if TestSuite.objects.filter(belong_project__project_name=belong_project, suite_name=suite_name).count() > 0:
            return 'Suite已存在, 请重新命名'
        TestSuite.objects.create(**kwargs)
        logging.info('suite添加成功: {kwargs}'.format(kwargs=kwargs))
    except Exception:
        return 'suite添加异常，请重试'
    return 'ok'


def edit_suite_data(**kwargs):
    id = kwargs.pop('id')
    project_name = kwargs.pop('project')
    suite_name = kwargs.get('suite_name')
    include = kwargs.pop('include')
    belong_project = ProjectInfo.objects.get(project_name=project_name)

    suite_obj = TestSuite.objects.get(id=id)
    try:
        if suite_name != suite_obj.suite_name and \
                TestSuite.objects.filter(belong_project=belong_project, suite_name=suite_name).count() > 0:
            return 'Suite已存在, 请重新命名'
        suite_obj.suite_name = suite_name
        suite_obj.belong_project = belong_project
        suite_obj.include = include
        suite_obj.save()
        logging.info('suite更新成功: {kwargs}'.format(kwargs=kwargs))
    except Exception:
        return 'suite添加异常，请重试'
    return 'ok'


'''环境信息落地'''


def env_data_logic(**kwargs):
    """
    环境信息逻辑判断及落地
    :param kwargs: dict
    :return: ok or tips
    """
    id = kwargs.get('id', None)
    if id:
        try:
            EnvInfo.objects.delete_env(id)
        except ObjectDoesNotExist:
            return '删除异常，请重试'
        return 'ok'
    index = kwargs.pop('index')
    env_name = kwargs.get('env_name')
    if env_name is '':
        return '环境名称不可为空'
    if kwargs.get('base_url') is '':
        return '请求地址不可为空'
    elif kwargs.get('simple_desc') is '':
        return '请添加环境描述'

    if index == 'add':
        try:
            if EnvInfo.objects.filter(env_name=env_name).count() < 1:
                EnvInfo.objects.insert_env(**kwargs)
                logging.info('环境添加成功：{kwargs}'.format(kwargs=kwargs))
                return 'ok'
            else:
                return '环境名称重复'
        except DataError:
            return '环境信息过长'
        except Exception:
            logging.error('添加环境异常：{kwargs}'.format(kwargs=kwargs))
            return '环境信息添加异常，请重试'
    else:
        try:
            if EnvInfo.objects.get_env_name(index) != env_name and EnvInfo.objects.filter(
                    env_name=env_name).count() > 0:
                return '环境名称已存在'
            else:
                EnvInfo.objects.update_env(index, **kwargs)
                logging.info('环境信息更新成功：{kwargs}'.format(kwargs=kwargs))
                return 'ok'
        except DataError:
            return '环境信息过长'
        except ObjectDoesNotExist:
            logging.error('环境信息查询失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'


def del_module_data(id):
    """
    根据模块索引删除模块数据，强制删除其下所有用例及配置
    :param id: str or int:模块索引
    :return: ok or tips
    """
    try:
        module_name = ModuleInfo.objects.get_module_name('', type=False, id=id)
        TestCaseInfo.objects.filter(belong_module__module_name=module_name).delete()
        ModuleInfo.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('{module_name} 模块已删除'.format(module_name=module_name))
    return 'ok'


def del_project_data(id):
    """
    根据项目索引删除项目数据，强制删除其下所有用例、配置、模块、Suite
    :param id: str or int: 项目索引
    :return: ok or tips
    """
    try:
        project_name = ProjectInfo.objects.get_pro_name('', type=False, id=id)

        belong_modules = ModuleInfo.objects.filter(belong_project__project_name=project_name).values_list('module_name')
        for obj in belong_modules:
            TestCaseInfo.objects.filter(belong_module__module_name=obj).delete()

        TestSuite.objects.filter(belong_project__project_name=project_name).delete()

        ModuleInfo.objects.filter(belong_project__project_name=project_name).delete()

        DebugTalk.objects.filter(belong_project__project_name=project_name).delete()

        ProjectInfo.objects.get(id=id).delete()

    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('{project_name} 项目已删除'.format(project_name=project_name))
    return 'ok'


def del_test_data(id):
    """
    根据用例或配置索引删除数据
    :param id: str or int: test or config index
    :return: ok or tips
    """
    try:
        TestCaseInfo.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('用例/配置已删除')
    return 'ok'


def del_suite_data(id):
    """
    根据Suite索引删除数据
    :param id: str or int: test or config index
    :return: ok or tips
    """
    try:
        TestSuite.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('Suite已删除')
    return 'ok'


def del_report_data(id):
    """
    根据报告索引删除报告
    :param id:
    :return: ok or tips
    """
    try:
        TestReports.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    return 'ok'


def copy_test_data(id, name):
    """
    复制用例信息，默认插入到当前项目、莫夸
    :param id: str or int: 复制源
    :param name: str：新用例名称
    :return: ok or tips
    """
    try:
        test = TestCaseInfo.objects.get(id=id)
        belong_module = test.belong_module
    except ObjectDoesNotExist:
        return '复制异常，请重试'
    if TestCaseInfo.objects.filter(name=name, belong_module=belong_module).count() > 0:
        return '用例/配置名称重复了哦'
    test.id = None
    test.name = name
    request = eval(test.request)
    if 'test' in request.keys():
        request.get('test')['name'] = name
    else:
        request.get('config')['name'] = name
    test.request = request
    test.save()
    logging.info('{name}用例/配置添加成功'.format(name=name))
    return 'ok'


def copy_suite_data(id, name):
    """
    复制suite信息，默认插入到当前项目、莫夸
    :param id: str or int: 复制源
    :param name: str：新用例名称
    :return: ok or tips
    """
    try:
        suite = TestSuite.objects.get(id=id)
        belong_project = suite.belong_project
    except ObjectDoesNotExist:
        return '复制异常，请重试'
    if TestSuite.objects.filter(suite_name=name, belong_project=belong_project).count() > 0:
        return 'Suite名称重复了哦'
    suite.id = None
    suite.suite_name = name
    suite.save()
    logging.info('{name}suite添加成功'.format(name=name))
    return 'ok'


def add_test_reports(runner, report_name=None):
    """
    定时任务或者异步执行报告信息落地
    :param start_at: time: 开始时间
    :param report_name: str: 报告名称，为空默认时间戳命名
    :param kwargs: dict: 报告结果值
    :return:
    """
    time_stamp = int(runner.summary["time"]["start_at"])
    runner.summary['time']['start_datetime'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
    report_name = report_name if report_name else runner.summary['time']['start_datetime']
    runner.summary['html_report_name'] = report_name

    report_path = os.path.join(os.getcwd(),
                               "reports{}{}.html".format(separator, int(runner.summary['time']['start_at'])))
    runner.gen_html_report(
        html_report_template=os.path.join(os.getcwd(), "templates{}extent_report_template.html".format(separator)))

    with open(report_path, encoding='utf-8') as stream:
        reports = stream.read()

    test_reports = {
        'report_name': report_name,
        'status': runner.summary.get('success'),
        'successes': runner.summary.get('stat').get('successes'),
        'testsRun': runner.summary.get('stat').get('testsRun'),
        'start_at': runner.summary['time']['start_datetime'],
        'reports': reports
    }

    TestReports.objects.create(**test_reports)
    return report_path


def cc_driver_callback_data(**kwargs):
    """
    曹操司机端操作落地
    :param kwargs:
    :return:
    """
    event = kwargs.get('event')
    high_speed_fee = kwargs.get('high_speed_fee')
    bridge_fee = kwargs.get('bridge_fee')
    park_fee = kwargs.get('park_fee')
    other_fee = kwargs.get('other_fee')
    data = {'event': event, 'status': 0,
            'fee_detail': {'high_speed_fee': high_speed_fee, 'bridge_fee': bridge_fee, 'park_fee': park_fee,
                           'other_fee': other_fee}}
    logger.info(data)
    redis_execute().set(name=CAOCAO_DRIVER_COMMAND, value=json.dumps(data))
    return '更新成功'


def sz_callback_data(**kwargs):
    """
    神州订单回调落地
    """
    sz_access_token_url = 'https://sandboxoauth.10101111.com/oauth/token'  # 获取access_token请求地址
    sz_change_status_url = 'https://sandboxapi.10101111.com/v1/action/order/changeStatus'  # 订单状态变更请求地址
    request_timeout = 5  # 接口超时时间，单位:秒
    driver_id = kwargs.get('driverId')
    bank_id = int(kwargs.get('bank'))
    trade_order_id = kwargs.get('tradeOrderId')
    status = kwargs.get('callBackStatus')
    high_way_amount = float(kwargs.get('highWayAmount'))  # 高速费
    clean_amount = float(kwargs.get('cleanAmount'))  # 清洁费
    airport_service_amount = float(kwargs.get('airportServiceAmount'))  # 机场服务费
    parking_amount = float(kwargs.get('parkingAmount'))  # 停车费
    other_amount = float(kwargs.get('otherAmount'))  # 其他费用
    actual_kilo_length = float(kwargs.get('actualKiloLength'))  # 行驶公里数

    get_access_token_data = {"password": "18610000000", "client_secret": "4elvlictibhl0bu9gsiw",
                             "grant_type": "password", "client_id": "585B0F5C0000000A", "username": "18610000000"}

    logger.info('get sz access_token!')
    logger.info(sz_access_token_url)
    logger.info(get_access_token_data)

    access_token_response = requests.post(url=sz_access_token_url, data=get_access_token_data, timeout=request_timeout)
    logger.info(access_token_response.text)
    if access_token_response.status_code != 200:
        return '获取神州access_token失败，接口请求状态码: {0}'.format(access_token_response.status_code)
    access_token = json.loads(access_token_response.content)['access_token']

    car_info_detail = mysql_execute(sql='select * from netCarPlatform.tbl_platform_car_info where trade_order_id=%s and channel_type=4 limit 1',params=(trade_order_id), bank=bank_id)
    channel_order_id = car_info_detail['channel_order_id']
    if channel_order_id is None:
        return 'tbl_platform_car_info表中channel_order_id为空，请检查！'

    logger.info('channel_order_id:{0}'.format(channel_order_id))
    logger.info('access_token:{0}'.format(access_token))
    logger.info('driver_id:{0}'.format(driver_id))
    logger.info('status:{0}'.format(status))
    if channel_order_id and access_token and driver_id and status:
        request_data = {"highwayAmount": high_way_amount,
                        "orderId": channel_order_id,
                        "cleanAmount": clean_amount,
                        "otherAmount": other_amount,
                        "clng": 0.0,
                        "clat": 0.0,
                        "airportServiceAmount": airport_service_amount,
                        "access_token": access_token,
                        "parkingAmount": parking_amount,
                        "actualKiloLength": actual_kilo_length,
                        "otherAmountRemark": "other fee",
                        "driverId": driver_id,
                        "status": status}
        logger.info('get sz order change status!')
        logger.info(sz_change_status_url)
        logger.info(request_data)
        response = requests.post(url=sz_change_status_url, data=request_data, timeout=request_timeout)
        logger.info(response.content)
        if response.status_code != 200:
            return '修改神州订单状态失败，接口请求状态码: {0}'.format(response.status_code)
        response_content = json.loads(response.content)
        response_code = response_content['code']
        response_msg = response_content['msg']
        response_status = response_content['status']

        if response_code == 1 and response_msg == '成功' and response_status == 'SUCCESS':
            return '订单状态回调成功！'
        else:
            return '订单状态回调失败，原因：{0}'.format(response_content)
    else:
        return '请检查渠道单号、车型、状态、token是否传入正确'


def pay_callback_data(**kwargs):
    """
    浦发-支付回调落地
    :param kwargs:
    :return:
    """
    sit_paycb_url = 'http://192.168.0.46:7102/paycb/api/pay/callback/notify'
    trade_order_id = kwargs.get('tradeOrderId')
    pay_status = kwargs.get('Status')
    headers = {'content-type': 'application/json; charset=UTF-8'}
    order_detail = mysql_execute('select * from tbl_trade_order where id=%s', params=(trade_order_id), trade=True)
    order_status = order_detail['order_status']
    if order_status not in [22, 25]:
        return '该订单状态不是支付中！'
    order_pay_record_detail = mysql_execute('select id from tbl_trade_order_pay_record where order_id=%s',
                                            params=(trade_order_id), trade=True)
    if order_pay_record_detail is None:
        return '订单未查询到支付单！'
    pay_record_id = order_pay_record_detail['id']

    request_data = {"data": {
        "bigOrderAmt": 5000,
        "bigOrderDate": "2019-01-11",
        "bigOrderDealDateTime": "2019-01-11 T 19:20:22",
        "bigOrderNo": trade_order_id,  # 订单号
        "bigOrderReqNo": pay_record_id,  # 支付单ID
        "bigOrderStatus": pay_status,
        "innerTransNo": "sadf3456789",
        "marketAmt": 2000,
        "respCode": "0000",
        "respMsg": "成功"},
        "interfaceId": "string",
        "reqDateTime": "string",
        "serviceCode": "string",
        "sign": "string",
        "signType": "string",
        "version": "string"}
    logger.info('请求trade端PayCb服务！')
    logger.info(sit_paycb_url)
    logger.info(request_data)
    response = requests.post(url=sit_paycb_url, json=request_data, headers=headers, timeout=5)
    logger.info(response.content)
    if response.status_code != 200:
        return '调用PayCb服务失败，请求接口状态: {0}'.format(response.status_code)
    else:
        return '调用成功！'


def sq_callback_data(**kwargs):
    """
    首汽订单回调落地-直接回调pipe
    :param request:
    :return:
    """
    sign_key = 'Py4CLvQZB5$A9hN3U'
    call_back_url = 'http://tcnl.ywsk.cn:37000/pfCallbackGateway/callback/sqCallbackOrderStatusNotify'
    headers = {'content-type': 'application/json; charset=UTF-8'}
    trade_order_id = kwargs.get('tradeOrderId')  # trade订单号
    call_back_status = kwargs.get('callBackStatus')  # 回调状态
    car_color = kwargs.get('carColor')  # 车辆颜色
    car_name = kwargs.get('carName')  # 车型名称
    driver_name = kwargs.get('driverName')  # 司机名字
    car_license = kwargs.get('carLicense')  # 车牌号码
    driver_mobile = kwargs.get('driverMobile')  # 司机电话
    driver_rate = kwargs.get('driverRate')  # 司机评分
    bank_id = int(kwargs.get('bank'))
    order_base_price = float(kwargs.get('basePrice'))  # 起步价
    high_speed_fee = float(kwargs.get('highSpeedFee'))  # 高速费
    parking_fee = float(kwargs.get('parkingFee'))  # 停车费
    airport_service_fee = float(kwargs.get('airportServiceFee'))  # 机场服务费
    room_board_fee = float(kwargs.get('roomBoardFee'))  # 食宿费
    voice_fee = float(kwargs.get('voiceFee'))  # 语音费
    hot_duration_fees = float(kwargs.get('hotDurationFees'))  # 高峰时长费
    over_time_price = float(kwargs.get('overTimePrice'))  # 超时长费
    over_mileage_price = float(kwargs.get('overMilagePrice'))  # 超里程费
    hot_mileage_fees = float(kwargs.get('hotMileageFees'))  # 高峰里程费
    waiting_fee = float(kwargs.get('waitingFee'))  # 等待费
    night_duration_fees = float(kwargs.get('nighitDurationFees'))  # 夜间时长费
    long_distance_price = float(kwargs.get('longDistancePrice'))  # 长途里程费
    night_distance_price = float(kwargs.get('nightDistancePrice'))  # 夜间服务费
    # 支付总价
    total_fee = order_base_price + high_speed_fee + parking_fee + airport_service_fee + room_board_fee + \
                voice_fee + hot_duration_fees + over_time_price + over_mileage_price + hot_mileage_fees + \
                waiting_fee + night_duration_fees + long_distance_price + night_distance_price

    car_info_detail = mysql_execute('select * from netCarPlatform.tbl_platform_car_info where trade_order_id=%s and channel_type=2 limit 1',params=(trade_order_id), bank=bank_id)
    order_detail = mysql_execute('SELECT * FROM netCarPlatform.tbl_platform_order where trade_order_id=%s',params=(trade_order_id), bank=bank_id)
    channel_order_id = car_info_detail['channel_order_id']  # 渠道ID
    partner_order_id = car_info_detail['id']
    car_type = int(car_info_detail['car_type'])  # 车型组代码

    expected_start_point = order_detail['start_point']  # 预期上车点
    expected_end_point = order_detail['end_point']  # 预期下车点
    city_code = order_detail['city_code']  # 城市编码
    order_create_time_stamp = int(int(order_detail['create_time']) / 1000)  # 获取订单创建时间的时间戳
    # 将时间戳格式化
    timeArray = time.localtime(order_create_time_stamp)
    order_create_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

    car_type_name = ''  # 车型组名称
    if car_type == 34:
        car_type_name = '舒适型'
    elif car_type == 35:
        car_type_name = '商务6座'
    elif car_type == 40:
        car_type_name = '商务福祉车'
    elif car_type == 43:
        car_type_name = '畅享型'
    elif car_type == 61:
        car_type_name = '豪华型'

    event_time = int(time.time())
    expired_time = event_time + 300
    request_data = None
    if call_back_status == 'accepted':  # 司机接单
        event_id = 'a6fb2b1034b54ca1a49c1239c6eb73af'
        driver_info = {"vehicleColor": car_color, "modelName": car_name, "groupName": car_type_name,
                       "driverRate": str(driver_rate), "driverId": "100026076",
                       "phone": "13501077762", "groupId": car_type,
                       "driverTrumpetPhone": str(driver_mobile),
                       "licensePlates": car_license, "name": driver_name, "vehiclePic": "",
                       "photoSrc": "http://m.360buyimg.com/pop/jfs/t23434/230/1763906670/10667/55866a07/5b697898N78cd1466.jpg"}

        json_meta = json.dumps(
            {"driverInfo": driver_info, "orderNo": channel_order_id, "partnerOrderNo": partner_order_id,
             "status": "accepted"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'setout':  # 司机出发
        event_id = 'c87aa95ab99c4970ad0cbbcd68ee2b88'
        json_meta = json.dumps({"orderNo": channel_order_id, "partnerOrderNo": partner_order_id, "status": "setout"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'arrived':  # 司机到达
        event_id = 'b4f731ea912041a9a10a7323eeb2d3f3'
        json_meta = json.dumps({"orderNo": channel_order_id, "partnerOrderNo": partner_order_id, "status": "arriving"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'in_progress':  # 开始服务
        event_id = 'fc11e1534a874a97be6dbd001fd1cc40'
        json_meta = json.dumps(
            {"orderNo": channel_order_id, "partnerOrderNo": partner_order_id, "status": "in_progress"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        # 回调该状态时，将当前时间用做乘客上车时间，存在redis中，过期时间24小时
        redis_execute().set(name=SQ_START_SERVICE_TIME_KEY + str(trade_order_id),
                            value=str(time.strftime("%Y-%m-%d %H:%M:%S")))
        redis_execute().expire(name=SQ_START_SERVICE_TIME_KEY + str(trade_order_id), time=86400)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'end_trip':  # 结束服务
        event_id = '2ec57b20410049ceb4ab5ff4373107a4'
        json_meta = json.dumps({"orderNo": channel_order_id, "partnerOrderNo": partner_order_id, "status": "end_trip"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        # 回调该状态时，将当前时间用做乘客下车时间，存在redis中，过期时间24小时
        redis_execute().set(name=SQ_END_SERVICE_TIME_KEY + str(trade_order_id),
                            value=str(time.strftime("%Y-%m-%d %H:%M:%S")))
        redis_execute().expire(name=SQ_END_SERVICE_TIME_KEY + str(trade_order_id), time=86400)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'reassign':  # 司机改派
        event_id = '20dee607b0064206a8e325f13c829978'
        driver_info = {"vehicleColor": '改派颜色', "modelName": '奥迪改派', "groupName": "畅享型",
                       "driverRate": '3.5', "driverId": "100026061", "phone": '13501077762',
                       "groupId": 43, "licensePlates": '京A6666', "name": '改派师傅',
                       "imei": "A0000092009549", "vehiclePic": "",
                       "photoSrc": "http://img.52z.com/upload/news/image/20180614/20180614035524_86460.jpg"}
        json_meta = json.dumps(
            {"driverInfo": driver_info, "orderNo": channel_order_id, "partnerOrderNo": partner_order_id,
             "status": "reassign"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'sys_canceled':  # 系统取消
        event_id = '4ffbaa3fbdb74e18a6fbb1b2b5f9da7f'
        json_meta = json.dumps({"orderNo": channel_order_id, "partnerOrderNo": partner_order_id,
                                "customerServiceInfo": {"opName": "", "cancelReason": "无司机，系统自动取消订单"},
                                "status": "sys_canceled"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'cs_canceled':  # 渠道客服取消
        event_id = 'da933b6437604a479f69ee92ef2bea6b'
        json_meta = json.dumps({"orderNo": channel_order_id, "partnerOrderNo": partner_order_id,
                                "customerServiceInfo": {"opName": "", "opId": 3103, "cancelReason": "联系不上乘客"},
                                "status": "cs_canceled"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'driver_overtime_canceled':  # 司机超时未到达取消
        event_id = 'b65e1821c84a4a42aefa36935d980b7b'
        json_meta = json.dumps({"orderNo": "B190412071304203000", "partnerOrderNo": "102000000622451568",
                                "customerServiceInfo": {"opName": "", "cancelReason": "司机超时未到达"},
                                "status": "driver_overtime_canceled"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,
                        "meta": json_meta, "sign": sign_id}

    elif call_back_status == 'completed':  # 订单完成
        event_id = 'f812c6b57f98430683c84643aec83e82'
        start_date = str(redis_execute().get(name=SQ_START_SERVICE_TIME_KEY + str(trade_order_id)), 'utf-8')
        logger.info('start date: {0}'.format(start_date))
        end_date = str(redis_execute().get(name=SQ_END_SERVICE_TIME_KEY + str(trade_order_id)), 'utf-8')
        logger.info('end date: {0}'.format(end_date))
        json_meta = json.dumps({"feeInfo": {"otherCost": [{"cost": high_speed_fee, "typeName": "高速服务费"},
                                                          {"cost": parking_fee, "typeName": "停车费"},
                                                          {"cost": airport_service_fee, "typeName": "机场服务费"},
                                                          {"cost": room_board_fee, "typeName": "食宿费"},
                                                          {"cost": voice_fee, "typeName": "语音费"}],
                                            "depositCreditAmount": 0,
                                            "cancelAmount": 0,
                                            "endDate": end_date,  # 实际下车时间
                                            "orderId": channel_order_id,
                                            "isAdvance": 0,
                                            "detailId": 73746114,
                                            "ddFees": 0,
                                            "cityId": city_code,  # 城市编码
                                            "dynamic_price": 0.0,
                                            "couponId": 0,
                                            "costDurationDetailDTOList": [],
                                            "couponAmount": "0",  # 优惠券金额，忽略
                                            "settleAmout": total_fee,
                                            "cancelAfterPayment": False,
                                            "nightDistancePrice": night_distance_price,  # 夜间服务费
                                            "nighitDuration": "0",  # 夜间时长
                                            "channelDiscountPercent": 0.0,
                                            "basePrice": order_base_price,  # 基础价基础价包含里程(单位:公里)
                                            "depositAmount": 0,
                                            "includeMileage": 1,  # 基础价包含里程(单位:公里)
                                            "accountPay": 0,
                                            "timePrice": "0.00",  # 分钟定价
                                            "isNewPrice": 1,
                                            "costAmount": 0,
                                            "includeMinute": 2,  # 基础价包含时长(单位:分钟)
                                            "version": "5.0",
                                            "carGroupName": car_type_name,  # 车型组名称
                                            "overMilageNumTotal": 0.00,  # 平峰里程+高峰里程
                                            "othersFee": 0.00,
                                            "groupName": car_type,  # 车型组代码
                                            "chargeSettleAmount": 0,
                                            "nightServicePrice": 0.00,
                                            "redPacketsAmount": 0.00,
                                            "driverId": 100026076,
                                            "overTimeNum": 0.00,  # 超时长数
                                            "tcFees": 0.00,
                                            "energyDiscountAmout": 0.00,
                                            "startDate": start_date,  # 实际上车时间
                                            "status": 45,
                                            "otherDepositAmount": 0,
                                            "travelMileageEnd": 0,
                                            "forecastAmount": 0.00,
                                            "customerPayPrice": total_fee,  # 乘客实际支付金额
                                            "channelPay": total_fee,
                                            "depositAccountAmount": 0,
                                            "outServicePrice": 0.00,
                                            "channelFlodAmount": 0.0,
                                            "min": 35,  # 订单总时长
                                            "hotDurationFees": hot_duration_fees,  # 高峰时长费
                                            "costMileageDetailDTOList": [],
                                            "overTimePrice": over_time_price,  # 超时长费
                                            "lineId": "",
                                            "channelDiscountType": 0,
                                            "driverPassengerPriceSeparate": True,
                                            "channelDiscountDriver": 4.22,
                                            "channelName": "partner-ywsk",
                                            "customerOweAmount": 0.00,
                                            "buyOutFlag": 0,
                                            "travelTimeStart": 58000,
                                            "endDateString": str(time.strftime('%Y-%m-%d')),
                                            "isDispatchFree": 0,
                                            "overTimeNumTotal": 0.00,  # 平峰时长+高峰时长
                                            "otherSettleAmount": 0,
                                            "gsFees": 0.00,
                                            "serviceType": "1",  # 服务类型
                                            "aliPay": 0,
                                            "chargeType": 0,
                                            "rtnResult": "S000000",
                                            "overMileageNum": 0.00,
                                            "longDistanceNum": 0.00,  # 长途里程
                                            "outServiceMileage": 0.00,
                                            "ssFees": 0,
                                            "mileage": 5.6,  # 订单总里程
                                            "nightServiceMileage": 0.00,
                                            "startPlace": expected_start_point,  # 实际上车地点
                                            "travelTime": 60000,
                                            "orderNo": channel_order_id,
                                            "hotMileage": "0.00",  # 高峰里程
                                            "paymentDiscountAmount": 0,
                                            "policyPremiumFee": 0,
                                            "yyFees": 0.00,
                                            "channelDiscountAmount": 0.0,
                                            "designatedDriverFee": 0.00,  # 指定司机附加费,无此项功能可忽略
                                            "customerRejectPay": 0.00,
                                            "riderName": "游网时空",  # 乘车人
                                            "giftSettleAmount": 0,
                                            "totalAmount": total_fee,
                                            "serverDate": str(time.strftime('%Y-%m-%d %H:%M:%S')),
                                            "hottimeFee": 0.00,
                                            "travelTimeEnd": 0,
                                            "overMilagePrice": over_mileage_price,  # 超里程费
                                            "hotMileageFees": hot_mileage_fees,  # 高峰里程费
                                            "couponSettleAmout": 0,  # 优惠券抵扣金额
                                            "nightDistanceNum": 0.00,  # 夜间服务里程
                                            "wxPay": 0,
                                            "posPay": 0,
                                            "orderStatus": 45,
                                            "travelMileageStart": 0,
                                            "mileagePrice": "0.00",  # 里程定价
                                            "factEndDate": str(time.strftime('%Y-%m-%d %H:%M:%S')),
                                            "overMileagePrice": 0.00,
                                            "costLongDistanceDetailDTOList": [],
                                            "orderCreateDate": order_create_time,
                                            "total": "17.58",  # 订单总额
                                            "waitingFee": waiting_fee,  # 等待费
                                            "carGroupId": 34,
                                            "depositPropertyCreditAmount": 0,
                                            "serviceTypeId": 1,
                                            "travelMileage": 2.00,  # 行驶里程
                                            "creditPay": 0,
                                            "waitingMinutes": waiting_fee,  # 等待时长
                                            "hotDuration": "0",  # 高峰时长
                                            "depositGiftAmount": 0,
                                            "depositSettleAmount": 0,
                                            "nighitDurationFees": night_duration_fees,  # 夜间时长费
                                            "propertyCreditPayAmount": 0,
                                            "isFamily": 0,
                                            "serviceName": "即时用车",
                                            "endPlace": expected_end_point,  # 实际下车地点
                                            "driverPay": 0,
                                            "bookingUserId": 80008650,
                                            "jcFees": 0,
                                            "overMilageNum": "0.00",  # 超里程数
                                            "longDistancePrice": long_distance_price,  # 长途里程费
                                            "actualPayAmount": total_fee,  # 乘客应付金额(优惠前)
                                            "thirdPay": 0.0,
                                            "decimalsFees": 0.00,  # 抹零费
                                            "pickupFee": 0.0,
                                            "cutPrice": 0.00},
                                "orderNo": channel_order_id,
                                "partnerOrderNo": partner_order_id,
                                "status": "completed"})
        sign_id = string_to_md5('channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id, event_time,expired_time,json_meta, sign_key))
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,"meta": json_meta, "sign": sign_id}

    elif call_back_status == 'order_finished':  # 订单确认
        event_id = 'b65e1821c84a4a42aefa36935d980b7b'
        json_meta = json.dumps({"orderNo": channel_order_id,
                                "partnerOrderNo": partner_order_id,
                                "finalStatus": {"reducePriceDesc": "",  # 减免描述信息
                                                "amount": total_fee,
                                                "riderPhone": "13712660701",  # 乘车人电话
                                                "driverPhotoSrc": "",  # 司机头像
                                                "licensePlates": car_license,  # 车牌号
                                                "riderName": "哈啰出行乘车人",  # 乘车人姓名
                                                "useCarFlag": "1",
                                                "driverScore": driver_rate,  # 司机评分
                                                "allTime": 18,
                                                "modelName": car_type_name,  # 车型名称
                                                "factEndAddr": expected_end_point,  # 实际下车地点
                                                "factStartPoint": "113.6772119140625,22.988736707899307;113.683729,22.994609",
                                                # 实际上车地点经纬度
                                                "final_status": "50",  # 状态
                                                "factEndPoint": "113.72890977647569,23.00319308810764;113.735395,23.00917",
                                                # 实际下车点经纬度
                                                "reducePrice": "",  # 减免金额
                                                "serviceTypeId": "1",  # 服务类型
                                                "bookingDate": "2019-04-12 07:43:00",  # 预约时间
                                                "driverName": "聂玉成",  # 司机姓名
                                                "driverPhone": "15814104036",  # 司机手机号
                                                "factStartAddr": expected_start_point,  # 实际上车地点
                                                "event": {"newOrderNo": "",  # 改派后订单号
                                                          "channelsNum": "partner-hellobike",  # 渠道号
                                                          "amount": total_fee,  # 最终支付金额
                                                          "originalOrderNo": channel_order_id,  # 原始订单号
                                                          "orderNo": channel_order_id,
                                                          "partnerOrderNo": partner_order_id,
                                                          "driverId": "1034588",  # 司机id
                                                          "opName": "",  # 操作说明
                                                          "opId": 10000,  # 操作ID
                                                          "eventType": "OrderSettleFinish",  # 事件类型
                                                          "cancelReason": "",  # 取消原因
                                                          "desc": ""  # 描述
                                                          },
                                                "payFlag": "0",  # 支付标志
                                                "mileage": "2.0"  # 公里数
                                                },
                                "status": "order_finished"})
        sign_id_str = 'channel=shouqi&eventId={0}&eventTime={1}&expiredTime={2}&meta={3}&sqycKey={4}'.format(event_id,event_time,expired_time,json_meta,sign_key)
        sign_id = string_to_md5(sign_id_str)
        request_data = {"channel": "shouqi", "eventId": event_id, "eventTime": event_time, "expiredTime": expired_time,"meta": json_meta, "sign": sign_id}

    resp = requests.post(url=call_back_url, params=request_data, headers=headers)
    if resp.status_code != 200:
        return '回调失败！状态码:{0}'.format(resp.status_code)
    logger.info(resp.content)
    resp_content = json.loads(resp.content)
    if resp_content['result'] == 0:
        return '回调成功！'
    else:
        return '回调失败！原因: {0}'.format(resp_content)


def sq_complaint_callback_data(**kwargs):
    """
    首汽工单回调落地-直接回调pipe
    :param request:
    :return:
    """
    logger.info(kwargs)
    sign_key = 'Py4CLvQZB5$A9hN3U'
    call_back_url = 'http://tcnl.ywsk.cn:37000/pfCallbackGateway/callback/sqCallbackComplain'
    headers = {'content-type': 'application/json; charset=UTF-8'}
    trade_order_id = kwargs.get('tradeOrderId')  # trade订单号
    amount = kwargs.get('amount')  # 金额
    is_all_refund = str(kwargs.get('isAllRefund'))  # 类型
    remark = str(kwargs.get('remark'))  # 备注
    reason = str(kwargs.get('reason'))  # 处理原因
    process_remark = str(kwargs.get('processRemark'))  # 处理原因
    refund_type = str(kwargs.get('refundType'))  # 处理原因
    bank_id = int(kwargs.get('bank'))

    car_info_detail = mysql_execute(
        'select * from tbl_platform_car_info where trade_order_id=%s and channel_type=2 and channel_order_id is not NULL',
        params=(trade_order_id), bank=bank_id)
    channel_order_id = car_info_detail['channel_order_id']
    partner_order_id = car_info_detail['id']

    complaint_detail = mysql_execute(
        'SELECT * FROM netCarPlatform.tbl_platform_complaint where trade_order_id=%s and complaint_type=1',
        params=(trade_order_id), bank=bank_id)
    if complaint_detail:
        refund_id = complaint_detail['work_order_id']
        one_level_id = complaint_detail['one_level_id']
        two_level_id = complaint_detail['two_level_id']
    else:
        refund_id = int(time.time()) + random.randint(111, 999)
        one_level_id = 4
        two_level_id = 45

    sign_id_str = 'complaintContent={8}&handler=李晶雪&isAllRefund={0}&isFirstTime=1&mitigateMoney={1}&oneLevel={9}&orderNo={2}&partnerOrderNo={3}&processRemark={10}&processState=1&reason={4}&refundId={5}&refundType={11}&remark={6}&source=partner-ywsk&sqycKey={7}'.format(
        is_all_refund, amount, channel_order_id, partner_order_id, reason, refund_id, remark, sign_key, two_level_id,
        one_level_id, process_remark, refund_type)
    sign_id = string_to_md5(sign_id_str)
    request_data = {'orderNo': channel_order_id,  # 渠道id
                    'remark': remark,
                    'mitigateMoney': amount,  # 减免金额
                    'reason': reason,  # 处理原因
                    'source': 'partner-ywsk',  # 渠道
                    'handler': '李晶雪',  # 处理人
                    'processState': '1',  # 处理状态 1：已处理，0：未处理
                    'processRemark': process_remark,  # 客服处理投诉说明
                    'refundId': refund_id,  # 退款id，对应费用投诉id
                    'partnerOrderNo': partner_order_id,  # 合作方订单号,car_info表中id
                    'refundType': refund_type,  # 退款类型：0-渠道发起的投诉，1-首汽发起的投诉
                    'isAllRefund': is_all_refund,  # 是否全额退款（0-否，1-是）
                    'isFirstTime': '1',  # 是否第一次退款（ 0-否，1-是）
                    'oneLevel': one_level_id,  # 一级分类
                    'complaintContent': two_level_id,  # 投诉内容
                    'sign': sign_id}
    logger.info('sq complaint request url: {0}'.format(call_back_url))
    logger.info('sq complaint request data: {0}'.format(request_data))
    logger.info('sq complaint request headers: {0}'.format(headers))
    resp = requests.post(url=call_back_url, params=request_data, headers=headers)
    if resp.status_code != 200:
        return '回调失败！状态码:{0}'.format(resp.status_code)
    logger.info(resp.content)
    resp_content = json.loads(resp.content)
    if resp_content['result'] == 0:
        return '回调成功！'
    else:
        return '回调失败！原因: {0}'.format(resp_content)


def sq_callback_data_for_channel(**kwargs):
    """
    首汽订单回调落地-通过首汽回调
    :param request:
    :return:
    """
    logger.info(kwargs)
    call_back_url = 'https://test-openapi.01zhuanche.com/touch/process/driver/updateOrderStatus'
    cancel_order_url = 'https://test-openapi.01zhuanche.com/touch/process/driver/cancelOrder'
    headers = {'content-type': 'application/json; charset=UTF-8'}
    trade_order_id = kwargs.get('tradeOrderId')  # trade订单号
    call_back_status = kwargs.get('callbackStatus')  # 回调状态
    car_group_id = kwargs.get('carGroupId')  # 车型组ID
    bank_id = int(kwargs.get('bank'))

    car_info_detail = mysql_execute(
        'select * from tbl_platform_car_info where trade_order_id=%s and channel_type=2 and channel_order_id is not NULL',
        params=(trade_order_id), bank=bank_id)
    channel_order_id = car_info_detail['channel_order_id']

    if call_back_status == 'cs_canceled':
        request_data = {'orderNo': channel_order_id, 'channel': 'ywsk', 'sqycKey': 'Py4CLvQZB5$A9hN3U'}

        resp = requests.post(url=cancel_order_url, params=request_data, headers=headers)
        if resp.status_code != 200:
            return '回调失败！状态码:{0}'.format(resp.status_code)
        logger.info(resp.content)
        resp_content = json.loads(resp.content)
        if int(resp_content['result']) == 0 and resp_content['data'] == '模拟客服取消成功' and resp_content[
            'errmsg'] == 'SUCCESS':
            return '回调成功！'
        else:
            return '回调失败！原因: {0}'.format(resp_content)

    else:
        request_data = {'orderNo': channel_order_id, 'orderStatus': call_back_status, 'carGroupId': car_group_id,
                        'channel': 'ywsk', 'sqycKey': 'Py4CLvQZB5$A9hN3U'}

        resp = requests.post(url=call_back_url, params=request_data, headers=headers)
        if resp.status_code != 200:
            return '回调失败！状态码:{0}'.format(resp.status_code)
        logger.info(resp.content)
        resp_content = json.loads(resp.content)
        if int(resp_content['result']) == 0 and resp_content['data'] == '更新成功' and resp_content['errmsg'] == 'SUCCESS':
            return '回调成功！'
        else:
            return '回调失败！原因: {0}'.format(resp_content)


def sz_complaint_callback_data(**kwargs):
    """
    神州工单回调落地
    :param kwargs:
    :return:
    """
    encryption_url = 'http://192.168.0.46:7003/szNetCarCallback/callback/getEncrypt'
    complaint_call_back_url = 'http://tcnl.ywsk.cn:37000/pfCallbackGateway/callback/szCallbackComplain'
    headers = {'content-type': 'application/json; charset=UTF-8'}
    trade_order_id = kwargs.get('tradeOrderId')  # trade订单号
    bank_id = int(kwargs.get('bank'))
    source_type = kwargs.get('sourceType')  # 来源类型(1:第三方,2:神州)
    process_result = kwargs.get('processResult')  # 处理结果
    refund_amount = kwargs.get('refundAmount')  # 退款金额
    is_finish = kwargs.get('isFinish')  # 是否完结(0:未完结,1:完结)
    is_support_reopen = kwargs.get('isSupportReopen')  # 是否支持再次开启(0:不支持,1:支持)
    feedback_type = '1009'
    description = '测试神州渠道直接发起'
    car_info_detail = mysql_execute(
        'select * from tbl_platform_car_info where trade_order_id=%s and channel_type=4 and channel_order_id is not NULL',
        params=(trade_order_id), bank=bank_id)
    channel_order_id = car_info_detail['channel_order_id']  # 渠道订单号
    complaint_detail = mysql_execute('select * from tbl_platform_complaint where trade_order_id=%s',
                                     params=(trade_order_id), bank=bank_id)
    if complaint_detail:
        feedback_type = complaint_detail['one_level_id']
        description = complaint_detail['content']

    request_data = json.dumps({"content": {"orderId": channel_order_id,
                                           "sourceType": source_type,
                                           "feedbackType": feedback_type,
                                           "description": description,
                                           "processResult": process_result,
                                           "refundAmount": refund_amount,
                                           "isFinish": is_finish,
                                           "isSupportReopen": is_support_reopen},
                               "operation": "feedbackOrderChanged"})

    logger.info('data string:{0}'.format(request_data))
    get_encryption = requests.get(url=encryption_url, params={'q': request_data})
    logger.info(encryption_url)
    logger.info(get_encryption.status_code)
    logger.info(get_encryption.text)
    logger.info('Get encrypted string:{0}'.format(get_encryption.text))
    logger.info('url:{0}'.format(complaint_call_back_url))
    logger.info('request data:{0}'.format({'q': get_encryption.text}))
    complaint_response = requests.get(url=complaint_call_back_url, params={'q': get_encryption.text}, headers=headers)

    if complaint_response.status_code != 200:
        return '回调失败！状态码:{0}'.format(complaint_response.status_code)
    logger.info('response:{0}'.format(complaint_response.text))
    resp_content = json.loads(complaint_response.content)
    if int(resp_content['status']) == 200:
        return '回调成功！'
    else:
        return '回调失败！原因: {0}'.format(resp_content)


def coupon_recharge_data(**kwargs):
    """
    Spdb红包充值落地
    :param kwargs:
    :return:
    """
    coupon_recharge_url = 'http://192.168.0.46:7101/netCar/api/spd/couponRecharge'
    headers = {'content-type': 'application/json; charset=UTF-8'}
    sign_key = 'bksk123kvzcnAadDnmas1;fnopij'

    def get_random_trade_no():
        """
        随机生成订单号并且数据库中不存在
        :return:
        """
        while True:
            num = str(int(time.time())) + str(random.randint(1000, 9999))
            result = mysql_execute('select * from tbl_trade_order where id=%s', params=(num), trade=True)
            if not result:
                return num

    event_id = kwargs.get('eventId')  # 活动ID
    is_user_id = kwargs.get('isUserId')  # 调用接口是否传user_id
    user_id = kwargs.get('userId')  # 用户ID
    recharge_from = '1'  # 充值来源 1=红包平台充值
    trade_no = get_random_trade_no()  # 订单号

    customer_detail = mysql_execute('select * from tbl_trade_customer where user_id=%s', params=(user_id), trade=True)
    if customer_detail:
        logger.info('user is active!')
        id_num = customer_detail['id_num']
        logger.info(id_num)
    else:
        id_num = user_id + '9999999'
        logger.info(id_num)

    coupon_amount = kwargs.get('couponAmount')  # 优惠券金额（当不传值时则走默认配置项）
    if len(coupon_amount) == 0:
        coupon_amount = None
    expire_time = kwargs.get('expireTime')  # 过期时间（当不传值时则走默认配置项）
    if len(expire_time) == 0:
        expire_time = None
    time_stamp = str(int(time.time()) * 1000)  # 时间戳（当前毫秒时间戳）
    sign_list = []
    if int(is_user_id) == 1:
        sign_list.append(user_id)
    if coupon_amount:
        sign_list.append(coupon_amount)
    if expire_time:
        sign_list.append(expire_time)
    sign_list.append(id_num)
    sign_list.append(trade_no)
    sign_list.append(event_id)
    sign_list.append(recharge_from)
    sign_list.append(time_stamp)
    sign_list.append(sign_key)
    sign_list.sort()
    sign_str = ''
    for x in sign_list:
        sign_str += x
    sign = hashlib.sha1(sign_str.encode()).hexdigest()
    logger.info('Sign is:{0}'.format(sign))

    if not coupon_amount:
        coupon_amount = None
    if not expire_time:
        expire_time = None

    data = {"eventId": event_id, "idNum": id_num, "rechargeFrom": recharge_from, "sign": sign, "timestamp": time_stamp,
            "tradeNo": trade_no}
    if int(is_user_id) == 1:
        data.update({"userId": user_id})
    if coupon_amount:
        data.update({"couponAmount": coupon_amount})
    if expire_time:
        data.update({"expireTime": expire_time})

    logger.info('request url:{0}'.format(coupon_recharge_url))
    logger.info('request data:{0}'.format(data))

    response = requests.post(url=coupon_recharge_url, json=data, headers=headers)
    if response.status_code != 200:
        return '请求失败！状态码:{0}'.format(response.status_code)
    logger.info('response:{0}'.format(response.text))
    resp_content = json.loads(response.content)
    if resp_content['errCode'] == '000000' and resp_content['success'] == True and resp_content['msg'] == '成功':
        return '请求成功！'
    else:
        return '请求失败！原因: {0}'.format(resp_content)


def sz_callback_for_pipe_data(**kwargs):
    """
    神州订单回调pipe落地
    :param request:
    :return:
    """
    call_back_url = 'http://tcnl.ywsk.cn:37000/pfCallbackGateway/callback/szCallbackOrderStatusNotify'
    headers = {'content-type': 'application/json; charset=UTF-8'}
    trade_order_id = kwargs.get('tradeOrderId')  # trade订单号
    call_back_status = kwargs.get('callBackStatus')  # 回调状态
    bank_id = int(kwargs.get('bank'))

    car_info_detail = mysql_execute('select * from netCarPlatform.tbl_platform_car_info where trade_order_id=%s and channel_type=4',params=(trade_order_id), bank=bank_id)
    if not car_info_detail:
        return '未查询到该订单！'
    channel_order_id = car_info_detail['channel_order_id']  # 渠道ID
    partner_order_id = car_info_detail['id']

    change_status_request_data = {"bankFlag": 1, "content": {"dOrderId": partner_order_id, "eventExplanation": "","orderId": channel_order_id, "status": call_back_status},"operation": "statusChanged"}

    # 更新订单详情接口返回数据
    order_detail_data = None
    default_data = json.loads(mysql_execute('select api_response from mock_response where api_url="/v1/resource/order/getOrderDetail" and channel="sz"',platform=True)['api_response'])
    default_data['content']['order']['id'] = channel_order_id
    default_data['content']['order']['customData'] = json.dumps({"dOrderId": partner_order_id})

    if call_back_status == 'dispatched':
        default_data['content']['order']['status'] = 'dispatched'
        order_detail_data = default_data

    elif call_back_status == 'arriving':
        default_data['content']['order']['status'] = 'arriving'
        order_detail_data = default_data

    elif call_back_status == 'arrived':
        default_data['content']['order']['status'] = 'arrived'
        order_detail_data = default_data

    elif call_back_status == 'serviceStarted':
        default_data['content']['order']['status'] = 'serviceStarted'
        order_detail_data = default_data

    elif call_back_status == 'serviceFinished':
        default_data['content']['order']['status'] = 'serviceFinished'
        order_detail_data = default_data

    elif call_back_status == 'balanceNotEnough':
        default_data['content']['order']['status'] = 'balanceNotEnough'
        order_detail_data = default_data

    elif call_back_status == 'rechargedInTime':
        default_data['content']['order']['status'] = 'rechargedInTime'
        order_detail_data = default_data

    elif call_back_status == 'noRetryInvalid':
        default_data['content']['order']['status'] = 'noRetryInvalid'
        order_detail_data = default_data

    elif call_back_status == 'balanceNotEnough':
        default_data['content']['order']['status'] = 'balanceNotEnough'
        order_detail_data = default_data

    elif call_back_status == 'canceled':
        default_data['content']['order']['status'] = 'canceled'
        default_data['content']['price']['detail'] = [{"amount":"15","name":"套餐价","subDetail":[]}]
        default_data['content']['price']['distance'] = 2219
        default_data['content']['price']['duration'] = 6
        default_data['content']['price']['equivalentPrice'] = 15
        default_data['content']['price']['totalPrice'] = '15'
        order_detail_data = default_data

    elif call_back_status == 'feeSubmitted':
        default_data['content']['order']['status'] = 'feeSubmitted'
        default_data['content']['order']['payStatus'] = 'unpaid'
        default_data['content']['order']['paymentStatus'] = 'unpaid'
        default_data['content']['order']['realElat'] = 39.93761
        default_data['content']['order']['realElng'] = 116.447219
        default_data['content']['order']['realEndAddress'] = '三里屯街道详细地址'
        default_data['content']['order']['realEndName'] = '三里屯街道'
        default_data['content']['order']['realSlat'] = 39.93855
        default_data['content']['order']['realSlng'] = 116.3266
        default_data['content']['order']['realStartAddress'] = '腾达大厦'
        default_data['content']['order']['realStartName'] = '腾达大厦'
        default_data['content']['price']['detail'] = [{"amount":"250","name":"套餐价","subDetail":[]},{"amount":"11.2","name":"超出里程费(4公里)","subDetail":[]},{"amount":"0.8","name":"路桥费","subDetail":[]}]
        default_data['content']['price']['distance'] = 5000
        default_data['content']['price']['duration'] = 1
        default_data['content']['price']['equivalentPrice'] = 218
        default_data['content']['price']['totalPrice'] = '262'
        order_detail_data = default_data

    elif call_back_status == 'paid':
        default_data['content']['order']['status'] = 'paid'
        default_data['content']['order']['payStatus'] = 'paid'
        default_data['content']['order']['paymentStatus'] = 'paid'
        default_data['content']['order']['realElat'] = 39.93761
        default_data['content']['order']['realElng'] = 116.447219
        default_data['content']['order']['realEndAddress'] = '三里屯街道详细地址'
        default_data['content']['order']['realEndName'] = '三里屯街道'
        default_data['content']['order']['realSlat'] = 39.93855
        default_data['content']['order']['realSlng'] = 116.3266
        default_data['content']['order']['realStartAddress'] = '腾达大厦'
        default_data['content']['order']['realStartName'] = '腾达大厦'
        default_data['content']['price']['detail'] = [{"amount":"250","name":"套餐价","subDetail":[]},{"amount":"11.2","name":"超出里程费(4公里)","subDetail":[]},{"amount":"0.8","name":"路桥费","subDetail":[]}]
        default_data['content']['price']['distance'] = 5000
        default_data['content']['price']['duration'] = 1
        default_data['content']['price']['equivalentPrice'] = 218
        default_data['content']['price']['totalPrice'] = '262'
        order_detail_data = default_data

    elif call_back_status == 'completed':
        default_data['content']['order']['status'] = 'completed'
        default_data['content']['order']['payStatus'] = 'paid'
        default_data['content']['order']['paymentStatus'] = 'paid'
        default_data['content']['order']['realElat'] = 39.93761
        default_data['content']['order']['realElng'] = 116.447219
        default_data['content']['order']['realEndAddress'] = '三里屯街道详细地址'
        default_data['content']['order']['realEndName'] = '三里屯街道'
        default_data['content']['order']['realSlat'] = 39.93855
        default_data['content']['order']['realSlng'] = 116.3266
        default_data['content']['order']['realStartAddress'] = '腾达大厦'
        default_data['content']['order']['realStartName'] = '腾达大厦'
        default_data['content']['price']['detail'] = [{"amount":"250","name":"套餐价","subDetail":[]},{"amount":"11.2","name":"超出里程费(4公里)","subDetail":[]},{"amount":"0.8","name":"路桥费","subDetail":[]}]
        default_data['content']['price']['distance'] = 5000
        default_data['content']['price']['duration'] = 1
        default_data['content']['price']['equivalentPrice'] = 218
        default_data['content']['price']['totalPrice'] = '262'
        order_detail_data = default_data

    redis_execute().set(name=str(channel_order_id) +'_sz_order_detail_response',value=json.dumps(order_detail_data))
    logger.info('redis key: {0}'.format(str(channel_order_id) +'_sz_order_detail_response'))
    logger.info('redis value: {0}'.format(json.dumps(order_detail_data)))
    logger.info('update redis success!')

    request_encrypt = requests.get(url=SZ_ENCRYPTION_URL, params={'q': str(change_status_request_data)},headers=headers)
    logger.info('sz request encrypt url: {0}'.format(SZ_ENCRYPTION_URL))
    logger.info('sz request encrypt data: {0}'.format(change_status_request_data))
    logger.info('sz request encrypt headers: {0}'.format(headers))
    logger.info(request_encrypt.text)

    resp = requests.get(url=call_back_url, params={'q': request_encrypt.text}, headers=headers)
    logger.info('sz request url: {0}'.format(call_back_url))
    logger.info('sz request data: {0}'.format(change_status_request_data))
    logger.info('sz request headers: {0}'.format(headers))
    if resp.status_code != 200:
        return '回调失败！状态码:{0}'.format(resp.status_code)
    logger.info(resp.content)
    resp_content = json.loads(resp.content)
    if resp_content['status'] == 200:
        return '回调成功！'
    else:
        return '回调失败！原因: {0}'.format(resp_content)
