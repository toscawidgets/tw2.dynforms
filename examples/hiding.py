import webob as wo, wsgiref.simple_server as wrs, os
import tw2.core as twc, tw2.forms as twf, tw2.dynforms as twd

mw = twc.TwMiddleware(None, controller_prefix='/')
opts = ['Red', 'Yellow', 'Green', 'Blue']

class Index(twc.Page):
    title = 'tw2.dynforms Hiding'
    class child(twd.HidingTableLayout):
        delivery = twd.HidingCheckBox(label_text='Delivery required?', mapping={1:['address']})
        address = twf.TextField()

mw.controllers.register(Index, 'index')
wrs.make_server('', 8000, mw).serve_forever()
