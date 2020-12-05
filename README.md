# Spirit

Spirit is a Python framework inspired on Flask, but with easier configuration.
Spirit is specifically designed with REST in mind, and only useses the python standard library.
This means that there is no specific package to deal with templates for example. The plan is to create a seperate package for Spirit which is dependend on the Jinja2 template engine.
There are features however for custom defined request methods, get variables, post variables and cookies. A database package based upon sqlite3 is present as well with the SQL layer partialy obscured inside the package for a more object oriented experience. There is a class to build a SQL quarry as well.

Sessions are possible, with storage on disk for session variables. These sessions are based on the cookie system from Spirit.

The server currently supports 200, 301, 404, 418 and 500 status codes. It is however very easy to add new ones when needed with the responseEncoder class.
