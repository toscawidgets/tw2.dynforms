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
    easy_install elixir

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

    class Item(el.Entity):
        order = el.ManyToOne(Order)
        code = el.Field(el.String(50))
        description = el.Field(el.String(200))

Add the following to the ``Order`` class::

    items = el.OneToMany('Item')

Create the new database table::

    >>> from myapp2 import *
    >>> el.metadata.create_all()

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
