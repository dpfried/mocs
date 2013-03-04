def set_status(status, model=None, state='PROGRESS'):
    # task.update_state(state=state, meta={'status': status})
    if model is not None:
        if model.status is None:
            model.status = status
        else:
            model.status += '\n' + status
        model.save()
