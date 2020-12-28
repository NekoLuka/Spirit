from Spirit import spirit, responseEncoder, requestDecoder

app = spirit()

@app.route("/<luka>/something/<nya>")
def index(request: requestDecoder, luka, nya):
    response = responseEncoder()
    response.setData(f"Hello {luka}, {nya}")
    return response

@app.route("/")
def ind(context: requestDecoder):
    return "hello"

app.run()