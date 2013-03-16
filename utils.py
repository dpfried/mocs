from django.utils import simplejson
from django.http import HttpResponse
from re import sub, compile

# as seen at https://coderwall.com/p/k8vb_a
def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = simplejson.dumps(objects)
            if 'callback' in request.REQUEST:
                # a jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                return HttpResponse(data, "text/javascript")
        except:
            data = simplejson.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator

generalize_pattern = compile(r'[\s\.]+')

def generalize(query_string):
    generalized = sub(generalize_pattern, '%', query_string)
    if not generalized.startswith('%'):
        generalized = '%' + generalized
    if not generalized.endswith('%'):
        generalized = generalized + '%'
    return generalized
