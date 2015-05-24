from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url


class UIHandler(RequestHandler):
    def get(self):
        self.render("index.html")


class VideoHandler(RequestHandler):
    def get(self):
        with open('video.mp4', 'rb') as vid:
        #with open('video.mkv', 'rb') as vid:
            self.set_header('Content-Type', 'video/mp4')
            self.write(vid.read())
            #count = 1
            #while True:
                #chunk = vid.read(8*1024*10)
                #if not chunk:
                    #break
                #print('chunk %d written' % count)
                #count += 1
                #self.write(chunk)
                #self.flush()
            self.finish()


def make_app():
    return Application([
        url(r"/", UIHandler),
        url(r"/video.mkv", VideoHandler),
    ], static_path='static')


def main():
    app = make_app()
    app.listen(8000)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
