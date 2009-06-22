import tw2.core as twc, tw2.forms as twf, datetime as dt

#--
# Miscellaneous widgets
#--

class LinkContainer(twc.DisplayOnlyWidget):
    """This widget provides a "View" link adjacent to any other widget required. This link is visible only when a value is selected, and allows the user to view detailed information on the current selection. The widget must be created with a single child, and the child must have its ID set to None."""
    template = "genshi:tw2.dynforms.templates.link_container"
    resources = [twc.JSLink(modname=__name__, filename='static/dynforms.js')]

    link = twc.Param('The link target. If a $ character is present in the URL, it is replaced with the current value of the widget.')
    view_text = twc.Param('Allows you to override the text string "view"', default='View')

    def prepare(self):
        super(LinkContainer, self).prepare()
        self.child.safe_modify('attrs')
        self.child.attrs['onchange'] = (('twd_link_onchange(this, "%s");' % self.link) +
                                            self.child.attrs.get('onchange', ''))
        self.safe_modify('attrs')
        self.attrs['id'] = self.child.compound_id + ':view'
        if not self.value:
            self.attrs['style'] = 'display:none;' + self.attrs.get('style', '')


class CustomisedForm(twf.Form):
    """A form that allows specification of several useful client-side behaviours."""
    # TBD: make growing not need this
    blank_deleted = twc.Param('Blank out any deleted form fields from GrowingTable on the page. This is required for growing to function correctly - you must use GrowingTableFieldSet within a CustomisedForm with this option set.', default=True)
    # TBD: 'save_prompt': 'If the user navigates away without submitted the form, and there are changes, this will prompt the user.',
    disable_enter = twc.Param('Disable the enter button (except with textarea fields). This reduces the chance of users accidentally submitting the form.', default=True)
    prevent_multi_submit = twc.Param('When the user clicks the submit button, disable it, to prevent the user causing multiple submissions.', default=True)

    resources = [twc.JSLink(modname=__name__, filename="static/dynforms.js")]

    def prepare(self):
        super(CustomisedForm, self).update_params(prepare)
        if self.blank_deleted:
            self.safe_modify('attrs')
            self.attrs['onsubmit'] = 'twd_blank_deleted()'
        if self.disable_enter:
            self.safe_modify('resources')
            self.resources.append(twc.JSSource('document.onkeypress = twd_suppress_enter;'))
        if self.prevent_multi_submit:
            self.safe_modify('submit_attrs')
            self.submit_attrs['onclick'] = 'return twd_no_multi_submit(this)'


class WriteOnlyValidator(twc.Validator):
    def __init__(self, token, *args, **kw):
        super(WriteOnlyValidator, self).__init__(*args, **kw)
        self.token = token
    def to_python(self, value, state=None):
        return value == self.token and twc.EmptyMarker or value

class WriteOnlyTextField(twf.TextField):
    """A text field that is write-only and never reveals database content. If a value exists in the database, a placeholder like "(supplied)" will be substituted. If the user does not modify the value, the validator will return a WriteOnlyMarker instance. Call strip_wo_markers to remove these from the dictionary."""

    token = twc.Param('Text that is displayed instead of the data. This can only be specified at widget creation, not at display time.', default='(supplied)')

    def __init__(self, *args, **kw):
        super(WriteOnlyTextField, self).__init__(*args, **kw)
        self.validator = WriteOnlyValidator(self.token)
    def prepare(self):
        super(WriteOnlyMixin, self).prepare()
        self.value = self.value and self.token


#--
# Growing forms
#--
class DeleteButton(twf.ImageButton):
    """A button to delete a row in a growing form. This is created automatically and would not usually be used directly."""
    attrs = {
        'alt': 'Delete row',
        'onclick': 'twd_grow_del(this); return false;',
    }
    modname = __name__
    filename = 'static/del.png'


class StripBlanks(twc.Validator):
    def any_content(self, val):
        if type(val) == list:
            for v in val:
                if self.any_content(v):
                    return True
            return False
        elif type(val) == dict:
            for k in val:
                if k == 'id':
                    continue
                if self.any_content(val[k]):
                    return True
            return False
        else:
            return bool(val)

    def to_python(self, value):
        return [v for v in value if self.any_content(v)]


class GrowingGridLayout(twf.GridLayout):
    """A GridLayout that can dynamically grow on the client. This is useful for allowing users to enter a list of items that can vary in length. The widgets are presented as a grid, with each field being a column. Delete and undo functionality is provided. To function correctly, the widget must appear inside a CustomisedForm."""

    resources = [twc.JSLink(modname=__name__, filename="static/dynforms.js")]
    validator = StripBlanks()
    template = 'genshi:tw2.dynforms.templates.growing_grid_layout'

    @classmethod
    def post_define(cls):
        if hasattr(cls.child, 'children'):
            if not hasattr(cls.child.children, 'del'): # TBD: 'del' in ...
                cls.child = cls.child(children = list(cls.child.children) + [DeleteButton(id='del', label='')])
        #children.append(twf.HiddenField('id', validator=fe.validators.Int))

    def prepare(self):
        self.value = [None] + self.value
        super(GrowingGridLayout, self).prepare()
        self.repetitions = len(self.value) + 1
        aa = twc.Link(modname=__name__, filename="static/undo.png").req()
        aa.prepare()
        self.undo_url = aa.link
        # First and last rows have delete hidden (and hidingbutton) and get onchange
        for r in (self.children[0], self.children[self.repetitions-1]):
            for c in r.children:
                c.safe_modify('attrs')
                if c.id == 'del':
                    c.attrs['style'] = 'display:none;' + c.attrs.get('style', '')
                else:
                    c.attrs['onchange'] = 'twd_grow_add(this);' + c.attrs.get('onchange', '')
        # First row is hidden
        hidden_row = self.children[0]
        hidden_row.safe_modify('attrs')
        hidden_row.attrs['style'] = 'display:none;' + hidden_row.attrs.get('style', '')

#--
# Hiding forms
#--
class HidingContainerMixin(object):
    """Mixin to add hiding functionality to a container widget. The developer can use multiple inheritence to combine this class with a container widget, e.g. ListFieldSet. For this to work correctly, the container must make use of the container_attrs parameter on child widgets."""

    @classmethod
    def post_define(cls):
        """
        Verify the mapping - check all controls exist and generate cls.hiding_ctrls
        """
        cls.hiding_ctrls = set()
        seen = set()
        for c in getattr(cls, 'children', []):
            seen.add(c.id)
            if issubclass(c, HidingComponentMixin):
                dep_ctrls = set()
                for m in c.mapping.values():
                    dep_ctrls.update(m)
                cls.hiding_ctrls.update(dep_ctrls)
                for d in dep_ctrls:
                    if not hasattr(cls.children, d):
                        raise twc.ParameterError('Widget referenced in mapping does not exist: ' + d)
                    if d in seen:
                        raise twc.ParameterError('Widget mapping references a preceding widget: ' + d)

    def prepare(self):
        super(HidingContainerMixin, self).prepare()
        show = set()
        for c in self.children:
            if isinstance(c, HidingComponentMixin):
                show.update(c.mapping.get(c.value, []))
            if c.id in self.hiding_ctrls and c.id not in show:
                c.safe_modify('container_attrs')
                c.container_attrs['style'] = 'display:none;' + c.container_attrs.get('style', '')

    @twc.validation.catch_errors
    def _validate(self, value):
        self._validated = True
        value = value or {}
        if not isinstance(value, dict):
            raise vd.ValidationError('corrupt', self.validator)
        self.value = value
        any_errors = False
        data = {}
        show = set()
        for c in self.children:
            if c.id in self.hiding_ctrls and c.id not in show:
                data[c.id] = None
            else:
                try:
                    if c._sub_compound:
                        data.update(c._validate(value))
                    else:
                        data[c.id] = c._validate(value.get(c.id))
                        if isinstance(c, HidingComponentMixin):
                            show.update(c.mapping.get(data[c.id], []))
                except twc.ValidationError:
                    data[c.id] = twc.Invalid
                    any_errors = True
        if self.validator:
            data = self.validator.to_python(data)
            self.validator.validate_python(data)
        if any_errors:
            raise twc.ValidationError('childerror', self.validator)
        return data


class HidingTableLayout(HidingContainerMixin, twf.TableLayout):
    """A TableLayout that can contain hiding widgets."""

class HidingListLayout(HidingContainerMixin, twf.ListLayout):
    """A ListLayout that can contain hiding widgets."""

class HidingComponentMixin(object):
    """This widget is a $$ with additional functionality to hide or show other widgets in the form, depending on the value selected. To function correctly, the widget must be used inside a suitable container, e.g. HidingTableForm, and the widget's id must not contain an underscore."""
    javascript = [twc.JSLink(modname=__name__, filename='static/dynforms.js')]

    mapping = twc.Param('Dict that maps selection values to visible controls', request_local=False)

    def prepare(self):
        super(HidingComponentMixin, self).prepare()
        self.safe_modify('resources')
        self.resources.append(
            twc.JSFuncCall(function='twd_hiding_init', args=(self.compound_id, self.mapping)).req())

class HidingSingleSelectField(HidingComponentMixin, twf.SingleSelectField):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'SingleSelectField')
    attrs = {'onchange': 'twd_hiding_onchange(this)'}

class HidingCheckBox(HidingComponentMixin, twf.CheckBox):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'CheckBox')
    attrs = {'onclick': 'twd_hiding_onchange(this)'}

class HidingSelectionList(HidingComponentMixin, twf.SelectionList):
    def prepare(self):
        super(HidingSelectionList, self).prepare()
        for opt in self.options:
            opt[2]['onclick'] = 'twd_hiding_listitem_onchange(this)'

class HidingCheckBoxList(HidingSelectionList, twf.CheckBoxList):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'CheckBoxList')

class HidingRadioButtonList(HidingSelectionList, twf.RadioButtonList):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'RadioButtonList')


class CalendarDatePicker(twf.TextField):
    """
    A JavaScript calendar system for picking dates.
    """
    resources = [
        twc.CSSLink(modname='tw2.dynforms', filename='static/calendar/calendar-system.css'),
        twc.JSLink(modname='tw2.dynforms', filename='static/calendar/calendar.js'),
        twc.JSLink(modname='tw2.dynforms', filename='static/calendar/calendar-setup.js'),
    ]
    language = twc.Param('Short country code for language to use, e.g. fr, de', default='en')
    show_time = twc.Variable('Whether to display the time', default=False)
    value = twc.Param('The default value is the current time', default=twc.Deferred(lambda: dt.datetime.now()))
    validator = twc.Param('To control the date format, specify it in the validator', default=twc.DateValidator)
    template = "genshi:tw2.dynforms.templates.calendar"

    def prepare(self):
        super(CalendarDatePicker, self).prepare()
        self.safe_modify('resources')
        self.resources.extend([
            twc.JSLink(modname='tw2.dynforms', filename='static/calendar/lang/calendar-%s.js' % self.language).req(),
            twc.JSFuncCall(function='Calendar.setup', args=[dict(
                inputField = self.compound_id,
                ifFormat = self.validator.format,
                button = self.compound_id + ':trigger',
                showsTime = self.show_time
            )]).req(),
        ])
        aa = twc.Link(modname='tw2.dynforms', filename='static/office-calendar.png').req()
        aa.prepare()
        self.cal_src = aa.link


class CalendarDateTimePicker(CalendarDatePicker):
    """
    A JavaScript calendar system for picking dates and times.
    """
    validator = twc.DateTimeValidator
    show_time = True
