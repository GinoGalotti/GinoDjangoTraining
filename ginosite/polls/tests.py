import datetime
from time import sleep

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from .models import Question


def create_question_hours_offset(question_text, hours):
    time = timezone.now() + datetime.timedelta(hours=hours)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_question_seconds_offset(question_text, seconds):
    time = timezone.now() + datetime.timedelta(seconds=seconds)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
    def text_index_view_with_no_question(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'No polls are available')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_past_question(self):
        create_question_hours_offset(question_text="Past Test Question", hours=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Test Question>'])

    def test_index_view_with_future_question(self):
        create_question_hours_offset(question_text="Future Test Question", hours=2)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available', status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_and_past_question(self):
        create_question_hours_offset(question_text="Future Test Question", hours=2)
        create_question_hours_offset(question_text="Past Test Question", hours=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Test Question>'])

    def test_index_view_with_more_than_onepast_question(self):
        create_question_hours_offset(question_text="Past Test Question", hours=-2)
        create_question_hours_offset(question_text="Past Test Question 2", hours=-1)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past Test Question 2>', '<Question: Past Test Question>'])

    def test_index_view_with_future_question_and_waiting(self):
        seconds_offset = 3
        create_question_seconds_offset(question_text="Near Future Test Question", seconds=seconds_offset)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available', status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
        sleep(seconds_offset)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Near Future Test Question>'])


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_future_question(self):
        future_question = create_question_hours_offset(question_text='Future Test Question', hours=3)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEquals(response.status_code, 404)

    def test_detail_view_with_past_question(self):
        past_question = create_question_hours_offset(question_text='Future Test Question', hours=-2)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)


class QuestionMethodTests(TestCase):
    def test_was_published_last_hour_with_future(self):
        """
        was_published_last_hour() should return false for question whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertEquals(future_question.was_published_last_hour(), False)

    def test_was_published_last_hour_with_one_day_ago_question(self):
        """
        was_published_last_hour() should return false for question whose pub_date is in the future
        """
        time = timezone.now() - datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertEquals(future_question.was_published_last_hour(), False)

    def test_was_published_last_hour_with_half_hour_ago_question(self):
        """
        was_published_last_hour() should return false for question whose pub_date is in the future
        """
        time = timezone.now() - datetime.timedelta(minutes=30)
        future_question = Question(pub_date=time)
        self.assertEquals(future_question.was_published_last_hour(), True)
