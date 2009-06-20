# Here you can create samples of your widgets by providing default parameters,
# inserting them in a container widget, mixing them with other widgets, etc...
# These samples will appear in the (unimplemented yet) widget browser.
import tw.forms as twf, tw.dynforms as twd, formencode as fe

class DemoGrowingTableForm(twd.GrowingTableForm):
    demo_for = twd.GrowingTableForm
    children = [
        twf.TextField('name'),
        twf.TextField('phone_number'),
        twf.CheckBox('personal'),
    ]

class DemoGrowingTableFieldSet(twd.GrowingTableFieldSet):
    demo_for = twd.GrowingTableFieldSet
    children = [
        twf.TextField('name'),
        twf.TextField('phone_number'),
        twf.CheckBox('personal'),
    ]

class DemoHidingButton(twf.FieldSet):
    demo_for = twd.HidingButton
    children = [
        twd.HidingButton('show'),
        twf.Label('show_1', attrs={'style':'display:none'}),
    ]

class DemoHidingCheckBox(twd.HidingTableFieldSet):
    demo_for = twd.HidingCheckBox
    children = [
        twd.HidingCheckBox('delivery', label_text='Delivery required?', mapping={1:['address']}),
        twf.TextField('address')
    ]
    
class DemoHidingCheckBoxList(twd.HidingTableFieldSet):
    demo_for = twd.HidingCheckBoxList
    children = [
        twd.HidingCheckBoxList('contact', label_text='Contact method', options=('E-mail', 'Phone', 'SMS'), 
            mapping={
                0: ['email_address'],
                1: ['phone_number'],
                2: ['phone_number'],
            }),
        twf.TextField('email_address'),
        twf.TextField('phone_number'),
    ]

class DemoHidingRadioButtonList(twd.HidingTableFieldSet):
    demo_for = twd.HidingRadioButtonList
    children = [
        twd.HidingRadioButtonList('contact', label_text='Contact method', options=('E-mail', 'Phone', 'SMS'), 
            mapping={            
                0: ['email_address'],
                1: ['phone_number'],
                2: ['phone_number'],
            }),
        twf.TextField('email_address'),
        twf.TextField('phone_number'),
    ]

class DemoHidingSingleSelectField(twd.HidingTableFieldSet):
    demo_for = twd.HidingSingleSelectField
    children = [
        twd.HidingSingleSelectField('contact', label_text='Contact method', options=[('',''), (0,'E-mail'), (1,'Phone'), (2,'SMS')],
            mapping={
                0: ['email_address'],
                1: ['phone_number'],
                2: ['phone_number'],
            }),
        twf.TextField('email_address'),
        twf.TextField('phone_number'),
    ]

class DemoOtherSingleSelectField(twd.OtherSingleSelectField):
    demo_for = twd.OtherSingleSelectField
    options = [(0,'Male'), (1,'Female')]
    
class DemoLinkContainer(twd.LinkContainer):
    demo_for = twd.LinkContainer
    children = [twf.SingleSelectField('widget', options=('', 'www.google.com','www.yahoo.com'))]
    link = 'http://$'
