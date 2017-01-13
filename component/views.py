from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

from django.conf import settings

from itertools import groupby
import json
from collections import OrderedDict
from kobotoolbox import get_household_analysis_data

from .forms import KMLUpload
from .kmlparser import KMLParser
from .models import Metadata, Component
from master.models import Slum

#@staff_member_required
def kml_upload(request):
    if request.method == 'POST':
        form = KMLUpload(request.POST or None,request.FILES)
        if form.is_valid():
            docFile = request.FILES['kml_file'].read()
            print form.cleaned_data
            objKML = KMLParser(docFile, form.cleaned_data['slum_name'])
            messages.success(request,'Form submission successful')
    else:
        form = KMLUpload()
    return render(request, 'kml_upload.html', {'form': form})

#@user_passes_test(lambda u: u.is_superuser)
def get_component(request, slum_id):
    slum = get_object_or_404(Slum, pk=slum_id)
    metadata = Metadata.objects.filter(visible=True)
    rhs_analysis = {}
    try:
        #Fetch RHS data from kobotoolbox
        fields_code = metadata.filter(type='F').values_list('code')
        fields = map(lambda x: x[0].split(':')[0],set(fields_code))
        rhs_analysis = get_household_analysis_data(slum.shelter_slum_code, fields)
    except:
        pass
    print rhs_analysis
    lstcomponent = []
    for metad in metadata:
        component = {}
        component['name'] = metad.name
        component['level'] = metad.level
        component['section'] = metad.section.name
        component['section_order'] = metad.section.order
        component['type'] = metad.type
        component['order'] = metad.order
        component['blob'] = metad.blob
        component['child'] = []
        if metad.type == 'C':
            for comp in metad.component_set.filter(slum=slum):
                component['child'].append({'housenumber':comp.housenumber, 'shape':json.loads(comp.shape.json)})
        elif metad.type == 'F':
            if metad.code != "":
                field = metad.code.split(':')
                if field[0] in rhs_analysis and field[1] in rhs_analysis[field[0]]:
                    component['child'] = rhs_analysis[field[0]][field[1]]
            else:
                if metad.name in settings.SPONSOR and slum_id == '288':
                    component['child'] = settings.SPONSOR[metad.name]
        if len(component['child']) > 0:
            lstcomponent.append(component)
    lstcomponent = sorted(lstcomponent, key=lambda x:x['section_order'])
    dtcomponent = OrderedDict()
    for key, comp in  groupby(lstcomponent, key=lambda x:x['section']):
        if key not in dtcomponent:
            dtcomponent[key] = {}
        for c in comp:
            dtcomponent[key][c['name']] = c
    return HttpResponse(json.dumps(dtcomponent),content_type='application/json')

def get_kobo_FF_data(request, slum_id):
   pass


def get_kobo_data(request, slum_id):
   pass


