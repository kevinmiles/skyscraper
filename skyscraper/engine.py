import abc
import requests


class Request:
    def __init__(self, url: str):
        self.url = url


class Response:
    def __init__(self, url: str, text: str):
        self.url = url
        self.text = text


class AbstractEngine(abc.ABC):
    @abc.abstractmethod
    def perform_request(self, request: Request) -> Response:
        pass


class RequestsEngine(AbstractEngine):
    def perform_request(self, request: Request) -> Response:
        # TODO: Support other methods than GET
        response = requests.get(request.url)
        return Response(response.url, response.text)


def make_engine(name):
    engines = {
        'requests': RequestsEngine,
    }

    if name in engines:
        return engines[name]()
    else:
        raise ValueError('No such engine "{}"'.format(name))
