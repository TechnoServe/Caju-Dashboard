import collections
import json
import locale
import time

import ee
import folium
import geojson
from django import template
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views import generic
from folium import plugins
from folium.plugins import MarkerCluster

import apps.dashboard.scripts.get_qar_information as qar
from apps.authentication import utils
from apps.authentication.models import RemOrganization, RemRole, RemUser
from apps.authentication.forms import RegisterOrganization
from apps.dashboard import models
from apps.dashboard.benin_commune import add_benin_commune
from apps.dashboard.benin_department import add_benin_department
from apps.dashboard.benin_plantations import add_benin_plantation
from apps.dashboard.benin_republic import add_benin_republic
from apps.dashboard.models import Plantation
from apps.dashboard.nursery_information import NurseryLayer
from .db_conn_string import cur
from apps.dashboard.qar_informations import QarLayer
from .forms import UserCustomProfileForm, UserBaseProfileForm, KorDateForm, Department_choice

# Google service account for the GEE geotiff
service_account = 'cajulab@benin-cajulab-web-application.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'privatekey.json')
ee.Initialize(credentials)
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'
# alldept = ee.Image('users/ashamba/allDepartments_v0')
alldept = ee.Image('users/cajusupport/allDepartments_v1')


class MyHome:

    def __init__(self):
        self.Qars = None
        print('')
        self.figure = folium.Figure()

    def get_base_map(self):
        cashew_map = None
        try:
            # Basemap dictionary
            basemaps = {
                'Google Maps': folium.TileLayer(
                    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                    attr=gettext('Google'),
                    name='Maps',
                    max_zoom=25,
                    overlay=True,
                    control=False
                ),
                'Google Satellite': folium.TileLayer(
                    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                    attr='Google',
                    name=gettext('Google Satellite'),
                    max_zoom=25,
                    overlay=True,
                    show=False,
                    control=True
                ),
                'Mapbox Satellite': folium.TileLayer(
                    tiles='https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{'
                          'y}.png?access_token=pk.eyJ1Ijoic2hha2F6IiwiYSI6ImNrczMzNTl3ejB6eTYydnBlNzR0dHUwcnUifQ'
                          '.vHqPio3Pe0PehWpIuf5QUg',
                    attr='Mapbox',
                    name=gettext('Mapbox Satellite'),
                    max_zoom=25,
                    overlay=True,
                    show=False,
                    control=True
                )
            }

            # Initialize map object

            cashew_map = folium.Map(
                location=[9.0, 2.4],
                zoom_start=8,
                prefer_canvas=True,
                tiles=None
            )

            cashew_map.add_child(basemaps['Google Maps'])
            cashew_map.add_child(basemaps['Google Satellite'])
            cashew_map.add_child(basemaps['Mapbox Satellite'])

            plugins.Fullscreen(
                position='topright',
                title='Full Screen',
                title_cancel='Exit Full Screen',
                force_separate_button=False
            ).add_to(cashew_map)

            # Adding the nursery layer from the class Nursery_LAYER
            marker_cluster = MarkerCluster(name=gettext("Nursery Information"))
            Nursery_layer = NurseryLayer(marker_cluster).add_nursery()
            Nursery_layer.add_to(cashew_map)

            print('')
            print('Define a method for displaying Earth Engine image tiles on a folium map.')
            start_time = time.time()

            def add_ee_layer(self, ee_image_object, vis_params, name):
                map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
                folium.raster_layers.TileLayer(
                    tiles=map_id_dict['tile_fetcher'].url_format,
                    attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
                    name=name,
                    overlay=True,
                    control=True
                ).add_to(self)

            folium.Map.add_ee_layer = add_ee_layer
            folium.map.FeatureGroup.add_ee_layer = add_ee_layer
            zones = alldept.eq(1)
            zones = zones.updateMask(zones.neq(0))
            cashew_map.add_ee_layer(zones, {'palette': "red"}, gettext('Satellite Prediction'))
            print("--- %s seconds ---" % (time.time() - start_time))

            print('')
            print('The no boundary layer to remove shapefiles on the Benin region')
            start_time = time.time()
            No_Boundary_layer = folium.FeatureGroup(name=gettext('No Boundary'), show=False, overlay=False)
            No_Boundary_layer.add_to(cashew_map)
            print("--- %s seconds ---" % (time.time() - start_time))

        except Exception as e:
            pass

        return cashew_map

    def get_context_data(self, path_link, cashew_map, **kwargs):
        try:

            print('...Getting database QAR...')
            start_time = time.time()
            self.Qars = qar.get_qar_data_from_db()
            # Adding the qar layer from the class QarLayer
            marker_cluster = MarkerCluster(name=gettext("QAR Information"))
            qarLayer = QarLayer(marker_cluster, self.Qars).add_qar()
            qarLayer.add_to(cashew_map)
            print("--- %s seconds ---" % (time.time() - start_time))

            print('')
            print('Adding the shapefiles with popups for the Benin Republic region')
            start_time = time.time()
            Benin_layer = add_benin_republic(self.Qars)
            Benin_layer.add_to(cashew_map)
            print("--- %s seconds ---" % (time.time() - start_time))

            print('')
            print('Adding the shapefiles with popups for the Benin departments region')
            start_time = time.time()
            Benin_dept_layer, dept_yieldHa = add_benin_department(self.Qars)
            Benin_dept_layer.add_to(cashew_map)
            print("--- %s seconds ---" % (time.time() - start_time))

            print('')
            print('Adding the shapefiles with popups for the Benin commune region')
            start_time = time.time()
            Benin_commune_layer = add_benin_commune(self.Qars)
            Benin_commune_layer.add_to(cashew_map)
            print("--- %s seconds ---" % (time.time() - start_time))

            print('')
            print('Adding the shapefiles with popups for the Benin plantations')
            start_time = time.time()
            Benin_plantation_layer = add_benin_plantation(path_link, dept_yieldHa)
            Benin_plantation_layer.add_to(cashew_map)
            print("--- %s seconds ---" % (time.time() - start_time))

        except Exception as e:
            print(e)
            pass

        return cashew_map


@login_required(login_url="/")
def index(request):
    path_link = request.path
    home_obj = MyHome()
    cashew_map = home_obj.get_base_map()

    # adding folium layer control for the previously added shapefiles
    cashew_map.add_child(folium.LayerControl())
    cashew_map = cashew_map._repr_html_()

    context = {'map': cashew_map, 'segment': 'map'}
    html_template = loader.get_template('dashboard/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/")
def full_map(request):
    path_link = request.path
    home_obj = MyHome()
    cashew_map = home_obj.get_base_map()
    cashew_map = home_obj.get_context_data(path_link, cashew_map)

    # adding folium layer control for the previously added shapefiles
    cashew_map.add_child(folium.LayerControl())
    cashew_map = cashew_map._repr_html_()
    data = {'map': cashew_map, 'segment': 'map'}

    return HttpResponse(
        json.dumps(data),
        content_type='application/javascript; charset=utf8'
    )


@login_required(login_url="/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('dashboard/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        html_template = loader.get_template('dashboard/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/")
def register_org(request):
    msg = None
    success = False

    if request.method == "POST":
        form = RegisterOrganization(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                current_user = request.user
                if current_user.is_authenticated:
                    # Do something for authenticated users.
                    obj.created_by = current_user.id
                    obj.created_date = datetime.datetime.now()
                    obj.updated_by = current_user.id
                    obj.updated_date = datetime.datetime.now()

                    # return redirect("/login/")
            except Exception as e:
                print("")

            obj.save()
            msg = gettext('Organization created - please <a href="/register">register user</a>.')
            success = True

        else:
            msg = gettext('Form is not valid')
    else:
        form = RegisterOrganization()

    return render(request, "authentication/register_org.html", {"form": form, "msg": msg, "success": success})


@login_required(login_url="/")
def register_role(request):
    msg = None
    success = False

    if request.method == "POST":
        form = RegisterRole(request.POST)
        if form.is_valid():
            org_name = form.cleaned_data.get("organization_")
            print(org_name)
            current_user = request.user
            if current_user.is_authenticated:
                # Do something for authenticated users.
                obj = form.save(commit=False)

                org_name = form.cleaned_data.get("organization_")
                # print(org_name)

                # logger.info("The value of org name is %s", org_name)

                # org = RemOrganization.objects.filter(id = org_name)[0]
                obj.organization = org_name
                obj.created_by = current_user.id
                obj.created_date = datetime.datetime.now()
                obj.updated_by = current_user.id
                obj.updated_date = datetime.datetime.now()
                obj.save()

                msg = 'Role added - please <a href="/register">register user</a>.'
                success = True

                # return redirect("/login/")
            else:
                # Do something for anonymous users.
                msg = 'Role not added - please <a href="/register_role">try againh</a>.'
                success = False

        else:
            msg = gettext('Form is not valid')
    else:
        form = RegisterRole()

    return render(request, "authentication/register_role.html", {"form": form, "msg": msg, "success": success})


@login_required(login_url="/")
def load_roles(request):
    org_id = request.GET.get('organization_name')
    roles = RemRole.objects.filter(organization=org_id)
    return render(request, 'authentication/role_options.html', {'roles': roles})


@method_decorator(login_required, name='dispatch')
class EditProfilePageView(generic.UpdateView):
    form_class = UserCustomProfileForm
    template_name = 'dashboard/profile.html'
    success_url = reverse_lazy('map')

    def form_invalid(self, form):
        print(form.errors)
        if self.request.accepts('text/html'):
            return super(EditProfilePageView, self).form_invalid(form)
        else:
            return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        print(form.errors)
        return super(EditProfilePageView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(EditProfilePageView, self).get_context_data(**kwargs)
        context['segment'] = 'profile'
        return context

    def get_object(self, queryset=None):
        print(self)
        return self.request.user


@login_required
def profile(request):
    msg = None
    success = False
    RemUser.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserBaseProfileForm(request.POST, instance=request.user)
        profile_form = UserCustomProfileForm(request.POST, request.FILES, instance=request.user.remuser)

        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect('map')
        else:
            print(form.errors)
            print(profile_form.errors)
            msg = gettext('Form is not valid')
    else:
        form = UserBaseProfileForm(instance=request.user)
        profile_form = UserCustomProfileForm(instance=request.user.remuser)

    args = {'form': form, 'profile_form': profile_form, "msg": msg, "success": success}
    args['segment'] = 'profile'
    # args.update(csrf(request))
    return render(request, 'dashboard/profile.html', args)


@login_required(login_url="/")
def tables(request):
    context = {}
    companies = RemOrganization.objects.all()
    org_count = int(companies.count() / 10)

    plantations = Plantation.objects.all()
    plantation_count = int(plantations.count() / 10)

    context['companies'] = companies
    context['org_count'] = range(1, org_count)
    context['org_count'] = range(1, org_count)
    context['plantation_count'] = range(1, plantation_count)
    context['segment'] = 'tables'
    return render(request, 'dashboard/companies.html', context)


@login_required(login_url="/")
def yields(request):
    context = {}
    yields_list = models.BeninYield.objects.filter(status=utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(yields_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        yields = paginator.page(page)
    except PageNotAnInteger:
        yields = paginator.page(1)
    except EmptyPage:
        yields = paginator.page(paginator.num_pages)

    context['yields'] = yields
    context['segment'] = 'yield'
    context['page_range'] = page_range
    return render(request, 'dashboard/yield.html', context)


@login_required(login_url="/")
def plantations(request):
    context = {}
    plantations_list = models.Plantation.objects.filter(status=utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(plantations_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        plantations = paginator.page(page)
    except PageNotAnInteger:
        plantations = paginator.page(1)
    except EmptyPage:
        plantations = paginator.page(paginator.num_pages)

    context['plantations'] = plantations
    context['segment'] = 'plantations'
    context['page_range'] = page_range

    return render(request, 'dashboard/plantations.html', context)


@login_required(login_url="/")
def nurseries(request):
    context = {}
    nurseries_list = models.Nursery.objects.filter(status=utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(nurseries_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        nurseries = paginator.page(page)
    except PageNotAnInteger:
        nurseries = paginator.page(1)
    except EmptyPage:
        nurseries = paginator.page(paginator.num_pages)

    context['nurseries'] = nurseries
    context['segment'] = 'nurseries'
    context['page_range'] = page_range
    return render(request, 'dashboard/nurseries.html', context)


@login_required(login_url="/")
def shipment(request):
    context = {}
    nurseries_list = models.Nursery.objects.filter(status=utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(nurseries_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        nurseries = paginator.page(page)
    except PageNotAnInteger:
        nurseries = paginator.page(1)
    except EmptyPage:
        nurseries = paginator.page(paginator.num_pages)

    context['nurseries'] = nurseries
    context['segment'] = 'shipment'
    context['page_range'] = page_range
    return render(request, 'dashboard/shipment.html', context)

@login_required(login_url="/")
def analytics(request):
    context = {}

    country = "Benin"
    query = ("SELECT kor,location_region,location_country FROM free_qar_result WHERE location_country=%s")
    cur.execute(query, (country,))

    infos = []
    for kor in cur:
        for location_region in cur:
            infos.append(location_region)

    infos1 = sorted(infos, key=lambda name: name[1])

    names_with_duplicate = []
    for x in infos1:
        names_with_duplicate.append(x[1])

    y = 0
    while len(names_with_duplicate) > y:
        if "Department" in names_with_duplicate[y]:
            names_with_duplicate[y] = names_with_duplicate[y].replace(" Department", "")
        else:
            pass
        y += 1

    names_sorted = list(set(names_with_duplicate))
    names_sorted = sorted(names_sorted)

    occurence1 = collections.Counter(names_with_duplicate)
    occurence2 = occurence1.items()
    occurence2 = list(occurence2)

    names_init = {}
    for x in names_sorted:
        names_init[x] = 0

    for info in infos:
        for name in names_init:
            if name == info[1] or name + " Department" == info[1]:
                names_init[name] += round(info[0])

    for occur in occurence2:
        for name in names_init:
            if name == occur[0]:
                names_init[name] /= occur[1]

    department_sum_list0 = names_init.items()
    department_sum_list0 = list(department_sum_list0)
    department_sum_list0 = sorted(department_sum_list0, reverse=True, key=lambda kor_: kor_[1])

    department_sum_list = []
    for x in department_sum_list0:
        department_sum_list.append(x[1])

    department_names = []
    for x in department_sum_list0:
        department_names.append(x[0])

    query = ("SELECT kor, location_sub_region, location_country FROM free_qar_result WHERE location_country=%s")
    cur.execute(query, (country,))

    infos_commune = []
    for kor in cur:
        for location_sub_region in cur:
            infos_commune.append(location_sub_region)

    infos_commune_1 = sorted(infos_commune, key=lambda name: name[1])

    commune_names_with_duplicate = []
    for x in infos_commune_1:
        commune_names_with_duplicate.append(x[1])

    occurence0 = collections.Counter(commune_names_with_duplicate)
    occurence = occurence0.items()
    occurence = list(occurence)

    commune_names = list(set(commune_names_with_duplicate))
    commune_names_sorted = sorted(commune_names)

    commune_names_init = {}
    for x in commune_names_sorted:
        commune_names_init[x] = 0

    for info in infos_commune:
        for name in commune_names_init:
            if name == info[1]:
                commune_names_init[name] += round(info[0])

    for occur in occurence:
        for name in commune_names_init:
            if name == occur[0]:
                commune_names_init[name] /= occur[1]

    commune_sum_list = commune_names_init.items()
    commune_sum_list = list(commune_sum_list)

    commune_names = []
    for x in commune_sum_list:
        commune_names.append(x[0])

    if request.method == "POST":
        form = KorDateForm(data=request.POST or None)
        form1 = Department_choice(data=request.POST or None)
        dep_commune_sum_list = []
        dep_commune_names = []
        per_kor = []
        kor_time = []
        if form1.is_valid():
            department_names_ = form1.cleaned_data.get("department")
            department_with_department = department_names_.capitalize()+" Department"

            query = ("SELECT kor, location_sub_region, location_region, location_country FROM free_qar_result WHERE location_country=%s AND location_region=%s OR location_region=%s")
            cur.execute(query, (country, department_names_, department_with_department))

            dep_commune = []
            for kor in cur:
                for location_sub_region in cur:
                    dep_commune.append(location_sub_region)

            dep_commune = sorted(dep_commune, key=lambda name: name[1])

            dep_commune_with_duplicate = []
            for x in dep_commune:
                dep_commune_with_duplicate.append(x[1])

            dep_comm_occurence = collections.Counter(dep_commune_with_duplicate)
            dep_comm_occurence0 = dep_comm_occurence.items()
            dep_comm_occurence0 = list(dep_comm_occurence0)

            dep_commune_names = list(set(dep_commune_with_duplicate))
            dep_commune_sorted = sorted(dep_commune_names)

            dep_commune_init = {}
            for x in dep_commune_sorted:
                dep_commune_init[x] = 0

            for info in dep_commune:
                for name in dep_commune_init:
                    if name == info[1]:
                        dep_commune_init[name] += round(info[0])

            for occur in dep_comm_occurence0:
                for name in dep_commune_init:
                    if name == occur[0]:
                        dep_commune_init[name] /= occur[1]

            dep_commune_sum_list0 = dep_commune_init.items()
            dep_commune_sum_list0 = list(dep_commune_sum_list0)

            dep_commune_sum_list = []
            for x in dep_commune_sum_list0:
                dep_commune_sum_list.append(x[1])

            for comm_name in dep_commune_sum_list0:
                dep_commune_names.append(comm_name[0])
            dep_commune_names = list(set(dep_commune_names))
            dep_commune_names = sorted(dep_commune_names)

        if form.is_valid():
            date1 = form.cleaned_data.get("my_date_field")
            date1 = str(date1)
            date1 = date1.replace("-", "/")
            date2 = form.cleaned_data.get("my_date_field1")
            date2 = str(date2)
            date2 = date2.replace("-", "/")
            time_duration = int(str(date1[5])+str(date1[6]))

            date1 = date1 + " 00:00:00"
            date2 = date2 + " 23:59:59"

            query = ("SELECT kor, location_country, created_at FROM free_qar_result WHERE location_country=%s AND created_at BETWEEN %s AND %s")
            cur.execute(query, (country, date1, date2))
            lite = []
            for kor in cur:
                lite.append(kor)
            lite = sorted(lite, key=lambda kor_: kor_[2])

            for x in lite:
                per_kor.append(x[0])

            for x in lite:
                kor_time.append(x[2].strftime("%m/%d/%Y"))

    else:
        form = KorDateForm()
        form1 = Department_choice()
        dep_commune_sum_list = []
        dep_commune_names = []
        kor_time = []
        per_kor = []

    context['commune_name'] = commune_names
    context['commune_sum_list'] = commune_sum_list
    context['department_name'] = department_names
    context['department_sum_list'] = department_sum_list
    context['per_kor'] = per_kor
    context['kor_time'] = kor_time
    context['form'] = form
    context['segment'] = 'analytics'
    context['Department_choice'] = form1
    context['dep_commune_names'] = dep_commune_names
    context['dep_commune_sum_list'] = dep_commune_sum_list
    return render(request, 'dashboard/analytics.html', context)


@login_required(login_url="/")
def drone(request, plant_id, coordinate_xy):
    basemaps = {
        'Google Maps': folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr=gettext('Google'),
            name='Maps',
            max_zoom=18,
            overlay=True,
            control=False
        ),
        'Google Satellite': folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name=gettext('Satellite'),
            max_zoom=25,
            overlay=True,
            show=True,
            control=False
        ),
        'Mapbox Satellite': folium.TileLayer(
            tiles='https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoic2hha2F6IiwiYSI6ImNrczMzNTl3ejB6eTYydnBlNzR0dHUwcnUifQ.vHqPio3Pe0PehWpIuf5QUg',
            attr='Mapbox',
            name=gettext('Satellite View'),
            max_zoom=30,
            overlay=True,
            show=True,
            control=True
        )
    }
    # figure = folium.Figure()

    alldept = ee.Image('users/ashamba/allDepartments_v0')

    coordinate_xy = (coordinate_xy).replace('[', "").replace(']', "").replace(' ', "").split(',')
    coordinate_xy = [float(coordinate_xy[0]), float(coordinate_xy[1])]

    # coordinate_xy = [9.45720800, 2.64348809]

    m = folium.Map(
        location=coordinate_xy,
        zoom_start=18,
        prefer_canvas=True,
        tiles=None
    )

    m.add_child(basemaps['Google Satellite'])

    def add_ee_layer_drone(self, ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=name,
            overlay=True,
            show=True,
            control=True
        ).add_to(self)

    def add_ee_layer(self, ee_image_object, vis_params, name):
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=name,
            overlay=True,
            show=False,
            control=True
        ).add_to(self)

    folium.Map.add_ee_layer_drone = add_ee_layer_drone

    zones = alldept.eq(1)
    zones = zones.updateMask(zones.neq(0))
    folium.Map.add_ee_layer = add_ee_layer

    try:
        with open(f"staticfiles/tree_crown_geojson/{plant_id}.geojson") as f:
            crown_json = geojson.load(f)
        crown_geojson = folium.GeoJson(data=crown_json,
                                       name='Tree Tops',
                                       show=False,
                                       zoom_on_click=True)
        crown_geojson.add_to(m)
        rgb = ee.Image(f'users/ashamba/{plant_id}')
        m.add_ee_layer_drone(rgb, {}, 'Drone Image')
    except Exception as e:
        print(e)
        pass

    m.add_ee_layer(zones, {'palette': "red"}, gettext('Satellite Prediction'))
    m.add_child(folium.LayerControl())
    m = m._repr_html_()
    context = {'map': m, 'segment': 'map'}

    html_template = loader.get_template('dashboard/index.html')
    return HttpResponse(html_template.render(context, request))
