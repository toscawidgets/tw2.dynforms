.. tutorial:

tw2.dynforms Tutorial
=====================

Introduction
------------

ToscaWidgets is a framework for creating re-usable web components, called "widgets". tw2.dynforms is a set of ToscaWidgets for creating dynamic forms. This includes dynamically growing grids, form fields that hide or show based on other fields, and several other features.

To demonstrate what tw2.dynforms can do, we're going to walk through creating an internal business application for order tracking. To keep the example simple, some practicalities such as authentication are ignored.


Getting Started
---------------

The best way to install the required packages is using easy_install. Assuming you already have easy_install, you'll need to::

    easy_install tw2.dynforms

To start building our application, lets create ``myapp.py`` with the following content::

    import wsgiref.simple_server as wrs
    import tw2.core as twc, tw2.forms as twf, tw2.dynforms as twd

    mw = twc.TwMiddleware(None, controller_prefix='/')

    class Index(twc.Page):
        title = 'tw2.dynforms Tutorial'
    mw.controllers.register(Index, 'index')

    wrs.make_server('', 8000, mw).serve_forever()

We'll now start the application to check that it works correctly. Issue::

    python myapp.py

In a web browser, go to http://localhost:8000/ If everything worked ok, this will present a "tw2.dynforms Tutorial" message.


Model
-----

The first step is to define the database tables. We'll use Elixir as our object-relational mapper; this is an active record style ORM that builds on SQLAlchemy. Add the following to ``myapp.py``::

    import elixir as el

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

    el.setup_all()

The next step is to actually create the database tables. TBD

We also want to create some test orders, so we have some data to work with later on::

    jb = People(name='Joe Bloggs')
    jd = People(name='Jane Doe')
    sp = Status(name='Pending')
    sd = Status(name='Dispatched')
    Order(name='Garden furniture', status=sp, customer=jb, assignee=jd)
    Order(name='Barbeque', status=sd, customer=jd, assignee=jb)
    session.flush()


Front Page
----------

The front page of the application needs to be a list of orders, so we can update the ``Index`` class as follows::

    class Index(twc.Page):
        class child(twf.GridLayout):
            name = twf.LabelField()
            status = twf.LabelField()
            customer = twf.LabelField()
            assignee = twf.LabelField()

        def fetch_data(self, req):
            self.value = Order.query.all()

With all this done, restart the application, refresh the browser page, and you'll see the list of orders.


Form Editing
------------

Users need to be able to click on an order to get further information. We'll build an inital version of the detail form using ToscaWidgets. Add the following to ``myapp.py``::

    class OrderForm(twf.FormPage):
        class child(twd.CustomisedForm):
            class child(twd.HidingTableLayout):
                id = twf.HiddenField()
                name = twf.TextField()
                status_id = twf.SingleSelectField(options=[str(r) for r in Status.query])
                customer_id = twf.SingleSelectField(options=[str(r) for r in People.query])
                assignee_id = twf.SingleSelectField(options=[str(r) for r in People.query])
                delivery = twf.CheckBox()
                address = twf.TextArea()

        @classmethod
        def request(cls, req, **kw):
            if req.method == 'GET':
                kw['value'] = Order.query.get(req.GET['id'])
            return super(OrderForm, cls).request(req, **kw)

    mw.controllers.register(OrderForm, 'order')

Users will need a link from the front page to the edit page. Update the ``Index`` class and add, at the beginning::

    id = LinkField(link='order?id=$', text='Edit', label=None)

Have a look at this in your browser - you will now be able to navigate from the order list, to the order editing form. To make the form save when you click "submit", add the following to the ``Order`` class::

    @classmethod
    def validated_request(cls, req, data):
        Order.query.get(id).from_dict(data)
        # TBD: redirect

You can now use your browser to edit orders in the system. This arrangement provides the basis for a highly functional system. In particular, validation can easily be added, with the error messages reported in a user-friendly way. It's also easy to adapt this to form a "create new order" function.


Hiding
------

The address field only applies to orders that need delivery; there's no need to show it for other orders. Dynforms helps you build dynamic forms like this, using a set of Hiding controls. In this case, we'll use HidingCheckBox. Change the following line::

    delivery = twf.CheckBox()

to::

    delivery = twd.HidingCheckBox(mapping={1:['address']})

The mapping defines what controls should be visible when the Hiding control has a particular value - in this case, when it is checked, the address field will become visible. Other hiding controls are available, including HidingSingleSelectField and HidingCheckBoxList, and you can also create your own using HidingComponentMixin. Dynforms fully supports nested hiding and other complex arrangements.


Growing
-------

In this application, each Order can contain a number of Items. Most orders will just have a handful, but potentially some orders may have a large number of items. What we really want is a dynamic form that grows spaces to enter items, as needed. Dynforms supports a variety of Growing forms to allow this. To implement this, first we need to add a new database class::

    class Item(Entity):
        order = ManyToOne(Order)
        code = Field(String(50))
        description = Field(String(200))

Also, add the following to the Order class::

    items = OneToMany('Item')

TBD: create tables

To create the corresponding widgets, add this to ``OrderForm``, after address::

    class items(twd.GrowingGridLayout):
        id = twf.HiddenField()
        order_id = twf.HiddenField()
        code = twf.SingleSelectField(options=['Red', 'Blue', 'Green'])
        description = twf.TextField()

Take a look at this in your browser - the growing form provides delete and undo functionality, and it's fun to play with.


Select with Other
-----------------

Over time, users will want to use more status codes for orders, beyond "pending" and "dispatched", such as "awaiting supplier" and "returned". Dynforms provides OtherSingleSelectField, which adds an "other" choice to the list, and when this is selected, prompts the user for a free-text value. To use this, edit controllers.py:

Change

.. code-block:: python

    status_id = twf.SingleSelectField(options=twd.load_options(model.Status), label_text='Status')

to

.. code-block:: python

    status_id = twd.OtherSingleSelectField(dataobj=model.Status, field='name', label_text='Status')

When you try this in your browser, you'll see that once a user enters an "other" value, it is then available in the select field for all users.


Further Customisation
---------------------

To give the site your own look, you can edit the templates to provide your own layout. Customising the appearance of the forms can be done using CSS. If you need more flexibility, you can override widget templates with your own versions.

tw.dynforms has several other features. Cascading fields - when a value is selected in one field, it causes an ajax request that can set the value of others fields. LinkContainer - lets you attach a "view" link to a control, particularly useful with SingleSelectFields and AjaxLookupFields. There's also WriteOnlyTextField for secret data, such as passwords, that the server does not disclose to clients.
