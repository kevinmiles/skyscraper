import logging
import abc
import requests
import asyncio
import pyppeteer


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

    @abc.abstractmethod
    def perform_download(self, url: str) -> bytes:
        pass

    def close(self):
        pass


class RequestsEngine(AbstractEngine):
    def perform_request(self, request: Request) -> Response:
        # TODO: Support other methods than GET
        response = requests.get(request.url)
        return Response(response.url, response.text)

    def perform_download(self, url: str) -> bytes:
        response = requests.get(url)
        return response.content


class ChromeEngine(AbstractEngine):
    def __init__(self):
        self.browser = None

    def perform_request(self, request: Request) -> Response:
        return asyncio.get_event_loop().run_until_complete(self._perform_request_async(request))

    def perform_download(self, url: str) -> bytes:
        response = requests.get(url)
        return response.content

    def close(self):
        asyncio.get_event_loop().run_until_complete(self._close())

    async def _close(self):
        if self.browser:
            await self.browser.close()

    async def _perform_request_async(self, request: Request) -> Response:
        if not self.browser:
            self.browser = await pyppeteer.launch()

        try:
            page = await self.browser.newPage()
            chrome_resp = await page.goto(request.url)
            content = await chrome_resp.text()

            return Response(chrome_resp.url, content)
        except pyppeteer.errors.NetworkError:
            logging.error('Pyppeteer NetworkError while visiting "{}"'.format(request.url))



def make_engine(name):
    engines = {
        'requests': RequestsEngine,
        'chrome': ChromeEngine,
    }

    if name in engines:
        return engines[name]()
    else:
        raise ValueError('No such engine "{}"'.format(name))
