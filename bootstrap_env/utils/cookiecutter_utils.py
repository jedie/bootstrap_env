from pprint import pprint

from cookiecutter.main import cookiecutter


def verbose_cookiecutter(**kwargs):
    from cookiecutter.log import configure_logger
    configure_logger(stream_level='DEBUG')

    print("Run cookiecutter with:")
    pprint(kwargs)
    print()
    result = cookiecutter(**kwargs)
    return result
