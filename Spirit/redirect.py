from Spirit.responseEncoder import responseEncoder

# Function to redirect the user to another page
def redirect(url: str="/") -> responseEncoder:
    data = responseEncoder("301 Moved Permanently")
    data.setHeader("Location", url)
    data.setData("301 Moved Permanently")
    return data