import logging
import threading
import time
from multiprocessing import Process

from django.http import HttpResponse
from django.shortcuts import render

from cdr_controller.filters.template_0 import template_0_main
from cdr_controller.filters.template_01 import template_1_main
# from cdr_controller.filters.template_02 import template_2_main
from cdr_controller.filters.template_03 import template_3_main
from cdr_controller.filters.template_05 import template_05_main
from . import data_generator

data_generator_exit_flag = 0
logger = logging.getLogger(__name__)
logging.getLogger("py4j").setLevel(logging.ERROR)


class dataGenThread(threading.Thread):
    def __init__(self, pick_type_distribution, rate_type_distribution,
                 pick_call_distribution, delta_distribution,
                 rate_place_distribution):
        threading.Thread.__init__(self)
        self.pick_type_distribution = pick_type_distribution
        self.rate_type_distribution = rate_type_distribution
        self.pick_call_distribution = pick_call_distribution
        self.delta_distribution = delta_distribution
        self.rate_place_distribution = rate_place_distribution

    def run(self):
        global data_generator_exit_flag
        while (1):
            if data_generator_exit_flag:
                exit(0)
            data_generator.people(
                pick_type_distribution=self.pick_type_distribution,
                rate_type_distribution=self.rate_type_distribution,
                pick_call_distribution=self.pick_call_distribution,
                delta_distribution=self.delta_distribution,
                rate_place_distribution=self.rate_place_distribution)


thread0 = dataGenThread(pick_type_distribution='default',
                        rate_type_distribution=0.3,
                        pick_call_distribution='default',
                        delta_distribution='default',
                        rate_place_distribution=0.7)

p0 = Process(target = template_0_main)
p1 = Process(target = template_1_main)
#p2 = Process(target = template_2_main)
p3 = Process(target = template_3_main)
p5 = Process(target = template_05_main)
template_pool = [p0, p1, p3, p5]


def hello_world(request):
    return render(request, 'hello_world.html', {})


def homepage(request):
    return render(request, 'homepage.html', {})


def index(request):
    global thread0
    if not thread0.isAlive():
        return render(request, 'homepage.html', {})
    return render(request, 'index.html', {})


def workload_generator(request):
    global thread0, template_pool
    if not thread0.isAlive():
        return render(request, 'homepage.html', {})
    if request.method == 'POST':
        data_gen_stop(request)
        pick_type_distribution = request.POST['pick_type_distribution']
        rate_type_distribution = float(request.POST['rate_type_distribution'])
        pick_call_distribution = request.POST['pick_call_distribution']
        delta_distribution = request.POST['delta_distribution']
        rate_place_distribution = float(request.POST['rate_place_distribution'])

        logger.info("Start updating workload generator ... ")
        thread0 = dataGenThread(
            pick_type_distribution=pick_type_distribution,
            rate_type_distribution=rate_type_distribution,
            pick_call_distribution=pick_call_distribution,
            delta_distribution=delta_distribution,
            rate_place_distribution=rate_place_distribution)
        thread0.start()

        # Start templates process
        for p in template_pool:
            p.start()
        logger.info("Update workload generator successfully! ")
    elif request.method == 'GET':
        pass
    return render(request, 'workload_generator.html', {})


def show_info(request):
    html = '<div>' + "request method: " + request.method + '</div>'
    html += '<div>' + "request.GET: " + str(dict(request.GET)) + '</div>'
    html += '<div>' + "request.POST: " + str(dict(request.POST)) + '</div>'
    html += '<div>' + "request.COOKIES: " + str(request.COOKIES) + '</div>'
    html += '<div>' + "request.scheme: " + request.scheme + '</div>'
    html += '<div>' + "request.META['REMOTE_ADDR']: " + str(
        request.META['REMOTE_ADDR']) + '</div>'
    html += '<div>' + "request.META:" + str(request.META) + '</div>'
    return HttpResponse(html)


def data_gen_start(request):
    global data_generator_exit_flag
    global thread0
    thread0 = dataGenThread(pick_type_distribution='default',
                            rate_type_distribution=0.3,
                            pick_call_distribution='default',
                            delta_distribution='default',
                            rate_place_distribution=0.7)
    data_generator_exit_flag = 0
    thread0.start()
    logger.info("Start data generator")
    p0.start()
    p1.start()
    # p2.start()
    p3.start()
    p5.start()
    return HttpResponse('Success')


def data_gen_stop(request):
    global data_generator_exit_flag
    global thread0, p0, p1, p3, p5 #, p2

    # restart template process
    p0.terminate()
    p1.terminate()
    # p2.terminate()
    p3.terminate()
    p5.terminate()
    p0 = Process(target=template_0_main)
    p1 = Process(target = template_1_main)
    #p2 = Process(target = template_2_main)
    p3 = Process(target = template_3_main)
    p5 = Process(target = template_05_main)
    data_generator_exit_flag = 1
    while (thread0.isAlive()):
        time.sleep(0.01)
        print('thread alive')
    logger.info('thread killed')
    return HttpResponse('Try to stop')
