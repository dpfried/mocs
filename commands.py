from os import getpid, kill, wait
from signal import SIGINT
from djcelery.management.commands import celeryd_detach
from settings import CELERY_PID_FILENAME, CELERY_LOG_FILENAME
from django.core.management import call_command
from StringIO import StringIO

def restart_django():
    pid = getpid()
    kill(pid, SIGINT)
    return pid

def restart_celery():
    try:
        with open(CELERY_PID_FILENAME) as f:
            pid = int(f.read().strip())
        kill(pid, SIGINT)
    except IOError:
        pid = None

    args = ['--logfile', CELERY_LOG_FILENAME, '--pidfile', CELERY_PID_FILENAME]
    command = celeryd_detach.Command()
    command.run_from_argv(args)
    with open(CELERY_PID_FILENAME) as f:
        new_pid = int(f.read().strip())
    return pid, new_pid

def syncdb():
    output = StringIO()
    call_command('syncdb', interactive=False, stdout=output)
    output.seek(0)
    return output.read()
