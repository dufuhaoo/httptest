import json
import logging
import os
import shutil
import sys
import time
import paramiko,requests
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from djcelery.models import PeriodicTask
from dwebsocket import accept_websocket
from HttpRunnerManager import settings
from ApiManager import separator
from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo, EnvInfo, TestReports, DebugTalk, \
    TestSuite
from ApiManager.tasks import main_hrun
from ApiManager.utils.common import module_info_logic, project_info_logic, case_info_logic, config_info_logic, \
    set_filter_session, get_ajax_msg, register_info_logic, task_logic, load_modules, upload_file_logic, \
    init_filter_session, get_total_values, timestamp_to_datetime,sz_call_back_logic,pay_callback_logic,sq_call_back_logic,sq_complaint_call_back_logic,sz_complaint_call_back_logic,coupon_recharge_logic,cc_driver_callback_logic,sq_call_back_logic_for_channel,sz_callback_for_pipe_logic
from ApiManager.utils.operation import env_data_logic, del_module_data, del_project_data, del_test_data, copy_test_data, \
    del_report_data, add_suite_data, copy_suite_data, del_suite_data, edit_suite_data
from ApiManager.utils.pagination import get_pager_info
from ApiManager.utils.runner import run_by_batch, run_test_by_type
from ApiManager.utils.task_opt import delete_task, change_task_status
from ApiManager.utils.testcase import get_time_stamp
from httprunner import HttpRunner
from ApiManager.utils import redis_helper
from HttpRunnerManager.settings import BASE_DIR
from ApiManager.pf_netcar_monitoring.base_monitoring import BaseMonitoring
from ApiManager.utils.mysql_helper import mysql_execute

logger = logging.getLogger('HttpRunnerManager')

# Create your views here.



def login_check(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_status'):
            return HttpResponseRedirect('/api/login/')
        return func(request, *args, **kwargs)

    return wrapper


def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'POST':
        username = request.POST.get('account')
        password = request.POST.get('password')

        if UserInfo.objects.filter(username__exact=username).filter(password__exact=password).count() == 1:
            logger.info('{username} 登录成功'.format(username=username))
            request.session["login_status"] = True
            request.session["now_account"] = username
            return HttpResponseRedirect('/api/index/')
        else:
            logger.info('{username} 登录失败, 请检查用户名或者密码'.format(username=username))
            request.session["login_status"] = False
            return render_to_response("login.html")
    elif request.method == 'GET':
        return render_to_response("login.html")


def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.is_ajax():
        user_info = json.loads(request.body.decode('utf-8'))
        msg = register_info_logic(**user_info)
        return HttpResponse(get_ajax_msg(msg, '恭喜您，账号已成功注册'))
    elif request.method == 'GET':
        return render_to_response("register.html")


@login_check
def log_out(request):
    """
    注销登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        logger.info('{username}退出'.format(username=request.session['now_account']))
        try:
            del request.session['now_account']
            del request.session['login_status']
            init_filter_session(request, type=False)
        except KeyError:
            logging.error('session invalid')
        return HttpResponseRedirect("/api/login/")


@login_check
def index(request):
    """
    首页
    :param request:
    :return:
    """
    project_length = ProjectInfo.objects.count()
    module_length = ModuleInfo.objects.count()
    test_length = TestCaseInfo.objects.filter(type__exact=1).count()
    suite_length = TestSuite.objects.count()

    total = get_total_values()
    manage_info = {
        'project_length': project_length,
        'module_length': module_length,
        'test_length': test_length,
        'suite_length': suite_length,
        'account': request.session["now_account"],
        'total': total
    }

    init_filter_session(request)
    return render_to_response('index.html', manage_info)


@login_check
def add_project(request):
    """
    新增项目
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = project_info_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/project_list/1/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('add_project.html', manage_info)


@login_check
def add_module(request):
    """
    新增模块
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        msg = module_info_logic(**module_info)
        return HttpResponse(get_ajax_msg(msg, '/api/module_list/1/'))
    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'data': ProjectInfo.objects.all().values('project_name')
        }
        return render_to_response('add_module.html', manage_info)


@login_check
def add_case(request):
    """
    新增用例
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        testcase_info = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(**testcase_info)
        return HttpResponse(get_ajax_msg(msg, '/api/test_list/1/'))
    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
        }
        return render_to_response('add_case.html', manage_info)


@login_check
def add_config(request):
    """
    新增配置
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        testconfig_info = json.loads(request.body.decode('utf-8'))
        msg = config_info_logic(**testconfig_info)
        return HttpResponse(get_ajax_msg(msg, '/api/config_list/1/'))
    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
        }
        return render_to_response('add_config.html', manage_info)


@login_check
def run_test(request):
    """
    运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        id = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        run_test_by_type(id, base_url, testcase_dir_path, type)
        report_name = kwargs.get('report_name', None)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        id = request.POST.get('id')
        base_url = request.POST.get('env_name')
        type = request.POST.get('type', 'test')

        run_test_by_type(id, base_url, testcase_dir_path, type)
        runner.run(testcase_dir_path)
        shutil.rmtree(testcase_dir_path)
        runner.summary = timestamp_to_datetime(runner.summary, type=False)

        return render_to_response('report_template.html', runner.summary)


@login_check
def run_batch_test(request):
    """
    批量运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        test_list = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        report_name = kwargs.get('report_name', None)
        run_by_batch(test_list, base_url, testcase_dir_path, type=type)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        type = request.POST.get('type', None)
        base_url = request.POST.get('env_name')
        test_list = request.body.decode('utf-8').split('&')
        if type:
            run_by_batch(test_list, base_url, testcase_dir_path, type=type, mode=True)
        else:
            run_by_batch(test_list, base_url, testcase_dir_path)

        runner.run(testcase_dir_path)

        shutil.rmtree(testcase_dir_path)
        runner.summary = timestamp_to_datetime(runner.summary,type=False)

        return render_to_response('report_template.html', runner.summary)


@login_check
def project_list(request, id):
    """
    项目列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        if 'mode' in project_info.keys():
            msg = del_project_data(project_info.pop('id'))
        else:
            msg = project_info_logic(type=False, **project_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(
            ProjectInfo, filter_query, '/api/project_list/', id)
        manage_info = {
            'account': account,
            'project': pro_list[1],
            'page_list': pro_list[0],
            'info': filter_query,
            'sum': pro_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project_all': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('project_list.html', manage_info)


@login_check
def module_list(request, id):
    """
    模块列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        if 'mode' in module_info.keys():  # del module
            msg = del_module_data(module_info.pop('id'))
        else:
            msg = module_info_logic(type=False, **module_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        module_list = get_pager_info(
            ModuleInfo, filter_query, '/api/module_list/', id)
        manage_info = {
            'account': account,
            'module': module_list[1],
            'page_list': module_list[0],
            'info': filter_query,
            'sum': module_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('module_list.html', manage_info)


@login_check
def test_list(request, id):
    """
    用例列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        test_info = json.loads(request.body.decode('utf-8'))

        if test_info.get('mode') == 'del':
            msg = del_test_data(test_info.pop('id'))
        elif test_info.get('mode') == 'copy':
            msg = copy_test_data(test_info.get('data').pop('index'), test_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))

    else:
        filter_query = set_filter_session(request)
        test_list = get_pager_info(
            TestCaseInfo, filter_query, '/api/test_list/', id)
        manage_info = {
            'account': account,
            'test': test_list[1],
            'page_list': test_list[0],
            'info': filter_query,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('test_list.html', manage_info)


@login_check
def config_list(request, id):
    """
    配置列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        test_info = json.loads(request.body.decode('utf-8'))

        if test_info.get('mode') == 'del':
            msg = del_test_data(test_info.pop('id'))
        elif test_info.get('mode') == 'copy':
            msg = copy_test_data(test_info.get('data').pop('index'), test_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        test_list = get_pager_info(
            TestCaseInfo, filter_query, '/api/config_list/', id)
        manage_info = {
            'account': account,
            'test': test_list[1],
            'page_list': test_list[0],
            'info': filter_query,
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('config_list.html', manage_info)


@login_check
def edit_case(request, id=None):
    """
    编辑用例
    :param request:
    :param id:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        testcase_lists = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(type=False, **testcase_lists)
        return HttpResponse(get_ajax_msg(msg, '/api/test_list/1/'))

    test_info = TestCaseInfo.objects.get_case_by_id(id)
    request = eval(test_info[0].request)
    include = eval(test_info[0].include)
    manage_info = {
        'account': account,
        'info': test_info[0],
        'request': request['test'],
        'include': include,
        'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
    }
    return render_to_response('edit_case.html', manage_info)


@login_check
def edit_config(request, id=None):
    """
    编辑配置
    :param request:
    :param id:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        testconfig_lists = json.loads(request.body.decode('utf-8'))
        msg = config_info_logic(type=False, **testconfig_lists)
        return HttpResponse(get_ajax_msg(msg, '/api/config_list/1/'))

    config_info = TestCaseInfo.objects.get_case_by_id(id)
    request = eval(config_info[0].request)
    manage_info = {
        'account': account,
        'info': config_info[0],
        'request': request['config'],
        'project': ProjectInfo.objects.all().values(
            'project_name').order_by('-create_time')
    }
    return render_to_response('edit_config.html', manage_info)


@login_check
def env_set(request):
    """
    环境设置
    :param request:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        env_lists = json.loads(request.body.decode('utf-8'))
        msg = env_data_logic(**env_lists)
        return HttpResponse(get_ajax_msg(msg, 'ok'))

    elif request.method == 'GET':
        return render_to_response('env_list.html', {'account': account})


@login_check
def env_list(request, id):
    """
    环境列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.method == 'GET':
        env_lists = get_pager_info(
            EnvInfo, None, '/api/env_list/', id)
        manage_info = {
            'account': account,
            'env': env_lists[1],
            'page_list': env_lists[0],
        }
        return render_to_response('env_list.html', manage_info)


@login_check
def report_list(request, id):
    """
    报告列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    if request.is_ajax():
        report_info = json.loads(request.body.decode('utf-8'))

        if report_info.get('mode') == 'del':
            msg = del_report_data(report_info.pop('id'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        report_list = get_pager_info(
            TestReports, filter_query, '/api/report_list/', id)
        manage_info = {
            'account': request.session["now_account"],
            'report': report_list[1],
            'page_list': report_list[0],
            'info': filter_query
        }
        return render_to_response('report_list.html', manage_info)


@login_check
def view_report(request, id):
    """
    查看报告
    :param request:
    :param id: str or int：报告名称索引
    :return:
    """
    reports = TestReports.objects.get(id=id).reports
    return render_to_response('view_report.html', {"reports": mark_safe(reports)})


@login_check
def periodictask(request, id):
    """
    定时任务列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        mode = kwargs.pop('mode')
        id = kwargs.pop('id')
        msg = delete_task(id) if mode == 'del' else change_task_status(id, mode)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        task_list = get_pager_info(
            PeriodicTask, filter_query, '/api/periodictask/', id)
        manage_info = {
            'account': account,
            'task': task_list[1],
            'page_list': task_list[0],
            'info': filter_query
        }
    return render_to_response('periodictask_list.html', manage_info)


@login_check
def add_task(request):
    """
    添加任务
    :param request:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = task_logic(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/api/periodictask/1/'))
    elif request.method == 'GET':
        info = {
            'account': account,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-create_time')
        }
        return render_to_response('add_task.html', info)


@login_check
def upload_file(request):
    account = request.session["now_account"]
    if request.method == 'POST':
        try:
            project_name = request.POST.get('project')
            module_name = request.POST.get('module')
        except KeyError as e:
            return JsonResponse({"status": e})

        if project_name == '请选择' or module_name == '请选择':
            return JsonResponse({"status": '项目或模块不能为空'})

        upload_path = sys.path[0] + separator + 'upload' + separator

        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)

        os.mkdir(upload_path)

        upload_obj = request.FILES.getlist('upload')
        file_list = []
        for i in range(len(upload_obj)):
            temp_path = upload_path + upload_obj[i].name
            file_list.append(temp_path)
            try:
                with open(temp_path, 'wb') as data:
                    for line in upload_obj[i].chunks():
                        data.write(line)
            except IOError as e:
                return JsonResponse({"status": e})

        upload_file_logic(file_list, project_name, module_name, account)

        return JsonResponse({'status': '/api/test_list/1/'})


@login_check
def get_project_info(request):
    """
     获取项目相关信息
     :param request:
     :return:
     """

    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))

        msg = load_modules(**project_info.pop('task'))
        return HttpResponse(msg)


@login_check
def download_report(request, id):
    if request.method == 'GET':

        summary = TestReports.objects.get(id=id)
        reports = summary.reports
        start_at = summary.start_at

        if os.path.exists(os.path.join(os.getcwd(), "reports")):
            shutil.rmtree(os.path.join(os.getcwd(), "reports"))
        os.makedirs(os.path.join(os.getcwd(), "reports"))

        report_path = os.path.join(os.getcwd(), "reports{}{}.html".format(separator, start_at.replace(":", "-")))
        with open(report_path, 'w+', encoding='utf-8') as stream:
            stream.write(reports)

        def file_iterator(file_name, chunk_size=512):
            with open(file_name, encoding='utf-8') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(report_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(start_at.replace(":", "-") + '.html')
        return response


@login_check
def debugtalk(request, id=None):
    if request.method == 'GET':
        debugtalk = DebugTalk.objects.values('id', 'debugtalk').get(id=id)
        return render_to_response('debugtalk.html', debugtalk)
    else:
        id = request.POST.get('id')
        debugtalk = request.POST.get('debugtalk')
        code = debugtalk.replace('new_line', '\r\n')
        obj = DebugTalk.objects.get(id=id)
        obj.debugtalk = code
        obj.save()
        return HttpResponseRedirect('/api/debugtalk_list/1/')


@login_check
def debugtalk_list(request, id):
    """
       debugtalk.py列表
       :param request:
       :param id: str or int：当前页
       :return:
       """

    account = request.session["now_account"]
    debugtalk = get_pager_info(
        DebugTalk, None, '/api/debugtalk_list/', id)
    manage_info = {
        'account': account,
        'debugtalk': debugtalk[1],
        'page_list': debugtalk[0],
    }
    return render_to_response('debugtalk_list.html', manage_info)


@login_check
def suite_list(request, id):
    account = request.session["now_account"]
    if request.is_ajax():
        suite_info = json.loads(request.body.decode('utf-8'))

        if suite_info.get('mode') == 'del':
            msg = del_suite_data(suite_info.pop('id'))
        elif suite_info.get('mode') == 'copy':
            msg = copy_suite_data(suite_info.get('data').pop('index'), suite_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(
            TestSuite, filter_query, '/api/suite_list/', id)
        manage_info = {
            'account': account,
            'suite': pro_list[1],
            'page_list': pro_list[0],
            'info': filter_query,
            'sum': pro_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('suite_list.html', manage_info)


@login_check
def add_suite(request):
    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = add_suite_data(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/api/suite_list/1/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
        }
        return render_to_response('add_suite.html', manage_info)

@login_check
def test_url(request):
    return render_to_response('test_url.html')


@login_check
def edit_suite(request, id=None):
    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = edit_suite_data(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/api/suite_list/1/'))

    suite_info = TestSuite.objects.get(id=id)
    manage_info = {
        'account': account,
        'info': suite_info,
        'project': ProjectInfo.objects.all().values(
            'project_name').order_by('-create_time')
    }
    return render_to_response('edit_suite.html', manage_info)

@login_check
@accept_websocket
def echo(request):
    if not request.is_websocket():
        return render_to_response('echo.html')
    else:
        servers = []
        for message in request.websocket:
            try:
                servers.append(message.decode('utf-8'))
            except AttributeError:
                pass
            if len(servers) == 4:
                break
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(servers[0], 5858, username=servers[1], password=servers[2], timeout=10)
        while True:
            cmd = servers[3]
            stdin, stdout, stderr = client.exec_command(cmd)
            for i, line in enumerate(stdout):
                request.websocket.send(bytes(line, encoding='utf8'))
            client.close()


@login_check
def pay_callback(request):
    """
    Spdb订单支付回调
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = pay_callback_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/pay_callback/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('pay_callback.html', manage_info)


@login_check
def spdb_test_helper(request):
    """
    Spdb测试辅助
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]

    # 查询订单支付轮循状态
    round_flag = False
    run_detail = os.popen('ps -ef | grep spdb_pay_round | grep -v grep').readlines()
    logger.info('Query Spdb order round-robin task: {0}'.format(run_detail))
    if run_detail:
        round_flag = True
    max_times = redis_helper.redis_execute().get(name=redis_helper.SPDB_PAYCB_ROUNT_MAX_NUMBER_KEY)
    logger.info('Maximum number of rotation: {0}'.format(max_times))
    current_times = redis_helper.redis_execute().get(name=redis_helper.SPDB_PAYCB_ROUNT_CURRENT_NUMBER_KEY)
    logger.info('Current cycle times: {0}'.format(current_times))
    progress = 0
    if max_times and current_times:
        progress = int(int(current_times) / int(max_times) * 100)
        logger.info('The current progress: {0}'.format(progress))
    flag = False
    # 查询全员免密状态
    secret_state = redis_helper.redis_execute(trade=True).get(name='netcar:secretState:')
    if secret_state == None:
        secret_state = True
    else:
        if int(str(secret_state, 'utf-8')) == 1:
            flag = True
        else:
            flag = False

    logger.info('At present, all employees are exempt from confidentiality: {0}'.format(secret_state))
    manage_info = {'account': account,
                   'round_task': {'name':'Spdb订单支付轮循', 'enabled':round_flag,'progress':progress},
                   'secret_task':{'name':'Spdb全员免密开关', 'enabled':flag}}

    return render_to_response('spdb_test_helper.html', manage_info)


@login_check
def spdb_monitoring(request):
    """
    Spdb场景监控
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]
    result_list = []

    def query_ps_and_redis(monitoring_file_name):
        """
        查询进程状态与Redis结果数据
        :param monitoring_file_name:
        :return:
        """
        running_flag = '未启动'
        # 查询该任务是否正在运行
        run_detail = os.popen('ps -ef | grep %s | grep -v grep' % monitoring_file_name).readlines()
        logger.info('Query Spdb {0} task: {1}'.format(monitoring_file_name, run_detail))
        if run_detail:
            running_flag = '运行中'
        else:
            # 查询该任务是都在待执行列表中
            redis_value = redis_helper.redis_execute().get(redis_helper.TEST_SUITE_KEY)
            if redis_value:
                down_job_detail = json.loads(redis_value)
                down_job_list = down_job_detail['down_job_list']
                if monitoring_file_name in str(down_job_list):
                    running_flag = '等待中'

        run_result_flag = True
        result_format = {'monitoring_name':None,'run_time':None,'running_time':None,'time_diff':None}
        run_result = redis_helper.redis_execute().get(name=monitoring_file_name)
        result_info = []
        if run_result:
            result_format = json.loads(run_result)
            for x in result_format['result']:
                if x['result'] != True:
                    run_result_flag = False
                    result_info.append({"method_name": x['method'], 'message': x['message']})

        # 获取近10次执行结果通过率
        run_success_percent_last_ten = 0
        last_ten_run_details = mysql_execute('select * from test_http.pf_monitoring where redis_key=%s order by create_time desc limit 10',params=(monitoring_file_name),platform=True,is_fetchone=False)
        run_list = []
        if last_ten_run_details:
            for i in last_ten_run_details:
                run_list.append(int(i['result']))
            success_num = run_list.count(0)
            run_success_percent_last_ten = int(int(success_num) / len(last_ten_run_details) * 100)

        # 获取全部执行结果通过率
        all_run_success_percent = 0
        all_run_details = mysql_execute('select * from test_http.pf_monitoring where redis_key=%s',params=(monitoring_file_name),platform=True,is_fetchone=False)
        all_run_list = []
        if all_run_details:
            for i in all_run_details:
                all_run_list.append(int(i['result']))
            all_success_num = all_run_list.count(0)
            all_run_success_percent = int(int(all_success_num) / len(all_run_details) * 100)

        result_list.append({'name': result_format['monitoring_name'], 'last_ten_success_percent':run_success_percent_last_ten,'all_success_percent':all_run_success_percent,'enabled': running_flag, 'status': run_result_flag,
             'message': result_info, 'run_time': result_format['run_time'],'running_time':result_format['running_time'], 'monitoring_name': monitoring_file_name,'time_diff':result_format['time_diff']})

    query_ps_and_redis(monitoring_file_name='forbidden_create_order_monitoring')
    query_ps_and_redis(monitoring_file_name='notice_manager_monitoring')
    query_ps_and_redis(monitoring_file_name='activity_rule_manager_monitoring')
    query_ps_and_redis(monitoring_file_name='activity_manager_monitoring')
    query_ps_and_redis(monitoring_file_name='contact_monitoring')
    query_ps_and_redis(monitoring_file_name='blacklist_manager_monitoring')
    query_ps_and_redis(monitoring_file_name='coupon_recharge_monitoring')
    query_ps_and_redis(monitoring_file_name='image_manager_monitoring')
    query_ps_and_redis(monitoring_file_name='activity_display_manager_monitoring')
    query_ps_and_redis(monitoring_file_name='flight_info_monitoring')
    query_ps_and_redis(monitoring_file_name='system_cancel_order_monitoring')
    query_ps_and_redis(monitoring_file_name='common_address_monitoring')
    system_info = BaseMonitoring().get_system_usage_info()
    system_ip = BaseMonitoring().get_host_ip()
    logger.info(system_info)
    memory_usage = '%.2f' % (system_info['memory_info']['usage'])
    memory_percent = system_info['memory_info']['percent']
    memory_free = '%.2f' % (system_info['memory_info']['free'])
    cpu_percent = system_info['cpu_info']['percent']
    system_info_text = '服务器IP地址:{0} ,当前已使用内存:{1}G ,内存使用率:{2}% ,剩余内存:{3}G ,CPU使用率:{4}%'.format(system_ip,memory_usage,memory_percent,memory_free,cpu_percent)
    system_content = {'memory_usage':float(memory_usage),'memory_free':float(memory_free),'memory_percent':float(memory_percent),'cpu_percent':float(cpu_percent),'ip':system_ip,'desc':system_info_text}
    manage_info = {'account': account,'result_list': result_list,'system_info':system_content}
    logger.info(manage_info)
    return render_to_response('spdb_monitoring.html', manage_info)

@login_check
def start_or_stop_monitoring(request):
    """
    场景监控开启、关闭
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        mode = kwargs['mode']
        monitoring_name = kwargs['monitoring_name']
        logger.info('params mode: {0}'.format(mode))
        logger.info('monitoring name:{0}'.format(monitoring_name))

        if mode == True:
            if monitoring_name == 'all':
                all_key = redis_helper.KEY_LIST
                logger.info('all monitoring key:{0}'.format(all_key))
                # 过滤掉当前正在执行的任务，将待执行的任务名称加入list
                down_job_list = []
                for x in all_key:
                    run_detail = os.popen('ps -ef | grep {0} | grep -v grep'.format(x)).readlines()
                    if not run_detail:
                        down_job_list.append({'monitoring_name':x,'status_desc':'等待中','join_time':time.time()})
                # 将待执行任务添加到redis
                logger.info('Inhale the queue to be executed!')
                logger.info('down job list : {0}'.format(down_job_list))
                value = {'down_job_list':down_job_list}
                redis_helper.redis_execute().set(redis_helper.TEST_SUITE_KEY,json.dumps(value))
                logger.info('Store successful!')
                return HttpResponse('ok')
            else:
                run_detail = os.popen('ps -ef | grep {0} | grep -v grep'.format(monitoring_name)).readlines()
                if run_detail:
                    return HttpResponse('正在运行中！')
                # 获取待执行列表
                down_job_detail = json.loads(redis_helper.redis_execute().get(redis_helper.TEST_SUITE_KEY))
                down_job_list = down_job_detail['down_job_list']
                logger.info('down job list:{0}'.format(down_job_detail))
                # 判断该任务是否在待执行列表中
                if monitoring_name in str(down_job_list):
                    return HttpResponse('已在待执行队列中，请等待！')
                else:
                    down_job_detail['down_job_list'].append({'monitoring_name':monitoring_name,'status_desc':'等待中','join_time':time.time()})
                    redis_helper.redis_execute().set(redis_helper.TEST_SUITE_KEY, json.dumps(down_job_detail))
                    logger.info('Update successful!')
                    logger.info('down job list:{0}'.format(down_job_detail))
                    return HttpResponse('ok')

        elif mode == False:
            if monitoring_name == 'all':
                # 获取待执行任务列表
                down_job_detail = json.loads(redis_helper.redis_execute().get(redis_helper.TEST_SUITE_KEY))
                down_job_detail['down_job_list'] = []
                redis_helper.redis_execute().set(redis_helper.TEST_SUITE_KEY, json.dumps(down_job_detail))
                logger.info('Update successful!')
                logger.info('down job list:{0}'.format(down_job_detail))
                return HttpResponse('ok')
            else:
                # monitoring_name = 'monitoring'
                # logger.info('Query Spdb {0}!'.format(monitoring_name))
                # pids = os.popen("ps -ef | grep %s | grep -v grep | awk '{print $2}'" % monitoring_name)
                # if pids:
                #     return HttpResponse('正在运行，请等待执行完成！')

                down_job_detail = json.loads(redis_helper.redis_execute().get(redis_helper.TEST_SUITE_KEY))
                down_job_list = down_job_detail['down_job_list']
                logger.info('down job list:{0}'.format(down_job_detail))
                for x in down_job_list:
                    # 判断该任务是否在待执行列表中，如果存在则在列表中删除
                    if monitoring_name == x['monitoring_name']:
                        down_job_list.remove(x)
                        redis_helper.redis_execute().set(redis_helper.TEST_SUITE_KEY, json.dumps(down_job_detail))
                        logger.info('Update successful!')
                        logger.info('down job list:{0}'.format(down_job_detail))
                        return HttpResponse('ok')

        return HttpResponse('ok')
    else:
        return HttpResponse('请求方式错误！')

@login_check
def spdb_secret_settings(request):
    """
    浦发全员开通免密开通、关闭
    :param request:
    :return:
    """
    if request.is_ajwax():
        kwargs = json.loads(request.body.decode('utf-8'))
        mode = kwargs['mode']
        logger.info('secret settings params mode: {0}'.format(mode))
        data = None
        if mode == True:
            logger.info('Open Spdb all employees free of secret payment!')
            data = {'state':1}
        elif mode == False:
            logger.info('Close all Spdb confidential payment!')
            data = {'state':0}
        response = requests.get(url='http://testzx.ywsk.cn:38000/netCar/api/test/settingSecretState',params=data,headers={'content-type': 'application/json; charset=UTF-8'})
        if response.status_code != 200:
            return HttpResponse('Spdb全员免密接口请求失败！原因: {0}'.format(response.status_code))
        resp_content = json.loads(response.content)
        if resp_content['code'] == 0 and resp_content['success'] == True and resp_content['msg'] == 'OK':
            return HttpResponse('ok')
        else:
            return HttpResponse('请求全员免密接口失败！原因: {0}'.format(resp_content))
    else:
        return HttpResponse('请求方式错误！')


@login_check
def start_stop_spdb_pay_round(request):
    """
    Spdb订单支付轮循开启、关闭
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        mode = kwargs['mode']
        logger.info('params mode: {0}'.format(mode))

        if mode == True:
            run_detail = os.popen('ps -ef | grep spdb_pay_round | grep -v grep').readlines()
            if run_detail:
                return HttpResponse('正在运行中，请勿重复执行！')

            logger.info('Start Spdb order payment round robin!')
            command = "cd {0} && export PYTHONPATH=. && nohup {1} {2}&".format(BASE_DIR,settings.SERVER_PYTHON_PATH,settings.SPDB_PAYCB_ROUND_JOB_PATH)
            logger.info('Execute system commands: {0}'.format(command))
            os.system(command)
            time.sleep(0.3)

        elif mode == False:
            logger.info('Turn off Spdb order payment cycle!')
            pids = os.popen("ps -ef | grep 'spdb_pay_round' | grep -v grep | awk '{print $2}'")
            for pid in pids:
                command = 'kill -9 %s' % pid
                os.system(command)
                time.sleep(0.2)
        return HttpResponse('ok')
    else:
        return HttpResponse('请求方式错误！')


@login_check
def cc_driver_callback(request):
    """
    曹操司机端操作
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        logger.info(project_info)
        msg = cc_driver_callback_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/cc_driver_callback/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('cc_driver_call_back.html', manage_info)


@login_check
def sz_callback(request):
    """
    神州渠道订单回调
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = sz_call_back_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/sz_callback/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('sz_callback.html', manage_info)


@login_check
def sq_callback(request):
    """
    首汽渠道订单回调
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = sq_call_back_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/sq_callback/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('sq_callback.html', manage_info)

@login_check
def sq_callback_for_channel(request):
    """
    首汽渠道订单回调
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = sq_call_back_logic_for_channel(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/sq_callback_for_channel/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('sq_callback_for_channel.html', manage_info)


@login_check
def sq_complaint_callback(request):
    """
    首汽渠道工单回调
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        logger.info(project_info)
        msg = sq_complaint_call_back_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/sq_complaint_callback/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('sq_complaint_call_back.html', manage_info)

@login_check
def sz_complaint_callback(request):
    """
    神州渠道工单回调
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        logger.info(project_info)
        msg = sz_complaint_call_back_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/sz_complaint_callback/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('sz_complaint_call_back.html', manage_info)


def coupon_recharge(request):
    """
    Spdb红包充值
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = coupon_recharge_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/coupon_recharge/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('coupon_recharge.html', manage_info)

def sz_callback_for_pipe(request):
    """
    神州订单回调pipe
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = sz_callback_for_pipe_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/sz_callback_for_pipe/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('sz_callback_for_pipe.html', manage_info)