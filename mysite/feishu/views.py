from .models import Feedback
from django.shortcuts import render


def index(request):
    latest_feedback_list = Feedback.objects.order_by('c_time')[:5]
    context = {
        'latest_feedback_list': latest_feedback_list,
    }
    return render(request, 'sites/index.html', context)
