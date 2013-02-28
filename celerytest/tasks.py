from celery.task import task
from time import sleep

@task()
def add(x, y):
    return x + y;

@task()
def status(delay):
    status.update_state(state='PROGRESS', meta={'description': 'starting timer'})
    sleep(delay)
    status.update_state(state='PROGRESS', meta={'description': 'after first sleep'})
    sleep(delay)
    return 'done'
