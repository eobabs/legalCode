from django.db import transaction
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from .models import Case, Donation
from .forms import CustomUserCreationForm, CaseForm, DonationForm


def home(request):
    recent_cases = Case.objects.filter(status='active').select_related('creator').order_by('-created_at')[:6]
    total_raised = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_cases = Case.objects.count()
    total_donors = Donation.objects.values('donor').distinct().count()

    context = {
        'recent_cases': recent_cases,
        'total_raised': total_raised,
        'total_cases': total_cases,
        'total_donors': total_donors,
    }
    return render(request, 'home.html', context)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Legal Aid Crowdfunding.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class CaseListView(ListView):
    model = Case
    template_name = 'cases/case_list.html'
    context_object_name = 'cases'
    paginate_by = 9

    def get_queryset(self):
        queryset = Case.objects.filter(status='active').select_related('creator')


        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )


        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['-created_at', 'goal_amount', '-goal_amount', 'deadline']:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset


class CaseDetailView(DetailView):
    model = Case
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['donation_form'] = DonationForm()
        context['recent_donations'] = self.object.donations.all()[:5]
        return context


@login_required
def create_case(request):
    if request.method == 'POST':
        form = CaseForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            case.creator = request.user
            case.save()
            messages.success(request, 'Case created successfully!')
            return redirect('case_detail', pk=case.pk)
    else:
        form = CaseForm()
    return render(request, 'cases/create_case.html', {'form': form})


@login_required
def donate_to_case(request, pk):
    case = get_object_or_404(Case, pk=pk)

    if not case.can_receive_donations():
        messages.error(request, 'This case is no longer accepting donations.')
        return redirect('case_detail', pk=pk)

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    donation = form.save(commit=False)
                    donation.case = case
                    donation.donor = request.user
                    donation.save()

                    case.raised_amount += donation.amount
                    case.save()

                    messages.success(
                        request,
                        f'Thank you for your donation of ${donation.amount}!'
                    )
                    return redirect('case_detail', pk=case.pk)
            except Exception as e:
                messages.error(request, 'There was an error processing your donation. Please try again.')

    return redirect('case_detail', pk=pk)


@login_required
def user_dashboard(request):
    user_cases = Case.objects.filter(creator=request.user).order_by('-created_at')
    user_donations = Donation.objects.filter(donor=request.user).order_by('-created_at')[:10]

    context = {
        'user_cases': user_cases,
        'user_donations': user_donations,
    }
    return render(request, 'dashboard.html', context)

