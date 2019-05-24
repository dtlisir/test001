# -*- coding: utf-8 -*-
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
    resp = client.cc.get_app_by_user(**kwargs)
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
    biz_id = int(request.POST.get('biz_id'))
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
    resp = client.cc.search_host(**kwargs)

    host_list = []
    if resp['result']:
        data = resp['data']['info']
        for _d in data:
            host_list.append({
                'host_innerip': _d['host']['bk_host_innerip'],
                'cloud_name': _d['host']['bk_cloud_id'][0]['bk_inst_name'],
                'set_name': _d['set'][0]['bk_set_name'],
                'module_name': _d['module'][0]['bk_module_name'],
                'host_outerip': _d['host']['bk_host_outerip'],
                'operator': _d['host']['operator'],
                'host_detail': _d['host']
            })

    result = {'data': host_list}
    return JsonResponse(result)

