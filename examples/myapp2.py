import wsgiref.simple_server as wrs
import tw2.core as twc, tw2.forms as twf, tw2.dynforms as twd

mw = twc.TwMiddleware(None, controller_prefix='/')

class Index(twc.Page):
    title = 'tw2.dynforms Tutorial'
mw.controllers.register(Index, 'index')

wrs.make_server('', 8000, mw).serve_forever()
