from Spirit import spirit, responseEncoder, requestDecoder

app = spirit()

@app.authorizedRoute({"luka": "nya"}, "web", "/")
def index(request: requestDecoder):
    response = responseEncoder()
    response.setData("Hello")
    return response

@app.route("/reset")
def reset(request: requestDecoder):
    response = responseEncoder()
    print(request.header["authorization"])
    return response

app.run()