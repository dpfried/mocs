import datetime

def set_status(status, model=None, state='PROGRESS'):
    # task.update_state(state=state, meta={'status': status})
    print '%s %s %s' % (datetime.datetime.now().time().isoformat(), ':', status)
    if model is not None:
        if model.status is None:
            model.status = status
        else:
            #model.status += '\n' + status
            model.status = status
        model.save()
