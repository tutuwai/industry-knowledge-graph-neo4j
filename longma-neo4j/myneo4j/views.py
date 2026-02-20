import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .pyneo_utils import *


# Create your views here.
@login_required
def index(request):
    try:
        start = request.GET.get("start", "")
        relation = request.GET.get("relation", "")
        end = request.GET.get("end", "")
        all_datas = get_all_relation(start, relation, end)
        links = json.dumps(all_datas["links"])
        datas = json.dumps(all_datas["datas"])
        categories = json.dumps(all_datas["categories"])
        legend_data = json.dumps(all_datas["legend_data"])

        print(categories)
        print(legend_data)
    except Exception as e:
        print(e)
    return render(request, "index.html", locals())


@login_required
def tree(request):
    return render(request, "tree.html", locals())
