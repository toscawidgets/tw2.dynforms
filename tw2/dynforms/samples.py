import tw2.forms as twf, tw2.dynforms as twd

class DemoGrowingGridLayout(twd.GrowingGridLayout):
    name = twf.TextField()
    phone_number = twf.TextField()
    personal = twf.CheckBox()

class DemoHidingCheckBox(twd.HidingTableLayout):
    demo_for = twd.HidingCheckBox
    delivery = twd.HidingCheckBox(label_text='Delivery required?', mapping={1:['address']})
    address = twf.TextField()

class DemoHidingCheckBoxList(twd.HidingTableLayout):
    demo_for = twd.HidingCheckBoxList
    contact = twd.HidingCheckBoxList(label_text='Contact method', options=('E-mail', 'Phone', 'SMS'),
        mapping={
            'E-mail': ['email_address'],
            'Phone': ['phone_number'],
            'SMS': ['phone_number'],
        })
    email_address = twf.TextField()
    phone_number = twf.TextField()

class DemoHidingRadioButtonList(twd.HidingTableLayout):
    demo_for = twd.HidingRadioButtonList
    contact = twd.HidingRadioButtonList(label_text='Contact method', options=('E-mail', 'Phone', 'SMS'),
        mapping={
            'E-mail': ['email_address'],
            'Phone': ['phone_number'],
            'SMS': ['phone_number'],
        })
    email_address = twf.TextField()
    phone_number = twf.TextField()

class DemoHidingSingleSelectField(twd.HidingTableLayout):
    demo_for = twd.HidingSingleSelectField
    contact = twd.HidingSingleSelectField(label_text='Contact method', options=('E-mail', 'Phone', 'SMS'),
        mapping={
            'E-mail': ['email_address'],
            'Phone': ['phone_number'],
            'SMS': ['phone_number'],
        })
    email_address = twf.TextField()
    phone_number = twf.TextField()

class DemoLinkContainer(twd.LinkContainer):
    child = twf.SingleSelectField(options=('', 'www.google.com','www.yahoo.com'))
    link = 'http://$'
