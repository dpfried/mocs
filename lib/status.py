def set_status(status, model=None, state='PROGRESS'):
    # task.update_state(state=state, meta={'status': status})
    if model is not None:
        model.status = status
        model.save()
