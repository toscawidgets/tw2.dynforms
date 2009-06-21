import webob as wo, wsgiref.simple_server as wrs, os
import tw2.core as twc, tw2.forms as twf, tw2.dynforms as twd

opts = ['Red', 'Yellow', 'Green', 'Blue']


class TestPage(twf.FormPage):
    title = 'tw2.dynforms example'
    class child(twf.Form):
        class child(twf.TableLayout):
            id = 'xx'
            a = twd.CalendarDatePicker()
            b = twf.CheckBox(validator=twc.Required)
            c = twd.LinkContainer(link='x$', child=twf.SingleSelectField(options=['']+opts))
            #class d(twd.GrowingGridLayout):
            #    value = [{'a':'aaa', 'b':'bbb'}]
            #    a = twf.TextField()
            #    b = twf.TextField()
            class e(twd.HidingTableLayout):
                a = twd.HidingSingleSelectField(options=['']+opts, mapping={'Red':['b'], 'Yellow':['c']})
                b = twf.TextField(validator=twc.Required)
                c = twf.TextField()


def app(environ, start_response):
    req = wo.Request(environ)
    resp = wo.Response(status="404 Not Found")
    return resp(environ, start_response)


if __name__ == "__main__":
    mw = twc.TwMiddleware(app, debug=True)
    mw.controllers.register(TestPage, 'test')
    wrs.make_server('', 8000, mw).serve_forever()
