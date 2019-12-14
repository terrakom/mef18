# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from .mef18_utils import Mef18Consumers
from . import warrior_utils
import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import threading

# Private methods and globals
CONSUMERS = None
CONSUMERS_INIT_LOCK = threading.Lock()
WARRIOR = None
WARRIOR_INIT_LOCK = threading.Lock()


def _init_consumers():
    global CONSUMERS
    global CONSUMERS_INIT_LOCK
    with CONSUMERS_INIT_LOCK:
        if CONSUMERS is None:
            CONSUMERS = Mef18Consumers()
            # server = "100.0.0.200:9092"
            # group_id = "w1"
            # topics = ["test"]
            # settings = {'server': server, 'group_id': group_id, 'topics': topics}
            # CONSUMERS.create_consumer('default', settings)
        return CONSUMERS


def _init_warrior():
    global WARRIOR
    global WARRIOR_INIT_LOCK
    with WARRIOR_INIT_LOCK:
        if WARRIOR is None:
            WARRIOR = warrior_utils.WarriorAdaptor()
        return WARRIOR


# Create your views here.
def index(request):
    consumers = _init_consumers()
    context = {'states': list(consumers.get_states()),
               'kafka': consumers.get_consumer_settings(),
               'bw': consumers.get_bw()}
    template = "mef18/index.html"
    return render(request, template, context)


def kafka_consumers(request):
    """
    Respond to POST, GET, DELETE for kafka consumer settings.
    If POST, create a Kafka consumer given settings in POST body.
    If GET, retrieve all Kafka consumers
    :param request: HTTP request
    :return:
    """
    consumers = _init_consumers()
    response = HttpResponse()
    if request.method == 'POST':
        try:
            settings = json.loads(request.body.decode('utf-8'))
            id = settings.get('id', 1)
            if 'id' in settings:
                del settings['id']
            c = consumers.create_consumer(id, settings)
            settings = {'settings': consumers.get_consumer_settings()}
            response = JsonResponse(settings)
            if not c:
                response.status_code = 400
        except json.JSONDecodeError:
            response.status_code = 400
    elif request.method == 'GET':
        settings = {'settings': consumers.get_consumer_settings()}
        response = JsonResponse(settings)
    elif request.method == 'DELETE':
        cid = QueryDict(request.body)['id']
        consumers.delete_consumer(cid)
        settings = {'settings': consumers.get_consumer_settings()}
        response = JsonResponse(settings)
        if cid in settings['settings']:
            response.status_code = 405
    else:
        response.status_code = 405
    return response


@api_view(['GET', 'POST', 'DELETE'])
# @authentication_classes((SessionAuthentication, BasicAuthentication,))
# @permission_classes((IsAuthenticated,))
def states(request):
    consumers = _init_consumers()
    response = HttpResponse(status=405)
    _init_consumers()
    if request.method == 'GET':
        states = {'states': list(consumers.get_states())}
        response = JsonResponse(states)
    elif request.method == 'DELETE':
        consumers.clear_states()
        states = {'states': list(consumers.get_states())}
        response = JsonResponse(states)
    elif request.method == 'POST':
        status = 200
        try:
            data = json.loads(request.body.decode('utf-8'))
            state = data.get('id', None)
            if state is not None:
                consumers.add_state(state)
            else:
                status = 400
        except (AttributeError, json.JSONDecodeError, ValueError, TypeError, StopIteration):
            status = 400
        states = {'states': list(consumers.get_states())}
        response = JsonResponse(states, status=status)
    return response


@api_view(['GET', 'POST', 'DELETE'])
# @authentication_classes((SessionAuthentication, BasicAuthentication,))
# @permission_classes((IsAuthenticated,))
def bandwidth(request):
    consumers = _init_consumers()
    response = HttpResponse(status=405)
    if request.method == 'GET':
        bw = consumers.get_bw()
        response = JsonResponse({'bw': bw})
    elif request.method == 'DELETE':
        consumers.push_bw(0)
        consumers.push_bw(0)
        bw = consumers.get_bw()
        response = JsonResponse({'bw': bw})
    elif request.method == 'POST':
        try:
            b = int(next(iter(request.POST.keys())))
            consumers.push_bw(b)
            bw = consumers.get_bw()
            response = JsonResponse({'bw': bw})
        except (AttributeError, ValueError, TypeError, StopIteration):
            response = HttpResponse(status=400)
    return response


@api_view(['GET', 'POST', 'DELETE'])
# @authentication_classes((SessionAuthentication, BasicAuthentication,))
# @permission_classes((IsAuthenticated,))
def service_activate(request):
    print('TRIGGER TRU WAKEUP', flush=True)
    consumers = _init_consumers()
    consumers.clear_states()
    warrior = _init_warrior()
    warrior.trigger_wakeup()
    consumers.add_state(1)
    return JsonResponse({'status': warrior.status})


@api_view(['GET', 'POST', 'DELETE'])
# @authentication_classes((SessionAuthentication, BasicAuthentication,))
# @permission_classes((IsAuthenticated,))
def service_deactivate(request):
    print('TRIGGER TRU NAPTIME', flush=True)
    consumers = _init_consumers()
    consumers.clear_states()
    warrior = _init_warrior()
    warrior.trigger_naptime()
    return JsonResponse({'status': warrior.status})


@api_view(['GET', 'POST', 'DELETE'])
# @authentication_classes((SessionAuthentication, BasicAuthentication,))
# @permission_classes((IsAuthenticated,))
def service_status(request):
    warrior = _init_warrior()
    return JsonResponse({'status': warrior.status})


@api_view(['GET', 'POST', 'DELETE'])
# @authentication_classes((SessionAuthentication, BasicAuthentication,))
# @permission_classes((IsAuthenticated,))
def tru_device_settings(request):
    print('TRU_WAKEUP_SETTINGS', flush=True)
    warrior = _init_warrior()
    if request.method == 'GET':
        txt = warrior.get_settings_file()
        return HttpResponse(txt)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            data = {}
        target_cpe_system = data.get('target_cpe_system', {})
        target_system = data.get('target_system', {})
        via_system = data.get('via_system', {})
        warrior.generate_system_data(target_system, target_cpe_system, via_system)
        return JsonResponse({'status': 'See logs'})

