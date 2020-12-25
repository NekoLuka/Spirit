from Spirit.consts import statusCode
from Spirit.responseEncoder import responseEncoder
from Spirit.requestDecoder import requestDecoder

def default404(context: requestDecoder) -> responseEncoder:
    response = responseEncoder(statusCode[404])
    response.setData(statusCode[404])
    return response

def default405(context: requestDecoder, allowedMethods: list) -> responseEncoder:
    response = responseEncoder("405 Method Not Allowed")
    response.setHeader("Allow", ",".join(allowedMethods))
    response.setData("405 method not allowed")
    return response

def default500(context: requestDecoder) -> responseEncoder:
    response = responseEncoder(statusCode[500])
    response.setData(statusCode[500])
    return response

def defaultRedirect(url: str="/") -> responseEncoder:
    response = responseEncoder(statusCode[301])
    response.setHeader("Location", url)
    response.setData(statusCode[301])
    return response

def defaultTeapot() -> responseEncoder:
    response = responseEncoder(statusCode[418])
    response.setData(statusCode[418])
    return response