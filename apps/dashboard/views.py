import collections
import datetime

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

from apps.authentication import utils
from apps.authentication.forms import RegisterOrganization, RegisterRole
from apps.authentication.models import RemOrganization, RemRole, RemUser
from apps.dashboard import models
from apps.dashboard.models import Plantation
from .db_conn_string import cur
from .forms import UserCustomProfileForm, UserBaseProfileForm, KorDateForm, DepartmentChoice


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
        form1 = DepartmentChoice(data=request.POST or None)
        dep_commune_sum_list = []
        dep_commune_names = []
        per_kor = []
        kor_time = []
        if form1.is_valid():
            department_names_ = form1.cleaned_data.get("department")
            department_with_department = department_names_.capitalize() + " Department"

            query = (
                "SELECT kor, location_sub_region, location_region, location_country FROM free_qar_result WHERE location_country=%s AND location_region=%s OR location_region=%s")
            cur.execute(query, (country, department_names_, department_with_department))

            dep_commune = []
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
            date1 = list(date1)
            date1[8] = "0"
            date1[9] = "1"
            date1 = "".join(date1)
            date1 = date1.replace("-", "/")
            date2 = form.cleaned_data.get("my_date_field1")
            date2 = str(date2)
            date2 = list(date2)
            date2[8] = "0"
            date2[9] = "1"
            date2 = "".join(date2)
            date2 = date2.replace("-", "/")

            date1 = date1 + " 00:00:00"
            date2 = date2 + " 23:59:59"

            query = (
                "SELECT kor, location_country, created_at FROM free_qar_result WHERE location_country=%s AND created_at BETWEEN %s AND %s")
            cur.execute(query, (country, date1, date2))
            lite = []
            for kor in cur:
                lite.append(kor)
            lite = sorted(lite, key=lambda kor_: kor_[2])

            date_month_with_duplicate = []
            for x in lite:
                date_month_with_duplicate.append(x[2])
            i = 0
            month_with_duplicate = []
            while len(date_month_with_duplicate) > i:
                month_with_duplicate.append(date_month_with_duplicate[i].strftime("%m/%Y"))
                i += 1

            month_sorted = list(set(month_with_duplicate))
            month_sorted = sorted(month_sorted)

            month_occurence = collections.Counter(month_with_duplicate)
            month_occurence = month_occurence.items()
            month_occurence = list(month_occurence)

            month_init = {}
            for x in month_sorted:
                month_init[x] = 0

            for dates in lite:
                for month in month_init:
                    if month == dates[2].strftime("%m/%Y"):
                        month_init[month] += round(dates[0])

            for occur in month_occurence:
                for month in month_init:
                    if month == occur[0]:
                        month_init[month] /= occur[1]

            month_kor_list = month_init.items()
            month_kor_list = list(month_kor_list)
            month_kor_list = sorted(month_kor_list, key=lambda kor_: kor_[0])

            for x in month_kor_list:
                per_kor.append(x[1])

            for x in month_kor_list:
                kor_time.append(x[0])

    else:
        form = KorDateForm()
        form1 = DepartmentChoice()
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
def nut_count(request):
    context1 = {}

    # Query to fetch nut_count from remote database
    country = "Benin"
    query = ("SELECT nut_count,location_region,location_country FROM free_qar_result WHERE location_country=%s")
    cur.execute(query, (country,))

    infos = []
    for x in cur:
        infos.append(x)

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

    query = ("SELECT nut_count, location_sub_region, location_country FROM free_qar_result WHERE location_country=%s")
    cur.execute(query, (country,))

    infos_commune = []
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
        form1 = DepartmentChoice(data=request.POST or None)
        dep_commune_sum_list = []
        dep_commune_names = []
        per_Nut_count = []
        Nut_count_time = []
        if form1.is_valid():
            department_names_ = form1.cleaned_data.get("department")
            department_with_department = department_names_.capitalize() + " Department"

            query = (
                "SELECT nut_count, location_sub_region, location_region, location_country FROM free_qar_result WHERE location_country=%s AND location_region=%s OR location_region=%s")
            cur.execute(query, (country, department_names_, department_with_department))

            dep_commune = []
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
            date1 = list(date1)
            date1[8] = "0"
            date1[9] = "1"
            date1 = "".join(date1)
            date1 = date1.replace("-", "/")
            date2 = form.cleaned_data.get("my_date_field1")
            date2 = str(date2)
            date2 = list(date2)
            date2[8] = "0"
            date2[9] = "1"
            date2 = "".join(date2)
            date2 = date2.replace("-", "/")

            date1 = date1 + " 00:00:00"
            date2 = date2 + " 23:59:59"

            query = (
                "SELECT nut_count, location_country, created_at FROM free_qar_result WHERE location_country=%s AND created_at BETWEEN %s AND %s")
            cur.execute(query, (country, date1, date2))
            lite = []
            for kor in cur:
                lite.append(kor)
            lite = sorted(lite, key=lambda kor_: kor_[2])

            date_month_with_duplicate = []
            for x in lite:
                date_month_with_duplicate.append(x[2])
            i = 0
            month_with_duplicate = []
            while len(date_month_with_duplicate) > i:
                month_with_duplicate.append(date_month_with_duplicate[i].strftime("%m/%Y"))
                i += 1

            month_sorted = list(set(month_with_duplicate))
            month_sorted = sorted(month_sorted)

            month_occurence = collections.Counter(month_with_duplicate)
            month_occurence = month_occurence.items()
            month_occurence = list(month_occurence)

            month_init = {}
            for x in month_sorted:
                month_init[x] = 0

            for dates in lite:
                for month in month_init:
                    if month == dates[2].strftime("%m/%Y"):
                        month_init[month] += round(dates[0])

            for occur in month_occurence:
                for month in month_init:
                    if month == occur[0]:
                        month_init[month] /= occur[1]

            month_kor_list = month_init.items()
            month_kor_list = list(month_kor_list)
            month_kor_list = sorted(month_kor_list, key=lambda kor_: kor_[0])

            for x in month_kor_list:
                per_Nut_count.append(x[1])

            for x in month_kor_list:
                Nut_count_time.append(x[0])

    else:
        form = KorDateForm()
        form1 = DepartmentChoice()
        dep_commune_sum_list = []
        dep_commune_names = []
        Nut_count_time = []
        per_Nut_count = []

    context1['commune_name'] = commune_names
    context1['commune_sum_list'] = commune_sum_list
    context1['department_name'] = department_names
    context1['department_sum_list'] = department_sum_list
    context1['per_Nut_count'] = per_Nut_count
    context1['Nut_count_time'] = Nut_count_time
    context1['form'] = form
    context1['segment'] = 'analytics'
    context1['Department_choice'] = form1
    context1['dep_commune_names'] = dep_commune_names
    context1['dep_commune_sum_list'] = dep_commune_sum_list
    return render(request, 'dashboard/nut_count.html', context1)


@login_required(login_url="/")
def defective_rate(request):
    context2 = {}

    # Query to fetch nut_count from remote database
    country = "Benin"
    query = ("SELECT defective_rate,location_region,location_country FROM free_qar_result WHERE location_country=%s")
    cur.execute(query, (country,))

    infos = []
    for x in cur:
        infos.append(x)

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

    query = (
        "SELECT defective_rate, location_sub_region, location_country FROM free_qar_result WHERE location_country=%s")
    cur.execute(query, (country,))

    infos_commune = []
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
        form1 = DepartmentChoice(data=request.POST or None)
        dep_commune_sum_list = []
        dep_commune_names = []
        per_defective_rate = []
        defective_rate_time = []
        if form1.is_valid():
            department_names_ = form1.cleaned_data.get("department")
            department_with_department = department_names_.capitalize() + " Department"

            query = (
                "SELECT defective_rate, location_sub_region, location_region, location_country FROM free_qar_result WHERE location_country=%s AND location_region=%s OR location_region=%s")
            cur.execute(query, (country, department_names_, department_with_department))

            dep_commune = []
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
            date1 = list(date1)
            date1[8] = "0"
            date1[9] = "1"
            date1 = "".join(date1)
            date1 = date1.replace("-", "/")
            date2 = form.cleaned_data.get("my_date_field1")
            date2 = str(date2)
            date2 = list(date2)
            date2[8] = "0"
            date2[9] = "1"
            date2 = "".join(date2)
            date2 = date2.replace("-", "/")

            date1 = date1 + " 00:00:00"
            date2 = date2 + " 23:59:59"

            query = (
                "SELECT defective_rate, location_country, created_at FROM free_qar_result WHERE location_country=%s AND created_at BETWEEN %s AND %s")
            cur.execute(query, (country, date1, date2))
            lite = []
            for kor in cur:
                lite.append(kor)
            lite = sorted(lite, key=lambda kor_: kor_[2])

            date_month_with_duplicate = []
            for x in lite:
                date_month_with_duplicate.append(x[2])
            i = 0
            month_with_duplicate = []
            while len(date_month_with_duplicate) > i:
                month_with_duplicate.append(date_month_with_duplicate[i].strftime("%m/%Y"))
                i += 1

            month_sorted = list(set(month_with_duplicate))
            month_sorted = sorted(month_sorted)

            month_occurence = collections.Counter(month_with_duplicate)
            month_occurence = month_occurence.items()
            month_occurence = list(month_occurence)

            month_init = {}
            for x in month_sorted:
                month_init[x] = 0

            for dates in lite:
                for month in month_init:
                    if month == dates[2].strftime("%m/%Y"):
                        month_init[month] += round(dates[0])

            for occur in month_occurence:
                for month in month_init:
                    if month == occur[0]:
                        month_init[month] /= occur[1]

            month_kor_list = month_init.items()
            month_kor_list = list(month_kor_list)
            month_kor_list = sorted(month_kor_list, key=lambda kor_: kor_[0])

            for x in month_kor_list:
                per_defective_rate.append(x[1])

            for x in month_kor_list:
                defective_rate_time.append(x[0])

    else:
        form = KorDateForm()
        form1 = DepartmentChoice()
        dep_commune_sum_list = []
        dep_commune_names = []
        defective_rate_time = []
        per_defective_rate = []

    context2['commune_name'] = commune_names
    context2['commune_sum_list'] = commune_sum_list
    context2['department_name'] = department_names
    context2['department_sum_list'] = department_sum_list
    context2['per_defective_rate'] = per_defective_rate
    context2['defective_rate_time'] = defective_rate_time
    context2['form'] = form
    context2['segment'] = 'analytics'
    context2['Department_choice'] = form1
    context2['dep_commune_names'] = dep_commune_names
    context2['dep_commune_sum_list'] = dep_commune_sum_list
    return render(request, 'dashboard/defective_rate.html', context2)
