import wsgiref.simple_server as wrs
import tw2.core as twc, tw2.forms as twf, tw2.dynforms as twd

import elixir as el
el.metadata.bind = 'sqlite:///myapp.db'
el.options_defaults['shortnames'] = True


class People(el.Entity):
    name = el.Field(el.String(100))
    email = el.Field(el.String(100))
    def __str__(self):
        return self.name

class Status(el.Entity):
    name = el.Field(el.String(100))
    def __str__(self):
        return self.name

class Order(el.Entity):
    name = el.Field(el.String(100))
    status = el.ManyToOne(Status)
    customer = el.ManyToOne(People)
    assignee = el.ManyToOne(People)
    delivery = el.Field(el.Boolean)
    address = el.Field(el.String(200))
    items = el.OneToMany('Item')

class Item(el.Entity):
    order = el.ManyToOne(Order)
    code = el.Field(el.String(50))
    description = el.Field(el.String(200))

el.setup_all()



mw = twc.TwMiddleware(None, controller_prefix='/')

class Index(twc.Page):
    title = 'Orders'
    class child(twf.GridLayout):
        id = twf.LinkField(link='order?id=$', text='Edit', label=None)
        name = twf.LabelField()
        status = twf.LabelField()
        customer = twf.LabelField()
        assignee = twf.LabelField()

    def fetch_data(self, req):
        self.value = Order.query.all()

mw.controllers.register(Index, 'index')


class OrderForm(twf.FormPage):
    title = 'Order'
    class child(twd.CustomisedForm):
        class child(twd.HidingTableLayout):
            id = twf.HiddenField()
            name = twf.TextField()
            status_id = twf.SingleSelectField(options=[str(r) for r in Status.query.all()])
            customer_id = twf.SingleSelectField(options=[str(r) for r in People.query.all()])
            assignee_id = twf.SingleSelectField(options=[str(r) for r in People.query.all()])
            delivery = twd.HidingCheckBox(mapping={1:['address']})
            address = twf.TextArea()
            class items(twd.GrowingGridLayout):
                id = twf.HiddenField()
                order_id = twf.HiddenField()
                code = twf.SingleSelectField(options=['Red', 'Blue', 'Green'])
                description = twf.TextField()

    def fetch_data(self, req):
        self.value = Order.query.get(req.GET['id'])

mw.controllers.register(OrderForm, 'order')

if __name__ == '__main__':
    wrs.make_server('', 8000, mw).serve_forever()
