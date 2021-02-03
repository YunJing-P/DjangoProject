from .models import Feedback
from django.shortcuts import render


def index(request):
    latest_feedback_list = Feedback.objects.filter(is_done=0).order_by('c_time')
    context = {
        'latest_feedback_list': latest_feedback_list,
    }
    return render(request, 'sites/index.html', context)
