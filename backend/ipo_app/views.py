import os
import json
import logging

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods

from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import IPO, Company, Document
from .forms import IPOForm, IPOLoginForm
from .serializers import IPOSerializer

logger = logging.getLogger(__name__)

# ---------- Access Control ----------
staff_required = user_passes_test(lambda u: u.is_authenticated and u.is_staff)

# ---------- Dashboard ----------
@staff_required
def dashboard_home_view(request):
    ipos = IPO.objects.select_related("company").all()
    ipo_names = [ipo.company.company_name for ipo in ipos]
    price_band = [float(ipo.price_band or 0) for ipo in ipos]
    market_prices = [float(ipo.current_market_price or 0) for ipo in ipos]
    listing_gains = [float(ipo.listing_gain or 0) for ipo in ipos]
    current_returns = [float(ipo.current_return or 0) for ipo in ipos]

    ipo_status_counts = ipos.values('status').annotate(count=Count('status'))
    status_dict = {entry['status']: entry['count'] for entry in ipo_status_counts}

    context = {
        'ipo_names': ipo_names,
        'price_band': price_band,
        'market_prices': market_prices,
        'listing_gains': listing_gains,
        'current_returns': current_returns,
        'total_ipos': ipos.count(),
        'total_companies': Company.objects.filter(ipo__isnull=False).distinct().count(),
        'ipo_status_counts': status_dict
    }
    return render(request, 'ipo/dashboard_ipo.html', context)

# ---------- IPO Login ----------
def ipo_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('ipo_app:ipo-list')

    if request.method == 'POST':
        form = IPOLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username=username)
                if user.email != email:
                    raise ValueError("Email mismatch")
            except (User.DoesNotExist, ValueError):
                messages.error(request, "Incorrect email, username, or password.")
                return render(request, 'registration/ipo_login.html', {'form': form})

            user = authenticate(request, username=username, password=password)
            if user and user.is_staff:
                login(request, user)
                request.session['is_ipo_user'] = True
                messages.success(request, "Login successful.")
                return redirect('ipo_app:ipo-list')
            else:
                messages.error(request, "Invalid login credentials.")
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = IPOLoginForm()

    return render(request, 'registration/ipo_login.html', {'form': form})


@require_http_methods(["GET"])
def ipo_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out from IPO dashboard.")
    return redirect('ipo_app:ipo-login')

# ---------- IPO CRUD ----------
@staff_required
def ipo_list_view(request):
    query = request.GET.get("q", "")
    status_filter = request.GET.get("status", "")
    ipos = IPO.objects.prefetch_related("documents").all()

    if query:
        ipos = ipos.filter(company__company_name__icontains=query)
    if status_filter:
        ipos = ipos.filter(status=status_filter)

    return render(request, "ipo/home.html", {
        "ipos": ipos,
        "force_sidebar_open": True
    })


@staff_required
def ipo_detail_view(request, ipo_id):
    ipo = get_object_or_404(IPO.objects.prefetch_related("documents"), id=ipo_id)
    return render(request, "ipo/ipo_detail.html", {"ipo": ipo})


@staff_required
def add_ipo_view(request):
    if request.method == 'POST':
        form = IPOForm(request.POST, request.FILES)
        rhp_file = request.FILES.get('rhp_pdf')
        drhp_file = request.FILES.get('drhp_pdf')

        if form.is_valid():
            ipo = form.save(commit=False)
            raw_name = form.cleaned_data['company'].strip().lower().title()
            company = Company.objects.filter(company_name__iexact=raw_name).first()
            if not company:
                company = Company.objects.create(company_name=raw_name)

            ipo.company = company
            ipo.save()

            if rhp_file:
                Document.objects.create(ipo=ipo, file=rhp_file, doc_type='RHP')
            if drhp_file:
                Document.objects.create(ipo=ipo, file=drhp_file, doc_type='DRHP')

            messages.success(request, "IPO added successfully.")
            return redirect('ipo_app:ipo-list')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = IPOForm()

    return render(request, 'ipo/ipo_form.html', {
        'form': form,
        'edit_mode': False
    })


@staff_required
@require_http_methods(["GET", "POST"])
def update_ipo_view(request, pk):
    ipo = get_object_or_404(IPO, pk=pk)

    if request.method == 'POST':
        form = IPOForm(request.POST, request.FILES, instance=ipo)
        rhp_file = request.FILES.get('rhp_pdf')
        drhp_file = request.FILES.get('drhp_pdf')

        if form.is_valid():
            ipo = form.save(commit=False)
            raw_name = form.cleaned_data['company'].strip().lower().title()
            company = Company.objects.filter(company_name__iexact=raw_name).first()
            if not company:
                company = Company.objects.create(company_name=raw_name)

            ipo.company = company

            if request.POST.get('delete_logo') == 'true' and ipo.company_logo:
                ipo.company_logo.delete(save=True)
                ipo.company_logo = None

            ipo.save()

            if rhp_file:
                Document.objects.update_or_create(ipo=ipo, doc_type='RHP', defaults={'file': rhp_file})
            if drhp_file:
                Document.objects.update_or_create(ipo=ipo, doc_type='DRHP', defaults={'file': drhp_file})

            messages.success(request, "IPO updated successfully.")
            return redirect('ipo_app:ipo-list')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = IPOForm(instance=ipo, initial={'company': ipo.company.company_name})

    return render(request, 'ipo/ipo_form.html', {
        'form': form,
        'ipo': ipo,
        'edit_mode': True
    })


@staff_required
@require_http_methods(["POST"])
def delete_ipo_view(request, ipo_id):
    ipo = get_object_or_404(IPO, id=ipo_id)
    company = ipo.company
    ipo.delete()
    logger.info(f"IPO deleted: {ipo}")

    # Optional: delete company if no IPOs are left
    if not IPO.objects.filter(company=company).exists():
        company.delete()

    messages.success(request, "IPO deleted successfully.")
    return redirect("ipo_app:ipo-list")


@staff_required
def redirect_to_ipo_add(request):
    return redirect("ipo_app:ipo-add")

# ---------- API ----------
@api_view(["POST"])
def receive_ipo_data(request):
    try:
        logger.info("POST request received for IPO data")
        payload = request.data

        # Save payload for debugging
        file_path = os.path.join(settings.BASE_DIR, 'received_ipo.json')
        with open(file_path, 'w') as f:
            json.dump(payload, f, indent=4)

        logger.debug(f"IPO Payload:\n{json.dumps(payload, indent=2)}")

        serializer = IPOSerializer(data=payload)
        if serializer.is_valid():
            ipo = serializer.save()
            return Response({"message": "IPO saved successfully", "ipo_id": ipo.id}, status=status.HTTP_201_CREATED)
        else:
            logger.warning(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error saving IPO: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
