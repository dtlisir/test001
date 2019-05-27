# -*- coding: utf-8 -*-
import os
import base64
import time
from config import BASE_DIR
from django.shortcuts import render
from django.http import JsonResponse
from blueking.component.shortcuts import get_client_by_request


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
def home(request):
    """
    首页
    """
    return render(request, 'home_application/home.html')


def get_biz_list(request):
    """
    获取所有业务
    """
    biz_list = []
    client = get_client_by_request(request)
    client.set_bk_api_ver("")
    kwargs = {
        "username": request.user.username,
    }
    resp = client.cc.get_app_by_user(kwargs)
    if resp['result']:
        data = resp['data']
        for _d in data:
            biz_list.append({
                'name': _d.get('ApplicationName'),
                'id': _d.get('ApplicationID'),
            })

    result = {'result': resp['result'], 'data': biz_list}
    return JsonResponse(result)


def get_host_by_bizid(request):
    """
    获取业务下IP
    """
    biz_id = int(request.GET.get('biz_id'))
    result = {'result': 'false', 'data': {}}
    client = get_client_by_request(request)
    kwargs = {
        'bk_biz_id': biz_id,
        "condition": [
            {
             "bk_obj_id": "biz",
             "fields": ['bk_biz_id', 'bk_biz_name']
            },
            {
                "bk_obj_id": "set",
                "fields": ['bk_set_id', 'bk_set_name']
            },
            {
                "bk_obj_id": "module",
                "fields": ['bk_module_id', 'bk_module_name']
            },
         ]
    }
    resp = client.cc.search_host(kwargs)

    host_list = []
    if resp['result']:
        data = resp['data']['info']
        for _d in data:
            host_list.append({
                'host_innerip': _d['host']['bk_host_innerip'],
                'cloud_name': _d['host']['bk_cloud_id'][0]['bk_inst_name'],
                'set_name': _d['set'][0]['bk_set_name'],
                'module_name': _d['module'][0]['bk_module_name'],
                'operator': _d['host']['operator'],
            })
        result = {'result': 'true', 'data': host_list}
    return JsonResponse(result)


def get_host_detail(request):
    """
    获取主机详情
    """
    biz_id = int(request.GET.get('biz_id'))
    ip = request.GET.get('host_ip')
    result = {'result': 'false', 'data': {}}
    client = get_client_by_request(request)
    kwargs = {
        'bk_biz_id': biz_id,
        "ip": {
            "data": [ip],
            "exact": 1,
            "flag": "bk_host_innerip"
        }
    }

    resp = client.cc.search_host(kwargs)

    if resp['result']:
        data = resp['data']['info'][0]['host']
        result = {'result': 'true', 'data': data}
    return JsonResponse(result)


def get_job_instance_log(client, biz_id, job_id):
    kwargs = {
        "bk_biz_id": biz_id,
        "job_instance_id": job_id
    }
    job_result = client.job.get_job_instance_log(kwargs)
    if job_result['data'][0]["is_finished"]:
        return job_result
    else:
        time.sleep(1)
        return get_job_instance_log(client, biz_id, job_id)


def get_host_mem_usage(request):
    biz_id = int(request.GET.get('biz_id'))
    host_ip = request.GET.get('host_ip')
    static_path = os.path.join(BASE_DIR, 'static')
    script_path = os.path.join(static_path, 'scripts')
    file_name = 'mem_usage.sh'
    file = os.path.join(script_path, file_name)
    with open(file) as f:
        content = f.read()
    f.close()
    script_content = base64.b64encode(content.encode('utf-8'))
    client = get_client_by_request(request)
    kwargs = {
        'bk_biz_id': biz_id,
        'script_content': str(script_content, 'utf-8'),
        'ip_list': [{"bk_cloud_id": 0, "ip": host_ip}],
        'account': 'root',
        'script_type': 1,
    }
    result = client.job.fast_execute_script(kwargs)
    if result["result"]:
        job_result = get_job_instance_log(client, biz_id, result['data']['job_instance_id'])
        if job_result['data'][0]['status'] in [3, 11]:
            data = job_result['data'][0]["step_results"][0]["ip_logs"][0]["log_content"]
            return JsonResponse({'result': True, 'data': {'value': data.split('\n')[0], 'name': '内存使用率'}})
        else:
            return JsonResponse({'result': False, 'data': {'message': job_result['message']}})
    else:
        return JsonResponse({'result': False, 'data': {'message': result['message']}})


def get_host_disk_usage(request):
    biz_id = int(request.GET.get('biz_id'))
    host_ip = request.GET.get('host_ip')
    static_path = os.path.join(BASE_DIR, 'static')
    script_path = os.path.join(static_path, 'scripts')
    file_name = 'disk_usage.sh'
    file = os.path.join(script_path, file_name)
    with open(file) as f:
        content = f.read()
    f.close()
    script_content = base64.b64encode(content.encode('utf-8'))
    client = get_client_by_request(request)
    kwargs = {
        'bk_biz_id': biz_id,
        'script_content': str(script_content, 'utf-8'),
        'ip_list': [{"bk_cloud_id": 0, "ip": host_ip}],
        'account': 'root',
        'script_type': 1,
    }
    result = client.job.fast_execute_script(kwargs)
    if result["result"]:
        job_result = get_job_instance_log(client, biz_id, result['data']['job_instance_id'])
        if job_result['data'][0]['status'] in [3, 11]:
            data = job_result['data'][0]["step_results"][0]["ip_logs"][0]["log_content"]
            return JsonResponse({'result': True, 'data': {'value': data.split('\n')[0], 'name': '磁盘使用率'}})
        else:
            return JsonResponse({'result': False, 'data': {'message': job_result['message']}})
    else:
        return JsonResponse({'result': False, 'data': {'message': result['message']}})

