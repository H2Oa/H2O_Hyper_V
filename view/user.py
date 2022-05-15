# -*- coding: utf-8 -*-
# Author: XiaoXinYo

from flask import Blueprint, redirect, render_template, request, session
from modular import core, user, virtual_machine, auxiliary, hyper_v

USER_APP = Blueprint('USER_APP', __name__)

@USER_APP.route('/user/', methods=['GET', 'POST'])
def redirect_d():
    return redirect('./index')

@USER_APP.route('/user/index', methods=['GET', 'POST'])
def index():
    account_number = session.get('account_number')
    return render_template(
        'user/index.html',
        title=core.get_core('title'),
        keyword=core.get_core('keyword'),
        description=core.get_core('description'),
        notice=core.get_notice(),
        account_number=account_number,
        password=user.get_password(account_number),
        qq_number=user.get_qq_number(account_number),
        register_date=user.get_register_date(account_number),
        virtual_machine_number=len(virtual_machine.get_use_user(account_number)),
        now_year=auxiliary.get_now_year()
    )

@USER_APP.route('/user/virtual_machine', methods=['GET', 'POST'])
def virtual_machine_d():
    account_number = session.get('account_number')
    return render_template(
        'user/virtual_machine.html',
        title=core.get_core('title'),
        keyword=core.get_core('keyword'),
        description=core.get_core('description'),
        now_year=auxiliary.get_now_year()
    )

@USER_APP.route('/user/logout')
def logout():
    session.clear()
    return redirect('../login')

@USER_APP.route('/user/ajax', methods=['GET', 'POST'])
def ajax():
    parameter = core.get_request_parameter(request)
    action = parameter.get('action')
    account_number = session.get('account_number')
    
    if auxiliary.empty_many(action, account_number):
        return core.generate_response_json_result('参数错误')

    if action == 'revise_account':
        new_password = parameter.get('new_password')
        new_qq_number = parameter.get('new_qq_number')
        if not auxiliary.empty(new_password) and len(new_password) < 8:
            return core.generate_response_json_result('密码长度至少8位')
        else:
            if not auxiliary.empty(new_password):
                user.set(account_number, 'password', auxiliary.get_md5(new_password))
            if not auxiliary.empty(new_qq_number):
                user.set(account_number ,'qq_number', new_qq_number)
            return core.generate_response_json_result('修改成功')
    elif action == 'get_virtual_machine':
        format_d = parameter.get('format')
        
        data = virtual_machine.get_use_user(account_number)
        if format_d == 'layui':
            information = []
            for data_count in data:
                data_single = data.get(data_count)
                information.append({
                    'name': data_count,
                    'state': data_single.get('state'),
                    'due_date': data_single.get('due_date'),
                    'remarks':data_single.get('remarks')
                })
            return core.generate_layui_response_json_result(information)
        else:
            information = {}
            for data_count in data:
                data_single = data.get(data_count)
                information[data_count] = {
                    'state': data_single.get('state'),
                    'due_date': data_single.get('due_date'),
                    'remarks':data_single.get('remarks')
                }
            return core.generate_response_json_result(information)
    
    name = parameter.get('name')
    vm = virtual_machine.get_use_user(account_number)
    
    if auxiliary.empty(name):
        return core.generate_response_json_result('参数错误')
    
    if name not in hyper_v.get():
        return core.generate_response_json_result('虚拟机不存在')
    elif name not in vm:
        return core.generate_response_json_result('权限错误')
    elif virtual_machine.is_due(name):
        return core.generate_response_json_result('该虚拟机已到期')
    
    if action == 'start_virtual_machine':
        hyper_v.start(name)
        return core.generate_response_json_result('开机成功')
    elif action == 'shutdown_virtual_machine':
        hyper_v.shutdown(name)
        return core.generate_response_json_result('关机成功')
    elif action == 'force_shutdown_virtual_machine':
        hyper_v.force_shutdown(name)
        return core.generate_response_json_result('强制关机成功')
    elif action == 'restart_virtual_machine':
        hyper_v.restart(name)
        return core.generate_response_json_result('重启成功')
    elif action == 'get_virtual_machine_checkpoint':
        information = ''
        checkpoint = hyper_v.get_checkpoint(name)
        for checkpoint_count in checkpoint:
            information += checkpoint_count + '\n'
        if information:
            information = checkpoint_information[:-1]
        return core.generate_response_json_result(information)
    elif action == 'apply_virtual_machine_checkpoint':
        checkpoint_name = parameter.get('checkpoint_name')
        
        if auxiliary.empty(checkpoint_name):
            return core.generate_response_json_result('参数错误')
        
        if checkpoint_name not in hyper_v.get_checkpoint(name):
            return core.generate_response_json_result('检查点不存在')
        hyper_v.apply_checkpoint(name, checkpoint_name)
        return core.generate_response_json_result('恢复检查点成功')
    elif action == 'remarks_virtual_machine':
        content = parameter.get('content')
        
        if auxiliary.empty(content):
            return core.generate_response_json_result('参数错误')
        
        virtual_machine.set_remarks(name, 'user', content)
        return core.generate_response_json_result('备注成功')
    return core.generate_response_json_result('参数错误')