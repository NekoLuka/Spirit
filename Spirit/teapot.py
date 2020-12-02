from Spirit.responseEncoder import responseEncoder

# Function that returns a teapot status
def teapot() -> responseEncoder:
    data = responseEncoder("418 I'm a teapot")
    data.setData("You tried to brew coffee in a teapot! We don't do that here.")
    return data