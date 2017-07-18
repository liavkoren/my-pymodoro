from django.core.validators import MaxValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel


from pytz import timezone


class Bout(models.Model):
    """ A Pymodoro work session. """
    project = models.ForeignKey('Project')
    start_time = models.DateTimeField()
    duration = models.DurationField(help_text='Duration in seconds.')
    notes = models.TextField(blank=True)
    plan = models.TextField()
    result = models.TextField(blank=True)
    focus = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MaxValueValidator(8)], help_text='Focus level, during the bout. Likert scale, out of seven. Four is neutral, one is very bad, seven is very good.')

    class Meta:
        ordering = ('start_time', )

    def __str__(self):
        formatter = '%d/%m/%Y @ %H:%M'  # day/month/year @ hour:minute. Day/month zero padded.
        localized = self.start_time.astimezone(timezone('US/Eastern')).strftime(formatter)
        return f'project={self.project.name}, start_time={localized}'


class Project(TimeStampedModel):
    """ A project that you're applying work sessions towards. """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name}: {self.description}'
