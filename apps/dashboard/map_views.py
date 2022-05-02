import json
import os
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from apps.dashboard.scripts.build_cashew_map import full_map

# For dev env
if not os.path.exists("staticfiles/cashew_map_en.html") and not os.path.exists("staticfiles/cashew_map_fr.html"):
    cashew_map_html_en = full_map("en")
    cashew_map_html_fr = full_map("fr")
else:
    pass

# For prod env
#cashew_map_html_en = full_map("en")
#cashew_map_html_fr = full_map("fr")

scheduler = BackgroundScheduler()


""" Prod env
@scheduler.scheduled_job(IntervalTrigger(days=1))
def update_cashew_map():
    global cashew_map_html_en
    cashew_map_html_en = full_map("en")
    global cashew_map_html_fr
    cashew_map_html_fr = full_map("fr")


scheduler.start()
"""

@login_required(login_url="/")
def index(request):
    start_time = time.time()
    filename = "staticfiles/cashew_map_en.html"
    cashew_map = None
    path_link = request.build_absolute_uri(request.path)

    if "/fr/" in path_link.__str__():
        filename = "staticfiles/cashew_map_fr.html"
        # For prod env
        #cashew_map = cashew_map_html_fr
    elif "/en/" in path_link.__str__():
        filename = "staticfiles/cashew_map_en.html"
        # For prod env
        #cashew_map = cashew_map_html_en

    if cashew_map is None:
        with open(filename, errors="ignore") as f:
            cashew_map = f.read()

    context = {"map": json.dumps(cashew_map), "segment": "map"}
    html_template = loader.get_template("dashboard/index.html")
    render = html_template.render(context, request)
    print("TOTAL LOADING TIME--- %s seconds ---" % (time.time() - start_time))
    return HttpResponse(render)
