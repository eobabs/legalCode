# case/views.py
import json
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q
from django.urls import reverse
from django.views.generic import DetailView, ListView

from .models import Case, Donation
from .forms import CustomUserCreationForm, CaseForm, DonationForm
from .payment_utils import PaystackPayment
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from .emails import send_donation_confirmation_email, notify_case_creator_of_donation

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
def initiate_payment(request, pk):
    case = get_object_or_404(Case, pk=pk)

    if not case.can_receive_donations():
        messages.error(request, 'This case is no longer accepting donations.')
        return redirect('case_detail', pk=pk)

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            message = form.cleaned_data['message']
            is_anonymous = form.cleaned_data['is_anonymous']

            paystack = PaystackPayment()
            user_email = request.user.email if request.user.email else settings.DEFAULT_FROM_EMAIL # Fallback email
            if not user_email:
                user_email = "anonymous@example.com"

            response, reference = paystack.initialize_payment(
                email=user_email,
                amount=amount,
                case_id=case.pk,
                user_id=request.user.pk,
                message=message,
                is_anonymous=is_anonymous
            )

            if response.get('status'):
                return redirect(response['data']['authorization_url'])
            else:
                messages.error(request, f"Payment initiation failed: {response.get('message', 'Unknown error')}")
                return redirect('case_detail', pk=case.pk)
        else:
            messages.error(request, 'Please correct the errors in your donation.')
            return render(request, 'cases/case_detail.html', {'case': case, 'donation_form': form})
    else:
        return redirect('case_detail', pk=pk)


@csrf_exempt
def payment_callback(request ):
    if request.method == 'GET':
        reference = request.GET.get('trxref') or request.GET.get('reference')
        if not reference:
            messages.error(request, 'Payment reference not found.')
            return redirect('home')

        paystack = PaystackPayment()
        verification_response = paystack.verify_payment(reference)

        if verification_response.get('status') and verification_response['data']['status'] == 'success':
            metadata = verification_response['data']['metadata']
            amount_paid = Decimal(str(verification_response['data']['amount'])) / 100 # Convert kobo back to Naira
            transaction_id = verification_response['data']['reference']

            case_id = metadata.get('case_id')
            user_id = metadata.get('user_id')
            message = metadata.get('message', '')


            is_anonymous_str = metadata.get('is_anonymous', 'False')
            is_anonymous = is_anonymous_str.lower() == 'true'
            try:
                case = Case.objects.get(pk=case_id)
                donor = User.objects.get(pk=user_id)

                if not Donation.objects.filter(transaction_id=transaction_id).exists():
                    with transaction.atomic():
                        donation = Donation.objects.create(
                            case=case,
                            donor=donor,
                            amount=amount_paid,
                            message=message,
                            is_anonymous=is_anonymous,
                            transaction_id=transaction_id
                        )
                        case.raised_amount += amount_paid
                        case.save()

                        messages.success(request, f'Thank you for your donation of ₦{amount_paid:.2f} to {case.title}!')

                        send_donation_confirmation_email(donation)
                        notify_case_creator_of_donation(donation)

                else:
                    messages.info(request, 'This donation has already been processed.')

                return redirect('case_detail', pk=case.pk)

            except Case.DoesNotExist:
                messages.error(request, 'Associated case not found.')
            except User.DoesNotExist:
                messages.error(request, 'Donor user not found.')
            except Exception as e:
                messages.error(request, f'An error occurred while processing your donation. Please contact support.')
                print(f"Error processing payment callback: {e}")
                return redirect('home')

        else:
            messages.error(request, 'Payment verification failed or was not successful. Please try again.')
            return redirect('home')
    elif request.method == 'POST':

        payload = json.loads(request.body)
        event = payload.get('event')

        if event == 'charge.success':
            data = payload.get('data')
            transaction_id = data.get('reference')
            amount_paid = Decimal(str(data.get('amount'))) / 100
            metadata = data.get('metadata', {})

            case_id = metadata.get('case_id')
            user_id = metadata.get('user_id')
            message = metadata.get('message', '')

            is_anonymous_str = metadata.get('is_anonymous', 'False')
            is_anonymous = is_anonymous_str.lower() == 'true'

            try:
                case = Case.objects.get(pk=case_id)
                donor = User.objects.get(pk=user_id)

                if not Donation.objects.filter(transaction_id=transaction_id).exists():
                    with transaction.atomic():
                        donation = Donation.objects.create(
                            case=case,
                            donor=donor,
                            amount=amount_paid,
                            message=message,
                            is_anonymous=is_anonymous,
                            transaction_id=transaction_id
                        )
                        case.raised_amount += amount_paid
                        case.save()

                        send_donation_confirmation_email(donation)
                        notify_case_creator_of_donation(donation)
                return JsonResponse({'status': 'success'}, status=200)
            except (Case.DoesNotExist, User.DoesNotExist) as e:
                print(f"Webhook error: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid case or user ID in metadata'}, status=400)
            except Exception as e:
                print(f"Webhook processing error: {e}")
                return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
        return JsonResponse({'status': 'ignored'}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required
def user_dashboard(request):
    user_cases = Case.objects.filter(creator=request.user).order_by('-created_at')
    user_donations = Donation.objects.filter(donor=request.user).order_by('-created_at')[:10]

    context = {
        'user_cases': user_cases,
        'user_donations': user_donations,
    }
    return render(request, 'dashboard.html', context)

