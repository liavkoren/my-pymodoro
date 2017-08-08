import datetime
import os
import time

import click
import django
import pygame
from pytz import timezone
import reprlib
from tqdm import tqdm


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pymodoro.settings')
django.setup()
from bouts import models  # NOQA

# from django import utils # see utils.timezone.now()
eastern = timezone('US/Eastern')


@click.group()
def cli():
    pass


@cli.command('start-project')
@click.argument('name')
@click.argument('description')
def start_project(name, description):
    models.Project.objects.create(name=name, description=description)
    click.echo(f"Created new project:  {name}\n  Go get 'em, champ.")


@cli.command('projects')
def projects():
    for project in models.Project.objects.all():
        click.echo(f'{project.name}: {reprlib.repr(project.description)}')


@cli.command('project-metrics')
@click.argument('name')
def project_metrics(name):
    for metric in models.ProjectMetric.objects.filter(project__name=name):
        click.echo(metric)


@cli.command('start-bout')
@click.argument('project')
def start_bout(project):
    """
    - Create Bout instance
    - Kick off a count down timer
    - On timer expiration, retrieve Bout instance, and update with notes,
    results and data for associated metrics.
        - Ideally
    - Collect plan, result and metrics info
    - play background, and ending sounds
    """
    bout = create_bout(project)
    bout_in_progress(bout)
    bout_complete(bout)


def create_bout(project):
    return models.Bout.objects.create(
        duration=datetime.timedelta(seconds=click.prompt('How many minutes?', default=35) * 60),
        plan=click.prompt("What's the plan, stan?"),
        project=models.Project.objects.get(name=project),
        start_time=datetime.datetime.now().astimezone(eastern),
    )


def bout_in_progress(bout):
    now = datetime.datetime.now().astimezone(eastern)
    bar_format = '{l_bar}{bar}[{elapsed}<{remaining}]'
    with tqdm(total=bout.duration.total_seconds(), desc='Bout progress', bar_format=bar_format, leave=False) as pbar:
        while datetime.datetime.now().astimezone(eastern) < bout.start_time + bout.duration:
            time.sleep(0.1)
            increment = (datetime.datetime.now().astimezone(eastern) - now).total_seconds()
            now = datetime.datetime.now().astimezone(eastern)
            pbar.update(increment)


@cli.command('bouts')
@click.argument('project')
def list_bouts(project):
    """ List a project's bouts."""
    # TODO: filtering
    pass


def bout_complete(bout):
    now = datetime.datetime.now()
    play_complete_sound()
    bout.result = click.prompt("How'd it go?")
    bout.focus = click.prompt('Focus level? (Likert scale, 1 - 7, one is very bad, seven is very good)')
    two_minutes = datetime.timedelta(seconds=60*2)
    time_elapsed = datetime.datetime.now() - now
    minutes, seconds = divmod(time_elapsed.total_seconds(), 60)
    if time_elapsed > two_minutes and click.prompt(f'Add an extra {minutes:.0f}:{seconds:02.0f} to the bout?', type=click.BOOL):
        bout.duration += time_elapsed
    bout.save()


def play_complete_sound():
    pygame.mixer.init()
    pygame.mixer.music.load('/Users/liavkoren/Downloads/applause3.wav')
    pygame.mixer.music.play()


if __name__ == '__main__':
    cli()
