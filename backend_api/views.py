import json
import random
from backend_api.models import *

from django.http import HttpResponse, Http404, JsonResponse

from backend_api.DBdriver import *

from backend_api.models import *
from django.shortcuts import get_object_or_404
from collections import defaultdict

# Create your views here.
def handle(request):
    return HttpResponse("Home Page")


def BNYBackEndPost(request):
    if request.method != 'POST' or not request.POST.get('JsonData'):
        raise Http404
    jsonString = request.POST['JsonData']
    jsonObj = json.loads(jsonString)
    # {'source': 's1name', 'destination': 's2name', 'fields': ['fname1', 'fname2']}
    # print(jsonObj)
    handleJson(jsonObj)
    return HttpResponse(status=200)

def fileUpload(request):
    if request.method != 'POST' or 'csv_file' not in request.FILES:
        raise Http404
    csv_file = request.FILES['csv_file']
    if not csv_file.name.endswith('.csv'):
        raise Http404
    file_data = csv_file.read().decode("utf-8") 
    lines = file_data.split("\n")
    for line in lines:
        cols = line.strip().split(',')
        if len(cols) < 2: continue
        jsonObj = {}
        jsonObj['source'] = cols[0]
        jsonObj['destination'] = cols[1]
        jsonObj['fields'] = list()
        for i in range(2, len(cols)):
            jsonObj['fields'].append(cols[i])
        handleJson(jsonObj)
    return HttpResponse()


def getOverlaps(request):
    result = {}
    overlaps = []
    for dest in Relationship.objects.values_list("toSystem_id",flat=True).distinct():
        destName = get_object_or_404(System, id=dest).name
        sources = Relationship.objects.filter(toSystem_id=dest)

        for i in range(len(sources)):
            # print (sources[i].fromSystem.name)
            # fields involves message from i to dest
            relation1 =get_object_or_404(Relationship, toSystem_id=dest, fromSystem_id=sources[i].fromSystem.id)
            # print (relation1.attributes.all())
            for j in range(i + 1, len(sources)):
                # fields involves message from j to dest
                relation2 = get_object_or_404(Relationship, toSystem_id=dest, fromSystem_id=sources[j].fromSystem.id)
                # find intersect if any
                intersect = list(set(relation1.attributes.all()) & set(relation2.attributes.all()))

                # if intersect detected
                if len(intersect) > 0:
                    for field in intersect:
                        innerObj = {}
                        innerObj['field'] = field.name
                        innerObj['dest'] = destName
                        innerObj['sources'] = sources[i].fromSystem.name
                        overlaps.append(innerObj)
                        innerObj = {}
                        innerObj['field'] = field.name
                        innerObj['dest'] = destName
                        innerObj['sources'] = sources[j].fromSystem.name
                        overlaps.append(innerObj)
    result['overlaps'] = overlaps    
    return JsonResponse(result, status=200)

""" 
def getOverlaps(request):
    result = {}
    result['overlaps'] = []
    # for every target system
    for dest in Relationship.objects.values_list("toSystem_id",flat=True).distinct():
        obj = {}
        obj['dest'] = get_object_or_404(System, id=dest).name
        #
        obj['overlap'] = []
        # find all the source systems whose destination is dest
        sources = Relationship.objects.filter(toSystem_id=dest)

        for i in range(len(sources)):
            # print (sources[i].fromSystem.name)
            # fields involves message from i to dest
            relation1 =get_object_or_404(Relationship, toSystem_id=dest, fromSystem_id=sources[i].fromSystem.id)
            # print (relation1.attributes.all())
            for j in range(i + 1, len(sources)):
                # fields involves message from j to dest
                relation2 = get_object_or_404(Relationship, toSystem_id=dest, fromSystem_id=sources[j].fromSystem.id)
                # find intersect if any
                intersect = list(set(relation1.attributes.all()) & set(relation2.attributes.all()))

                # if intersect detected
                if len(intersect) > 0:
                    for field in intersect:
                        innerObj = {}
                        innerObj['field'] = field.name
                        innerObj['sources'] = [sources[i].fromSystem.name, sources[j].fromSystem.name]
                        obj['overlap'].append(innerObj)

                        # print(dest.fromSystem.name + ' -> ' + dest.toSystem.name)
        result['overlaps'].append(obj)
    return JsonResponse(result, status=200) """


def getModels(request):
    result = {}
    systems = []
    result['systems'] = systems
    seen = set()
    if not System.objects.all():
        return JsonResponse(result, status=400)

    for system in System.objects.all():
        obj = {}
        innerObj = {}
        innerObj['id'] = system.name
        innerObj['color'] = system.color
        obj['data'] = innerObj
        obj['type'] = "node"
        systems.append(obj)
        print (system.attributes)
    for relation in Relationship.objects.all():
        innerObj = {}
        innerObj['source'] = relation.fromSystem.name
        innerObj['target'] = relation.toSystem.name
        innerObj['id'] = innerObj['source'] + innerObj['target']
        obj = {}
        obj['data'] = innerObj
        obj['type'] = "edge"
        systems.append(obj)

    return JsonResponse(result, status=200)

def manualProcessNode(request):
    if request.method != 'POST' or not request.POST.get('nodeName') or not request.POST.get('action'):
        return HttpResponse(status=403)
    # user adds a new node to system
    nodeName = request.POST.get('nodeName')
    print (nodeName)
    if request.POST.get('action') == 'add':
        system = System.objects.filter(name=nodeName)

        # system = get_object_or_404(System, name=nodeName)
        # system does not existed, create a new one and savew
        if not system or len(system) == 0:
            newSystem = System(name=nodeName)
            newSystem.save()
            return HttpResponse(status=200)
        else:
            # try to add an existed node, return 404
            return HttpResponse(status=403)

    if request.POST.get('action') == 'remove':
        system = System.objects.filter(name=nodeName)
        # system does existed, delete and save
        if system and len(system) > 0:
            # newSystem = System(name=nodeName)
            system[0].delete()
            return HttpResponse(status=200)
        else:
            # try to remove a non-existed node, return 404
            return HttpResponse(status=403)
    # for any unexpected error, return 404
    return HttpResponse(status=403)


def manualProcessEdge(request):
    if request.method != 'POST' or not request.POST.get('source') or not request.POST.get('destination') or not request.POST.get('action'):
        return HttpResponse(status=403)

    source = request.POST.get('source')
    dest = request.POST.get('destination')

    sourceSystem = System.objects.filter(name=source)
    destSystem = System.objects.filter(name=dest)


    if not sourceSystem or len(sourceSystem) == 0 or not destSystem or len(destSystem) == 0:
        # try to deal with systems don't exist
        return HttpResponse(status=403)

    relationship = Relationship.objects.filter(fromSystem_id=sourceSystem[0], toSystem_id=destSystem[0])


    if request.POST.get('action') == 'add':
        if relationship or len(relationship) > 0:
            # there is none relationship between source and dest
            return HttpResponse(status=403)
        newR = Relationship(fromSystem=sourceSystem[0], toSystem=destSystem[0])
        newR.save()
        return HttpResponse(status=200)
    if request.POST.get('action') == 'remove':
        if not relationship:
            return HttpResponse(status=403)
        
        relationship[0].delete()
        return HttpResponse(status=200)

def getColorCode():
    r = lambda: random.randint(0, 255)
    return ('#%02X%02X%02X' % (r(), r(), r()))