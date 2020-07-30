from django.shortcuts import render

from django.db.models import F

from django.views import generic

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
#from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import Question, Choice

from django.utils import timezone


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        and excluding the ones with no choices.
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now() #lte meaning less than or equal.. duh !
        ).exclude( choice=None
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        and the ones with no choices.
        """
        return Question.objects.filter(pub_date__lte=timezone.now()
        ).exclude(choice=None)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        and the ones with no choices.
        """
        return Question.objects.exclude(choice=None)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        if not question.choice_set.exists() :
            # return render(request, 'polls/error.html', {
            #     'error_message': "Question does not exist.",
            # })
            return HttpResponseRedirect(reverse('polls:error', args=('Question does not exist',)))
        else:
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
    else:
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        # Consider using refresh_from_db() with F().
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def error(request, error_message):
    return render(request, 'polls/error.html', {
        'error_message': error_message,
    })
