from django.urls import reverse


def channels_reverse(viewname, args=None, kwargs=None):
    """
        Reverse doesn't work with channels on default, I have found a function on stackoverflow 
        that does the same thing as reverse but for channels.
    """
    return reverse(viewname, urlconf='game.routing', args=args, kwargs=kwargs)