from Spirit import spirit, responseEncoder, requestDecoder

app = spirit()

@app.route("/")
def index(request: requestDecoder):
    response = responseEncoder()
    response.setData("Hello world")
    return response

app.run()