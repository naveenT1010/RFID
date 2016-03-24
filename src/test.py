import web

urls = (
    '/', 'index'
)

class index:
    def GET(name):
        return "Hello, ", + str(name)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()