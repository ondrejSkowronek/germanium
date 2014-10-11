import collections
import six

from django.utils.unittest.compatibility import wraps


def login(function=None, **user_kwargs):
    """Login decorator usage: @login(user_data)"""
    def _login(function):
        def _decorator(self, *args, **kwargs):
            user = self.get_user(**user_kwargs)
            self.login(user)
            return function(self, *args, **kwargs)
        return wraps(function)(_decorator)

    if function:
        return _login(function)
    return _login


def login_all(cls=None, **user_kwargs):
    """Login decorator for all methods inside test usage: @login(user_data)"""
    def _login_all(cls):
        for attr, val in cls.__dict__.iteritems():
            if callable(val) and attr.startswith("test_"):
                setattr(cls, attr, login(**user_kwargs)(val))
        return cls

    if cls:
        return _login_all(cls)
    return _login_all


def data_provider(fn_data_provider_or_str, *data_provider_args, **data_provider_kwargs):
    """Data provider decorator, allows another callable to provide the data for the test"""
    def test_decorator(fn):

        def get_data(self):
            if isinstance(fn_data_provider_or_str, six.string_types):
                return getattr(self, fn_data_provider_or_str)()
            else:
                return fn_data_provider_or_str(self)

        def repl(self, *args):
            for i in get_data(self):
                try:
                    if isinstance(i, collections.Iterable):
                        fn(self, *i)
                    else:
                        fn(self, i)
                except AssertionError:
                    print "Assertion error caught with data set ", i
                    raise
        return repl
    return test_decorator
