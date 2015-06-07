import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_last_hour(self):
        now = timezone.now()
        return now - datetime.timedelta(hours=1) <= self.pub_date <= now

    was_published_last_hour.admin_order_field = 'pub_date'
    was_published_last_hour.boolean = True
    was_published_last_hour.short_description = 'Published during this hour'


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
