import collections
import csv
import io
import os
from datetime import datetime

import xlwt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, FileResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views import generic
from reportlab.lib import colors
from reportlab.lib.pagesizes import A2, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    TableStyle,
    SimpleDocTemplate,
    Table,
    Paragraph,
    Spacer,
    Image,
)

from apps.authentication import utils
from apps.authentication.forms import RegisterOrganization, RegisterRole
from apps.authentication.models import RemRole, RemUser
from apps.dashboard import models
from cajulab_remote_sensing_dashboard import settings
from .db_conn_string import (
    __mysql_disconnect__,
    __close_ssh_tunnel__,
    __open_ssh_tunnel__,
    __mysql_connect__,
)
from .forms import (
    UserCustomProfileForm,
    UserBaseProfileForm,
    KorDateForm,
    DepartmentChoice,
    NurserySearch,
    BeninYieldSearch,
    PlantationsSearch,
    TrainingSearch,
    CommuneChoice,
)

CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
all_paper_params = [
    {
        'type': 'A2',
        'first_logo_x': 3.125,
        'first_logo_y': 0.865,
        'second_logo_x': 3.125,
        'second_logo_y': 0.427,
        'create_date_x': 21.67,
        'create_date_y': 0.65,
        'page_footer_logo_x': 1,
        'page_footer_logo_y': 0.60,
        'page_footer_logo_width': 0.307,
        'page_footer_logo_height': 0.307,
        'page_footer_line_x': 0.5,
        'page_footer_line_y': 0.5,
        'page_footer_line_width': 22.9,
        'page_footer_line_height': 0.5,
        'page_number_x': 22.15,
        'page_number_y': 0.25,
    },
    {
        'type': 'A4',
        'first_logo_x': 1.56,
        'first_logo_y': 0.43,
        'second_logo_x': 2.08,
        'second_logo_y': 0.28,
        'create_date_x': 10,
        'create_date_y': 0.65,
        'page_footer_logo_x': 1,
        'page_footer_logo_y': 0.60,
        'page_footer_logo_width': 0.2,
        'page_footer_logo_height': 0.2,
        'page_footer_line_x': 0.5,
        'page_footer_line_y': 0.5,
        'page_footer_line_width': 10.95,
        'page_footer_line_height': 0.5,
        'page_number_x': 10.58,
        'page_number_y': 0.25,
    }
]


@login_required(login_url="/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.

    load_template = request.path.split("/")[-1]
    context["segment"] = load_template

    html_template = loader.get_template(load_template)
    return HttpResponse(html_template.render(context, request))


def error_400(request, exception):
    return render(request, "dashboard/HTTP400.html", status=400)


def error_403(request, exception):
    return render(request, "dashboard/HTTP403.html", status=403)


def error_404(request, exception):
    return render(request, "dashboard/HTTP404.html", status=404)


def error_500(request):
    return render(request, "dashboard/HTTP500.html")


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
                    obj.created_date = datetime.now()
                    obj.updated_by = current_user.id
                    obj.updated_date = datetime.now()

                    # return redirect("/login/")
            except Exception as e:
                print("")

            obj.save()
            msg = gettext(
                'Organization created - please <a href="/register">register user</a>.'
            )
            success = True

        else:
            msg = gettext("Form is not valid")
    else:
        form = RegisterOrganization()

    return render(
        request,
        "authentication/register_org.html",
        {"form": form, "msg": msg, "success": success},
    )


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
                obj.created_date = datetime.now()
                obj.updated_by = current_user.id
                obj.updated_date = datetime.now()
                obj.save()

                msg = 'Role added - please <a href="/register">register user</a>.'
                success = True

                # return redirect("/login/")
            else:
                # Do something for anonymous users.
                msg = 'Role not added - please <a href="/register_role">try againh</a>.'
                success = False

        else:
            msg = gettext("Form is not valid")
    else:
        form = RegisterRole()

    return render(
        request,
        "authentication/register_role.html",
        {"form": form, "msg": msg, "success": success},
    )


@login_required(login_url="/")
def load_roles(request):
    org_id = request.GET.get("organization_name")
    roles = RemRole.objects.filter(organization=org_id)
    return render(request, "authentication/role_options.html", {"roles": roles})


@method_decorator(login_required, name="dispatch")
class EditProfilePageView(generic.UpdateView):
    form_class = UserCustomProfileForm
    template_name = "dashboard/profile.html"
    success_url = reverse_lazy("profile")

    def form_invalid(self, form):
        print(form.errors)
        if self.request.accepts("text/html"):
            return super(EditProfilePageView, self).form_invalid(form)
        else:
            return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        print(form.errors)
        return super(EditProfilePageView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(EditProfilePageView, self).get_context_data(**kwargs)
        context["segment"] = "profile"
        return context

    def get_object(self, queryset=None):
        print(self)
        return self.request.user


@login_required
def profile(request):
    msg = None
    success = False
    RemUser.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserBaseProfileForm(request.POST, instance=request.user)
        profile_form = UserCustomProfileForm(
            request.POST, request.FILES, instance=request.user.remuser
        )

        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect("profile")
        else:
            print(form.errors)
            print(profile_form.errors)
            msg = gettext("Form is not valid")
    else:
        form = UserBaseProfileForm(instance=request.user)
        profile_form = UserCustomProfileForm(instance=request.user.remuser)

    args = {
        "form": form,
        "profile_form": profile_form,
        "msg": msg,
        "success": success,
        "segment": "profile",
    }
    # args.update(csrf(request))
    return render(request, "dashboard/profile.html", args)


def export_pdf(datas_name, paper_type, paper_format, title_list, elemts_list, date_from=None, date_to=None):
    buffer = io.BytesIO()
    paper_params = None
    for elemt in all_paper_params:
        if elemt['type'] == paper_type:
            paper_params = elemt

    elements = []

    # For dev env
    TechnoserveLabs_reportlab_logo = Image(os.path.join(
        CORE_DIR, "static/assets/img/brand/TNS-Labs-Logov3.jpg"), paper_params['first_logo_x'] * inch,
                                                                  paper_params['first_logo_y'] * inch)
    BeninCaju_reportlab_logo = Image(os.path.join(
        CORE_DIR, "static/assets/img/brand/TNS-Labs-Logo.jpg"), paper_params['second_logo_x'] * inch,
                                                                paper_params['second_logo_y'] * inch)
    # For prod env
    # TechnoserveLabs_reportlab_logo = Image(os.path.join(
    #     settings.STATIC_ROOT, "assets/img/brand/TNS-Labs-Logov3.jpg"), paper_params['first_logo_x'] * inch,
    #                                                               paper_params['first_logo_y'] * inch)
    # BeninCaju_reportlab_logo = Image(os.path.join(
    #     settings.STATIC_ROOT, "assets/img/brand/TNS-Labs-Logo.jpg"), paper_params['second_logo_x'] * inch,
    #                                                            paper_params['second_logo_y'] * inch)
    TechnoserveLabs_reportlab_logo.hAlign = 'LEFT'
    BeninCaju_reportlab_logo.hAlign = 'RIGHT'
    logo_table = Table([[TechnoserveLabs_reportlab_logo, BeninCaju_reportlab_logo]])
    logo_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (0, 0), "LEFT"),
                ("VALIGN", (-1, -1), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (-1, -1), (-1, -1), 100),
                ("RIGHTPADDING", (0, 0), (0, 0), 100),
            ]
        )
    )

    elements.append(logo_table)
    elements.append(Spacer(1, 12))

    sample_style_sheet = getSampleStyleSheet()
    title_style = sample_style_sheet["Heading1"]
    title_style.alignment = 1
    table_name = (
        "{0} ({1} au {2})".format(gettext(datas_name),
                                  date_from[0:10], date_to[0:10]
                                  )
        if date_from and date_to
        else "{0} ({1})".format(gettext(datas_name), gettext("All"))
    )
    paragraph_1 = Paragraph(table_name, title_style)

    elements.append(paragraph_1)
    elements.append(Spacer(1, 12))

    doc = SimpleDocTemplate(
        buffer,
        title="{0}_{1}".format(gettext(datas_name), datetime.now().strftime(
            "%Y_%m_%d_%I_%M_%S")),
        rightMargin=72,
        leftMargin=72,
        topMargin=30,
        bottomMargin=72,
        pagesize=landscape(paper_format),
    )

    data = [(gettext(title) for title in title_list)]

    for elemt in elemts_list:
        data.append(elemt)

    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.Color(
                        green=(178 / 255), red=(20 / 255), blue=(177 / 255)
                    ),
                ),
                ("LEFTPADDING", (0, 0), (-1, 0), 15),
                ("RIGHTPADDING", (0, 0), (-1, 0), 15),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 15),
                ("TOPPADDING", (0, 0), (-1, 0), 15),
            ]
        )
    )

    elements.append(table)

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Times-Roman", 10)
        canvas.drawString(
            ((paper_params['page_footer_logo_x'] + paper_params['page_footer_logo_width']) + 0.05) * inch,
            0.65 * inch, table_name)
        now = datetime.now()
        create_date = "Created on " + now.strftime("%d/%m/%Y")
        canvas.drawCentredString(paper_params['create_date_x'] * inch, paper_params['create_date_y'] * inch,
                                 create_date)
        canvas.setLineWidth(0.008 * inch)

        # For dev env
        canvas.drawInlineImage(os.path.join(CORE_DIR, "static/assets/img/brand/TNS-Logo.jpg"),
                               paper_params['page_footer_logo_x'] * inch,
                               paper_params['page_footer_logo_y'] * inch,
                               paper_params['page_footer_logo_width'] * inch,
                               paper_params['page_footer_logo_height'] * inch)

        # For prod env
        # canvas.drawInlineImage(os.path.join(settings.STATIC_ROOT, "assets/img/brand/TNS-Logo.jpg"),
        #                        paper_params['page_footer_logo_x'] * inch,
        #                        paper_params['page_footer_logo_y'] * inch,
        #                        paper_params['page_footer_logo_width'] * inch,
        #                        paper_params['page_footer_logo_height'] * inch)

        canvas.line(paper_params['page_footer_line_x'] * inch, paper_params['page_footer_line_y'] * inch,
                    paper_params['page_footer_line_width'] * inch, paper_params['page_footer_line_height'] * inch)
        page_number_text = "%d" % (doc.page)
        canvas.drawCentredString(paper_params['page_number_x'] * inch, paper_params['page_number_y'] * inch,
                                 page_number_text)

        canvas.restoreState()

    try:
        doc.build(
            elements,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number,
        )
    except Exception as f:
        print(f)
    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=True,
                            filename="{0}_{1}.pdf".format(gettext(datas_name), datetime.now().strftime(
                                "%Y_%m_%d_%I_%M_%S")))
    return response


@login_required(login_url="/")
def yields(request):
    context = {}

    search_yields = request.GET.get("search")
    yields_column = request.GET.get("column")
    yields_list = None
    response = None

    if search_yields:
        if yields_column != "all":
            yields_column = yields_column.replace(" ", "_")
            params = {
                "{}__icontains".format(yields_column): search_yields,
            }
            yields_list = models.BeninYield.objects.filter(
                Q(**params), status=utils.Status.ACTIVE
            )

        else:
            yields_list = models.BeninYield.objects.filter(
                Q(plantation_name__icontains=search_yields)
                | Q(total_yield_kg__icontains=search_yields)
                | Q(total_yield_per_ha_kg__icontains=search_yields)
                | Q(total_yield_per_tree_kg__icontains=search_yields)
                | Q(product_id__icontains=search_yields)
                | Q(total_number_trees__icontains=search_yields)
                | Q(total_sick_trees__icontains=search_yields)
                | Q(total_dead_trees__icontains=search_yields)
                | Q(total_trees_out_of_prod__icontains=search_yields)
                | Q(year__icontains=search_yields),
                status=utils.Status.ACTIVE,
            )

    else:
        yields_list = models.BeninYield.objects.filter(status=utils.Status.ACTIVE)

    if "pdf" in request.POST:
        titles_list = [
            "Plantation name",
            "Product id",
            "Year",
            "Total number trees",
            "Total yield kg",
            "Total yield per ha kg",
            "Total yield per tree kg",
            "Total sick trees",
            "Total dead trees",
            "Total trees out of prod",
        ]
        yields_datas = [[getattr(yields0, title.lower().replace(" ", "_")) for title in titles_list] for yields0 in yields_list]
        response = export_pdf(datas_name='Yields', paper_type="A2", paper_format=A2, title_list=titles_list,
                              elemts_list=yields_datas)
    elif "xls" in request.POST:
        response = HttpResponse(content_type="application/ms-excel")
        if "/fr/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=rendement" + str(datetime.now()) + ".xls"
            )
        elif "/en/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=yield" + str(datetime.now()) + ".xls"
            )
        wb = xlwt.Workbook(encoding=" utf-8")
        ws = wb.add_sheet("Nurseries")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = [
            gettext("Plantation name"),
            gettext("Product id"),
            gettext("Year"),
            gettext("Total number trees"),
            gettext("Total yield kg"),
            gettext("Total yield per ha kg"),
            gettext("Total yield per tree kg"),
            gettext("Total sick trees"),
            gettext("Total dead trees"),
            gettext("Total trees out of prod"),
        ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = []

        for yields0 in yields_list:
            rows.append(
                (
                    yields0.plantation_name,
                    yields0.product_id,
                    yields0.year,
                    yields0.total_number_trees,
                    yields0.total_yield_kg,
                    yields0.total_yield_per_ha_kg,
                    yields0.total_yield_per_tree_kg,
                    yields0.total_sick_trees,
                    yields0.total_dead_trees,
                    yields0.total_trees_out_of_prod,
                )
            )

        for row in rows:
            row_num += 1

            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        wb.save(response)

    elif "csv" in request.POST:
        response = HttpResponse(content_type="text/csv")
        if "/fr/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=rendement" + str(datetime.now()) + ".csv"
            )
        elif "/en/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=yield" + str(datetime.now()) + ".csv"
            )
        writer = csv.writer(response)
        writer.writerow(
            [
                gettext("Plantation name"),
                gettext("Product id"),
                gettext("Year"),
                gettext("Total number trees"),
                gettext("Total yield kg"),
                gettext("Total yield per ha kg"),
                gettext("Total yield per tree kg"),
                gettext("Total sick trees"),
                gettext("Total dead trees"),
                gettext("Total trees out of prod"),
            ]
        )

        for yields0 in yields_list:
            writer.writerow(
                [
                    yields0.plantation_name,
                    yields0.product_id,
                    yields0.year,
                    yields0.total_number_trees,
                    yields0.total_yield_kg,
                    yields0.total_yield_per_ha_kg,
                    yields0.total_yield_per_tree_kg,
                    yields0.total_sick_trees,
                    yields0.total_dead_trees,
                    yields0.total_trees_out_of_prod,
                ]
            )

    page = request.GET.get("page", 1)

    paginator = Paginator(yields_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        yields = paginator.page(page)
    except PageNotAnInteger:
        yields = paginator.page(1)
    except EmptyPage:
        yields = paginator.page(paginator.num_pages)

    context["yields"] = yields
    context["segment"] = "yield"
    context["page_range"] = page_range
    context["form"] = BeninYieldSearch(
        initial={
            "column": request.GET.get("column", ""),
        }
    )
    return response if response else render(request, "dashboard/yield.html", context)


@login_required(login_url="/")
def plantations(request):
    context = {}

    search_plantations = request.GET.get("search")
    plantations_column = request.GET.get("column")
    plantations_list = None
    response = None

    if search_plantations:
        if plantations_column != "all":
            plantations_column = plantations_column.replace(" ", "_")
            if plantations_column == "owner_gender":
                params = {
                    "{}__iexact".format(plantations_column): search_plantations,
                }
            else:
                params = {
                    "{}__icontains".format(plantations_column): search_plantations,
                }
            plantations_list = models.Plantation.objects.filter(
                Q(**params), status=utils.Status.ACTIVE
            )

        else:
            plantations_list = models.Plantation.objects.filter(
                Q(plantation_name__icontains=search_plantations)
                | Q(plantation_code__icontains=search_plantations)
                | Q(owner_first_name__icontains=search_plantations)
                | Q(owner_last_name__icontains=search_plantations)
                | Q(owner_gender__iexact=search_plantations)
                | Q(total_trees__icontains=search_plantations)
                | Q(country__icontains=search_plantations)
                | Q(department__icontains=search_plantations)
                | Q(commune__icontains=search_plantations)
                | Q(arrondissement__icontains=search_plantations)
                | Q(village__icontains=search_plantations)
                | Q(current_area__icontains=search_plantations)
                | Q(latitude__icontains=search_plantations)
                | Q(longitude__icontains=search_plantations)
                | Q(altitude__icontains=search_plantations),
                status=utils.Status.ACTIVE,
            )

    else:
        plantations_list = models.Plantation.objects.filter(status=utils.Status.ACTIVE)

    if "pdf" in request.POST:
        titles_list = (
            "Plantation name",
            "Plantation code",
            "Owner first name",
            "Owner last name",
            "Owner gender",
            "Total trees",
            "Country",
            "Department",
            "Commune",
            "Arrondissement",
            "Village",
            "Current area",
            "Latitude",
            "Longitude",
            "Altitude",
            )

        plantations_data = [[getattr(plantations0, title.lower().replace(" ", "_")) for title in titles_list] for plantations0 in plantations_list]
        response = export_pdf(datas_name='Pantations', paper_type="A2", paper_format=A2, title_list=titles_list,
                              elemts_list=plantations_data)

    elif "xls" in request.POST:
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = (
                "attachement; filename=plantations" + str(datetime.now()) + ".xls"
        )
        wb = xlwt.Workbook(encoding=" utf-8")
        ws = wb.add_sheet("Plantations")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = [
            gettext("Plantation name"),
            gettext("Plantation code"),
            gettext("Owner first name"),
            gettext("Owner last name"),
            gettext("Owner gender"),
            gettext("Total trees"),
            gettext("Country"),
            gettext("Department"),
            gettext("Commune"),
            gettext("Arrondissement"),
            gettext("Village"),
            gettext("Current area"),
            gettext("Latitude"),
            gettext("Longitude"),
            gettext("Altitude"),
        ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = []

        for plantations0 in plantations_list:
            rows.append(
                (
                    plantations0.plantation_name,
                    plantations0.plantation_code,
                    plantations0.owner_first_name,
                    plantations0.owner_last_name,
                    plantations0.owner_gender,
                    plantations0.total_trees,
                    plantations0.country,
                    plantations0.department,
                    plantations0.commune,
                    plantations0.arrondissement,
                    plantations0.village,
                    plantations0.current_area,
                    plantations0.latitude,
                    plantations0.longitude,
                    plantations0.altitude,
                )
            )

        for row in rows:
            row_num += 1

            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        wb.save(response)

    elif "csv" in request.POST:
        response = HttpResponse(content_type="text/csv")

        response["Content-Disposition"] = (
                "attachement; filename=plantation" + str(datetime.now()) + ".csv"
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                gettext("Plantation name"),
                gettext("Plantation code"),
                gettext("Owner first name"),
                gettext("Owner last name"),
                gettext("Owner gender"),
                gettext("Total trees"),
                gettext("Country"),
                gettext("Department"),
                gettext("Commune"),
                gettext("Arrondissement"),
                gettext("Village"),
                gettext("Current area"),
                gettext("Latitude"),
                gettext("Longitude"),
                gettext("Altitude"),
            ]
        )

        for plantations0 in plantations_list:
            writer.writerow(
                [
                    plantations0.plantation_name,
                    plantations0.plantation_code,
                    plantations0.owner_first_name,
                    plantations0.owner_last_name,
                    plantations0.owner_gender,
                    plantations0.total_trees,
                    plantations0.country,
                    plantations0.department,
                    plantations0.commune,
                    plantations0.arrondissement,
                    plantations0.village,
                    plantations0.current_area,
                    plantations0.latitude,
                    plantations0.longitude,
                    plantations0.altitude,
                ]
            )

    page = request.GET.get("page", 1)

    paginator = Paginator(plantations_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        plantations = paginator.page(page)
    except PageNotAnInteger:
        plantations = paginator.page(1)
    except EmptyPage:
        plantations = paginator.page(paginator.num_pages)

    context["plantations"] = plantations
    context["segment"] = "plantations"
    context["page_range"] = page_range
    context["form"] = PlantationsSearch(
        initial={
            "column": request.GET.get("column", ""),
        }
    )
    return response if response else render(request, "dashboard/plantations.html", context)


@login_required(login_url="/")
def nurseries(request):
    context = {}

    search_nurseries = request.GET.get("search")
    nursery_column = request.GET.get("column")
    nurseries_list = None
    response = None

    if search_nurseries:
        if nursery_column != "all":
            nursery_column = nursery_column.replace(" ", "_")
            params = {
                "{}__icontains".format(nursery_column): search_nurseries,
            }
            nurseries_list = models.Nursery.objects.filter(
                Q(**params), status=utils.Status.ACTIVE
            )

        else:
            nurseries_list = models.Nursery.objects.filter(
                Q(nursery_name__icontains=search_nurseries)
                | Q(owner_first_name__icontains=search_nurseries)
                | Q(owner_last_name__icontains=search_nurseries)
                | Q(nursery_address__icontains=search_nurseries)
                | Q(country__icontains=search_nurseries)
                | Q(commune__icontains=search_nurseries)
                | Q(current_area__icontains=search_nurseries)
                | Q(latitude__icontains=search_nurseries)
                | Q(longitude__icontains=search_nurseries)
                | Q(altitude__icontains=search_nurseries)
                | Q(partner__icontains=search_nurseries)
                | Q(number_of_plants__icontains=search_nurseries),
                status=utils.Status.ACTIVE,
            )

    else:
        nurseries_list = models.Nursery.objects.filter(status=utils.Status.ACTIVE)

    if "pdf" in request.POST:
        titles_list = (
            "Nursery Name",
            "Owner First Name",
            "Owner Last Name",
            "Nursery Address",
            "Country",
            "Commune",
            "Current Area",
            "Latitude",
            "Longitude",
            "Altitude",
            "Partner",
            "Number of Plants",
        )
        nurseries_data = [[getattr(nursery0, title.lower().replace(" ", "_")) for title in titles_list] for nursery0 in nurseries_list]
        response = export_pdf(datas_name='Nurseries', paper_type="A2", paper_format=A2, title_list=titles_list,
                              elemts_list=nurseries_data)


    elif "xls" in request.POST:
        response = HttpResponse(content_type="application/ms-excel")
        if "/fr/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=pépinières" + str(datetime.now()) + ".xls"
            )
        elif "/en/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=nurseries" + str(datetime.now()) + ".xls"
            )
        wb = xlwt.Workbook(encoding=" utf-8")
        ws = wb.add_sheet("Nurseries")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = [
            gettext("Nursery Name"),
            gettext("Owner First Name"),
            gettext("Owner Last Name"),
            gettext("Nursery Address"),
            gettext("Country"),
            gettext("Commune"),
            gettext("Current Area"),
            gettext("Latitude"),
            gettext("Longitude"),
            gettext("Altitude"),
            gettext("Partner"),
            gettext("Number of Plants"),
        ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = []

        for nursery0 in nurseries_list:
            rows.append(
                (
                    nursery0.nursery_name,
                    nursery0.owner_first_name,
                    nursery0.owner_last_name,
                    nursery0.nursery_address,
                    nursery0.country,
                    nursery0.commune,
                    nursery0.current_area,
                    nursery0.latitude,
                    nursery0.longitude,
                    nursery0.altitude,
                    nursery0.partner,
                    nursery0.number_of_plants,
                )
            )

        for row in rows:
            row_num += 1

            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        wb.save(response)

    elif "csv" in request.POST:
        response = HttpResponse(content_type="text/csv")
        if "/fr/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=pépinières" + str(datetime.now()) + ".csv"
            )
        elif "/en/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=nurseries" + str(datetime.now()) + ".csv"
            )
        writer = csv.writer(response)
        writer.writerow(
            [
                gettext("Nursery Name"),
                gettext("Owner First Name"),
                gettext("Owner Last Name"),
                gettext("Nursery Address"),
                gettext("Country"),
                gettext("Commune"),
                gettext("Current Area"),
                gettext("Latitude"),
                gettext("Longitude"),
                gettext("Altitude"),
                gettext("Partner"),
                gettext("Number of Plants"),
            ]
        )

        for nursery0 in nurseries_list:
            writer.writerow(
                [
                    nursery0.nursery_name,
                    nursery0.owner_first_name,
                    nursery0.owner_last_name,
                    nursery0.nursery_address,
                    nursery0.country,
                    nursery0.commune,
                    nursery0.current_area,
                    nursery0.latitude,
                    nursery0.longitude,
                    nursery0.altitude,
                    nursery0.partner,
                    nursery0.number_of_plants,
                ]
            )

    page = request.GET.get("page", 1)

    paginator = Paginator(nurseries_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        nurseries = paginator.page(page)
    except PageNotAnInteger:
        nurseries = paginator.page(1)
    except EmptyPage:
        nurseries = paginator.page(paginator.num_pages)

    context["nurseries"] = nurseries
    context["segment"] = "nurseries"
    context["page_range"] = page_range
    context["form"] = NurserySearch(
        initial={
            "column": request.GET.get("column", ""),
        }
    )
    return response if response else render(request, "dashboard/nurseries.html", context)


@login_required(login_url="/")
def training(request):
    context = {}

    search_training = request.GET.get("search")
    training_column = request.GET.get("column")
    department_form = request.GET.get("department")
    commune_form = request.GET.get("commune")
    date_form_from = request.GET.get("my_date_field")
    date_form_to = request.GET.get("my_date_field1")
    training_list = None
    response = None

    if search_training:

        if date_form_from and date_form_to:
            date_form_from = date_form_from + " 00:00:00.000000"
            date_form_to = date_form_to + " 23:59:59.999999"

        if training_column == "module name":
            training_column = training_column.replace(" ", "_")
            params = {
                "{}__icontains".format(training_column): search_training,
            }
            module_list = models.TrainingModule.objects.filter(Q(**params))
            if date_form_from and date_form_to:
                training_object = models.Training.objects.filter(
                    DateTime__gte=date_form_from, DateTime__lte=date_form_to
                )
            else:
                training_object = models.Training.objects.all()
            training_list = []
            for item in training_object:
                for element in module_list:
                    if str(item.module_id) == str(element.id):
                        training_list.append(item)

        elif training_column == "trainer first name":
            trainer_firstname_list = models.Trainer.objects.filter(
                Q(firstname__icontains=search_training)
            )
            if date_form_from and date_form_to:
                training_object = models.Training.objects.filter(
                    DateTime__range=[date_form_from, date_form_to]
                )
            else:
                training_object = models.Training.objects.all()
            training_list = []
            for item in training_object:
                for element in trainer_firstname_list:
                    if str(item.trainer_id) == str(element.id):
                        training_list.append(item)

        elif training_column == "trainer last name":
            trainer_lastname_list = models.Trainer.objects.filter(
                Q(lastname__icontains=search_training)
            )
            if date_form_from and date_form_to:
                training_object = models.Training.objects.filter(
                    DateTime__range=[date_form_from, date_form_to]
                )
            else:
                training_object = models.Training.objects.all()
            training_list = []
            for item in training_object:
                for element in trainer_lastname_list:
                    if str(item.trainer_id) == str(element.id):
                        training_list.append(item)

        elif training_column == "number of participant":
            training_column = training_column.replace(" ", "_")
            if date_form_from and date_form_to:
                training_object = models.Training.objects.filter(
                    DateTime__range=[date_form_from, date_form_to]
                )
            else:
                training_object = models.Training.objects.all()
            params = {
                "{}__icontains".format(training_column): search_training,
            }
            training_list = training_object.filter(Q(**params))

        else:
            module_list = models.TrainingModule.objects.filter(
                Q(module_name__icontains=search_training)
            )
            if date_form_from and date_form_to:
                training_object = models.Training.objects.filter(
                    DateTime__range=[date_form_from, date_form_to]
                )
            else:
                training_object = models.Training.objects.all()
            training_list = []
            for item in training_object:
                for element in module_list:
                    if str(item.module_id) == str(element.id):
                        training_list.append(item)
            trainer_firstname_list = models.Trainer.objects.filter(
                Q(firstname__icontains=search_training)
            )
            for item in training_object:
                for element in trainer_firstname_list:
                    if str(item.trainer_id) == str(element.id):
                        training_list.append(item)
            trainer_lastname_list = models.Trainer.objects.filter(
                Q(lastname__icontains=search_training)
            )
            for item in training_object:
                for element in trainer_lastname_list:
                    if str(item.trainer_id) == str(element.id):
                        training_list.append(item)
            training_list_beta = models.Training.objects.filter(
                Q(number_of_participant__icontains=search_training)
            )
            for item in training_list_beta:
                training_list.append(item)
    elif department_form or commune_form:
        if department_form:
            if date_form_from and date_form_to:
                training_list = models.Training.objects.filter(Q(department__icontains=department_form),
                                                               DateTime__range=[date_form_from, date_form_to])
            else:
                training_list = models.Training.objects.filter(Q(department__icontains=department_form))

        elif commune_form:
            if date_form_from and date_form_to:
                training_list = models.Training.objects.filter(Q(commune__icontains=commune_form),
                                                               DateTime__range=[date_form_from, date_form_to])
            else:
                training_list = models.Training.objects.filter(Q(commune__icontains=commune_form))

    elif date_form_from and date_form_to:
        training_list = models.Training.objects.filter(
            DateTime__range=[date_form_from, date_form_to]
        )

    else:
        training_list = models.Training.objects.all()

    if "pdf" in request.POST:
        titles_list = (
            "Module Name",
            "Trainer First Name",
            "Trainer Last Name",
            "Date",
            "Hour",
            "Number of Participant",
            "Department",
            "Commune",
        )

        training_data = []

        for training0 in training_list:
            training_data.append(
                (
                    training0.module_id.module_name
                    if training0.module_id.module_name
                       and training0.module_id.module_name != "nan"
                    else "--",
                    training0.trainer_id.firstname
                    if training0.trainer_id.firstname
                        and training0.trainer_id.firstname != "nan"
                    else "--",
                    training0.trainer_id.lastname
                    if training0.trainer_id.lastname
                       and training0.trainer_id.lastname != "nan"
                    else "--",
                    training0.DateTime.strftime("%Y-%m-%d")
                    if training0.DateTime and training0.DateTime != "nan"
                    else "--",
                    training0.DateTime.strftime("%H:%M")
                    if training0.DateTime and training0.DateTime != "nan"
                    else "--",
                    training0.number_of_participant
                    if training0.number_of_participant
                       and training0.number_of_participant != "nan"
                    else "--",
                    training0.department
                    if training0.department
                       and training0.department != "nan"
                    else "--",
                    training0.commune
                    if training0.commune
                       and training0.commune != "nan"
                    else "--",
                )
            )
        response = export_pdf(datas_name='Trainings', paper_type="A4", paper_format=A4, title_list=titles_list,
                              elemts_list=training_data)                

    elif "xls" in request.POST:
        response = HttpResponse(content_type="application/ms-excel")
        if "/fr/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=formations" + str(datetime.now()) + ".xls"
            )
        elif "/en/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=trainings" + str(datetime.now()) + ".xls"
            )
        wb = xlwt.Workbook(encoding=" utf-8")
        ws = wb.add_sheet("Trainings")
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = [
            gettext("Module Name"),
            gettext("Trainer First Name"),
            gettext("Trainer Last Name"),
            gettext("Date"),
            gettext("Hour"),
            gettext("Number of Participant"),
            gettext("Department"),
            gettext("Commune"),
        ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = []

        for training in training_list:
            rows.append(
                (
                    training.module_id.module_name,
                    training.trainer_id.firstname,
                    training.trainer_id.lastname,
                    training.DateTime.strftime("%Y-%m-%d"),
                    training.DateTime.strftime("%H:%M"),
                    training.number_of_participant,
                    training.department,
                    training.commune,
                )
            )

        for row in rows:
            row_num += 1

            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        wb.save(response)

    elif "csv" in request.POST:
        response = HttpResponse(content_type="text/csv")
        if "/fr/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=formation" + str(datetime.now()) + ".csv"
            )
        elif "/en/" in request.build_absolute_uri():
            response["Content-Disposition"] = (
                    "attachement; filename=training" + str(datetime.now()) + ".csv"
            )
        writer = csv.writer(response)
        writer.writerow(
            [
                gettext("Module Name"),
                gettext("Trainer First Name"),
                gettext("Trainer Last Name"),
                gettext("Date"),
                gettext("Hour"),
                gettext("Number of Participant"),
                gettext("Department"),
                gettext("Commune"),
            ]
        )

        for training in training_list:
            writer.writerow(
                [
                    training.module_id.module_name,
                    training.trainer_id.firstname,
                    training.trainer_id.lastname,
                    training.DateTime.strftime("%Y-%m-%d"),
                    training.DateTime.strftime("%H:%M"),
                    training.number_of_participant,
                    training.department,
                    training.commune,
                ]
            )

    page = request.GET.get("page", 1)

    paginator = Paginator(training_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        trainings = paginator.page(page)
    except PageNotAnInteger:
        trainings = paginator.page(1)
    except EmptyPage:
        trainings = paginator.page(paginator.num_pages)

    context["trainings"] = trainings
    context["segment"] = "trainings"
    context["page_range"] = page_range
    context["department_form"] = DepartmentChoice(initial={"department": request.GET.get("department")})
    context["commune_form"] = CommuneChoice(initial={"commune": request.GET.get("commune")})
    context["form"] = TrainingSearch(
        initial={
            "column": request.GET.get("column", ""),
        }
    )
    context["date_duration_get_form"] = KorDateForm(
        initial={
            "my_date_field": request.GET.get("my_date_field"),
            "my_date_field1": request.GET.get("my_date_field1"),
        }
    )
    return response if response else render(request, "dashboard/training.html", context)


@login_required(login_url="/")
def shipment(request):
    context = {}
    nurseries_list = models.Nursery.objects.filter(status=utils.Status.ACTIVE)

    page = request.GET.get("page", 1)

    paginator = Paginator(nurseries_list, 10)

    page_range = paginator.get_elided_page_range(number=page)
    try:
        nurseries = paginator.page(page)
    except PageNotAnInteger:
        nurseries = paginator.page(1)
    except EmptyPage:
        nurseries = paginator.page(paginator.num_pages)

    context["nurseries"] = nurseries
    context["segment"] = "shipment"
    context["page_range"] = page_range
    return render(request, "dashboard/shipment.html", context)


@login_required(login_url="/")
def analytics(request):
    context = {}
    kor_date_period = gettext("KOR Graph against date period")
    __open_ssh_tunnel__()
    cur = __mysql_connect__().cursor()
    country = "Benin"
    query = "SELECT kor,location_region,location_country FROM free_qar_result WHERE location_country=%s"
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
    department_sum_list0 = sorted(
        department_sum_list0, reverse=True, key=lambda kor_: kor_[1]
    )

    department_sum_list = []
    for x in department_sum_list0:
        department_sum_list.append(x[1])

    department_names = []
    for x in department_sum_list0:
        department_names.append(x[0])

    query = "SELECT kor, location_sub_region, location_country FROM free_qar_result WHERE location_country=%s"
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

            query = "SELECT kor, location_sub_region, location_region, location_country FROM free_qar_result WHERE location_country=%s AND location_region=%s OR location_region=%s"
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

            query = "SELECT kor, location_country, created_at FROM free_qar_result WHERE location_country=%s AND created_at BETWEEN %s AND %s"
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
                month_with_duplicate.append(
                    date_month_with_duplicate[i].strftime("%m/%Y")
                )
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

    context["commune_name"] = commune_names
    context["commune_sum_list"] = commune_sum_list
    context["department_name"] = department_names
    context["department_sum_list"] = department_sum_list
    context["per_kor"] = per_kor
    context["kor_time"] = kor_time
    context["form"] = form
    context["segment"] = "analytics"
    context["Department_choice"] = form1
    context["dep_commune_names"] = dep_commune_names
    context["dep_commune_sum_list"] = dep_commune_sum_list
    context["kor_date_period"] = kor_date_period
    __mysql_disconnect__()
    __close_ssh_tunnel__()
    return render(request, "dashboard/analytics.html", context)


@login_required(login_url="/")
def nut_count(request):
    context1 = {}
    nut_date_period = gettext("Nut count Graph against date period")
    __open_ssh_tunnel__()
    cur = __mysql_connect__().cursor()
    # Query to fetch nut_count from remote database
    country = "Benin"
    query = "SELECT nut_count,location_region,location_country FROM free_qar_result WHERE location_country=%s"
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
    department_sum_list0 = sorted(
        department_sum_list0, reverse=True, key=lambda kor_: kor_[1]
    )

    department_sum_list = []
    for x in department_sum_list0:
        department_sum_list.append(x[1])

    department_names = []
    for x in department_sum_list0:
        department_names.append(x[0])

    query = "SELECT nut_count, location_sub_region, location_country FROM free_qar_result WHERE location_country=%s"
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

            query = "SELECT nut_count, location_sub_region, location_region, location_country FROM free_qar_result WHERE location_country=%s AND location_region=%s OR location_region=%s"
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

            query = "SELECT nut_count, location_country, created_at FROM free_qar_result WHERE location_country=%s AND created_at BETWEEN %s AND %s"
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
                month_with_duplicate.append(
                    date_month_with_duplicate[i].strftime("%m/%Y")
                )
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

    context1["commune_name"] = commune_names
    context1["commune_sum_list"] = commune_sum_list
    context1["department_name"] = department_names
    context1["department_sum_list"] = department_sum_list
    context1["per_Nut_count"] = per_Nut_count
    context1["Nut_count_time"] = Nut_count_time
    context1["form"] = form
    context1["segment"] = "analytics"
    context1["Department_choice"] = form1
    context1["dep_commune_names"] = dep_commune_names
    context1["dep_commune_sum_list"] = dep_commune_sum_list
    context1["nut_date_period"] = nut_date_period
    __mysql_disconnect__()
    __close_ssh_tunnel__()
    return render(request, "dashboard/nut_count.html", context1)


@login_required(login_url="/")
def defective_rate(request):
    context2 = {}
    defective_date_period = gettext("Defective rate Graph against date period")
    __open_ssh_tunnel__()
    cur = __mysql_connect__().cursor()
    # Query to fetch nut_count from remote database
    country = "Benin"
    query = "SELECT defective_rate,location_region,location_country FROM free_qar_result WHERE location_country=%s"
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
    department_sum_list0 = sorted(
        department_sum_list0, reverse=True, key=lambda kor_: kor_[1]
    )

    department_sum_list = []
    for x in department_sum_list0:
        department_sum_list.append(x[1])

    department_names = []
    for x in department_sum_list0:
        department_names.append(x[0])

    query = "SELECT defective_rate, location_sub_region, location_country FROM free_qar_result WHERE location_country=%s"
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

            query = "SELECT defective_rate, location_sub_region, location_region, location_country FROM free_qar_result WHERE location_country=%s AND location_region=%s OR location_region=%s"
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

            query = "SELECT defective_rate, location_country, created_at FROM free_qar_result WHERE location_country=%s AND created_at BETWEEN %s AND %s"
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
                month_with_duplicate.append(
                    date_month_with_duplicate[i].strftime("%m/%Y")
                )
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

    context2["commune_name"] = commune_names
    context2["commune_sum_list"] = commune_sum_list
    context2["department_name"] = department_names
    context2["department_sum_list"] = department_sum_list
    context2["per_defective_rate"] = per_defective_rate
    context2["defective_rate_time"] = defective_rate_time
    context2["form"] = form
    context2["segment"] = "analytics"
    context2["Department_choice"] = form1
    context2["dep_commune_names"] = dep_commune_names
    context2["dep_commune_sum_list"] = dep_commune_sum_list
    context2["defective_date_period"] = defective_date_period
    __mysql_disconnect__()
    __close_ssh_tunnel__()
    return render(request, "dashboard/defective_rate.html", context2)
