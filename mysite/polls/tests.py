from django.test import TestCase

# Create your tests here.

import datetime
from django.utils import timezone

from django.urls import reverse

from .models import Question, Choice



def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question_id, choice_text, votes):
    """
    Create a choice for the given "question_id" with the given `choice_text` and the
    given number of `votes`
    """
    return Choice.objects.create(question=question_id, choice_text=choice_text, votes=votes)



class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)



class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_question_no_choices(self):
        """
        If no choices exist, the question should not be published.
        """
        create_question(question_text="Question with no choices.", days=0)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        past_question = create_question(question_text="Past question.", days=-30)
        create_choice(past_question,"choice text", 0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        future_question = create_question(question_text="Future question.", days=30)
        create_choice(future_question,"choice text", 0)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        past_question = create_question(question_text="Past question.", days=-30)
        future_question = create_question(question_text="Future question.", days=30)
        create_choice(past_question,"choice text", 0)
        create_choice(future_question,"choice text", 0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        past_question_one = create_question(question_text="Past question 1.", days=-30)
        create_choice(past_question_one,"choice text", 0)
        past_question_two = create_question(question_text="Past question 2.", days=-5)
        create_choice(past_question_two,"choice text", 0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )




class QuestionDetailViewTests(TestCase):
    def test_question_no_choice(self):
        """ The detail view of a question with no choice
        returns a 404 not found 
        """
        question_no_choice = create_question(question_text='question with no coice', days=0)
        url = reverse('polls:detail', args=(question_no_choice.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        or/and with no choices
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        create_choice(future_question, "choice text", 0)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        create_choice(past_question, "choice text", 0)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)



class QuestionResultsViewTest(TestCase):
    def test_no_choices(self):
        """
        If no choices exist, return 404.
        """
        question_with_no_choices = create_question(question_text="Question with no choices.", days=0)
        response = self.client.get(reverse('polls:results', args=(question_with_no_choices.id,)))
        self.assertEqual(response.status_code, 404)
