from celery import task, current_task
from time import sleep

@task()
def add(x, y):
    return x + y;

@task()
def status(delay):
    current_task.update_state(state='PROGRESS', meta={'description': 'starting timer'})
    sleep(delay)
    current_task.update_state(state='PROGRESS', meta={'description': 'after first sleep'})
    sleep(delay)
    return 'done'
