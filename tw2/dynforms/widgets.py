import tw2.core as twc, tw2.forms as twf, datetime as dt

#--
# Growing
#--
class DeleteButton(twf.ImageButton):
    """A button to delete a row in a growing grid. This is created automatically and would not usually be used directly."""
    attrs = {
        'onclick': 'twd_grow_del(this); return false;',
    }
    modname = __name__
    filename = 'static/del.png'
    alt = 'Delete row'
    validator = twc.BlankValidator


class GrowingGridLayout(twf.GridLayout):
    """A GridLayout that can dynamically grow on the client, with delete and undo functionality. This is useful for allowing users to enter a list of items that can vary in length. To function correctly, the widget must appear inside a CustomisedForm."""
    resources = [
        twc.Link(id='undo', modname=__name__, filename="static/undo.png"),
        twc.JSLink(modname=__name__, filename="static/dynforms.js"),
    ]
    template = 'genshi:tw2.dynforms.templates.growing_grid_layout'

    # TBD: support these properly & min/max
    repetitions = twc.Variable()
    extra_reps = twc.Variable(default=1)
    mix_reps = twc.Variable()
    max_reps = twc.Variable()

    @classmethod
    def post_define(cls):
        if hasattr(cls.child, 'children'):
            if not hasattr(cls.child.children, 'del'): # TBD: 'del' in ...
                cls.child = cls.child(children = list(cls.child.children) + [DeleteButton(id='del', label='')])

    def prepare(self):
        if not hasattr(self, '_validated'):
            self.value = [None] + (self.value or [])
        super(GrowingGridLayout, self).prepare()
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

    def _validate(self, value, state=None):
        value = [v for v in value if not ('del.x' in v and 'del.y' in v)]
        return twc.RepeatingWidget._validate(self, [None] + twf.StripBlanks().to_python(value), state)[1:]


#--
# Hiding
#--
class HidingComponentMixin(twc.Widget):
    """This widget is a $$ with additional functionality to hide or show other widgets in the form, depending on the value selected. The widget must be used inside a hiding container, e.g. HidingTableLayout."""
    resources = [twc.JSLink(modname=__name__, filename='static/dynforms.js')]

    mapping = twc.Param('A dictionary that maps selection values to visible controls', request_local=False)

    def prepare(self):
        super(HidingComponentMixin, self).prepare()
        self.safe_modify('resources')
        self.add_call(twc.js_function('twd_hiding_init')(
            self.compound_id, self.mapping))

class HidingSingleSelectField(HidingComponentMixin, twf.SingleSelectField):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'SingleSelectField')
    attrs = {'onchange': 'twd_hiding_onchange(this)'}

class HidingCheckBox(HidingComponentMixin, twf.CheckBox):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'CheckBox')
    attrs = {'onclick': 'twd_hiding_onchange(this)'}

class HidingSelectionList(HidingComponentMixin, twf.widgets.SelectionList):
    def prepare(self):
        super(HidingSelectionList, self).prepare()
        for opt in self.options:
            opt[0]['onclick'] = 'twd_hiding_listitem_onchange(this);' + opt[0].get('onclick', '')

class HidingCheckBoxList(HidingSelectionList, twf.CheckBoxList):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'CheckBoxList')

class HidingRadioButtonList(HidingSelectionList, twf.RadioButtonList):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'RadioButtonList')

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
                if isinstance(c.value, list):
                    for v in c.value:
                        show.update(c.mapping.get(v, []))
                else:
                    show.update(c.mapping.get(c.value, []))
            if c.id in self.hiding_ctrls and c.id not in show:
                c.safe_modify('container_attrs')
                c.container_attrs['style'] = 'display:none;' + c.container_attrs.get('style', '')

    @twc.validation.catch_errors
    def _validate(self, value, state=None):
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
                        data.update(c._validate(value, data))
                    else:
                        data[c.id] = c._validate(value.get(c.id), data)
                        if isinstance(c, HidingComponentMixin):
                            show.update(c.mapping.get(data[c.id], []))
                except twc.ValidationError:
                    data[c.id] = twc.Invalid
                    any_errors = True
        if self.validator:
            data = self.validator.to_python(data, state)
            self.validator.validate_python(data, state)
        if any_errors:
            raise twc.ValidationError('childerror', self.validator)
        return data


class HidingTableLayout(HidingContainerMixin, twf.TableLayout):
    """A TableLayout that can contain hiding widgets."""

class HidingListLayout(HidingContainerMixin, twf.ListLayout):
    """A ListLayout that can contain hiding widgets."""

#--
# Miscellaneous widgets
#--
class CalendarDatePicker(twf.widgets.InputField):
    """
    A JavaScript calendar system for picking dates. The date format can be configured on the validator.
    """
    resources = [
        twc.CSSLink(modname='tw2.dynforms', filename='static/calendar/calendar-system.css'),
        twc.JSLink(modname='tw2.dynforms', filename='static/calendar/calendar.js'),
        twc.JSLink(modname='tw2.dynforms', filename='static/calendar/calendar-setup.js'),
        twc.Link(id='cal', modname='tw2.dynforms', filename='static/office-calendar.png'),
    ]
    language = twc.Param('Short country code for language to use, e.g. fr, de', default='en')
    show_time = twc.Variable('Whether to display the time', default=False)
    value = twc.Param('The default value is the current date/time', default=None)
    validator = twc.DateValidator
    template = "genshi:tw2.dynforms.templates.calendar"
    type = 'text'

    def prepare(self):

        if not self.value:
            # XXX -- Doing this instead of twc.Deferred consciously.
            # twc.Deferred is/was nice, but the execution in post_define(...) of
            #   cls._deferred = [k for k, v in cls.__dict__.iteritems()
            #                    if isinstance(v, pm.Deferred)]
            # with dir(..) instead of vars(..) is too costly.  This is the only
            # place I'm aware of that actually uses deferred params. - threebean
            self.value = dt.datetime.now()

        super(CalendarDatePicker, self).prepare()

        self.safe_modify('resources')
        self.resources.extend([
            twc.JSLink(parent=self.__class__, modname='tw2.dynforms', filename='static/calendar/lang/calendar-%s.js' % self.language),
        ])
        self.add_call(twc.js_function('Calendar.setup')(dict(
            inputField = self.compound_id,
            ifFormat = self.validator.format,
            button = self.compound_id + ':trigger',
            showsTime = self.show_time
        )))


class CalendarDateTimePicker(CalendarDatePicker):
    """
    A JavaScript calendar system for picking dates and times.
    """
    validator = twc.DateTimeValidator
    show_time = True


class LinkContainer(twc.DisplayOnlyWidget):
    """This widget provides a "View" link adjacent to any other widget required. This link is visible only when a value is selected, and allows the user to view detailed information on the current selection."""
    template = "genshi:tw2.dynforms.templates.link_container"
    resources = [twc.JSLink(modname=__name__, filename='static/dynforms.js')]

    link = twc.Param('The link target. If a $ character is present in the URL, it is replaced with the current value of the widget.')
    view_text = twc.Param('Text to appear in the link', default='View')
    id_suffix = 'view'

    def prepare(self):
        super(LinkContainer, self).prepare()
        self.child.safe_modify('attrs')
        self.child.attrs['onchange'] = (('twd_link_onchange(this, "%s");' % self.link) +
                                            self.child.attrs.get('onchange', ''))
        if not self.child.value:
            self.attrs['style'] = 'display:none;' + self.attrs.get('style', '')


class CustomisedForm(twf.Form):
    """A form that allows specification of several useful client-side behaviours."""
    blank_deleted = twc.Param('Blank out any invisible form fields before submitting. This is needed for GrowingGrid.', default=True)
    disable_enter = twc.Param('Disable the enter button (except with textarea fields). This reduces the chance of users accidentally submitting the form.', default=True)
    prevent_multi_submit = twc.Param('When the user clicks the submit button, disable it, to prevent the user causing multiple submissions.', default=True)

    resources = [twc.JSLink(modname=__name__, filename="static/dynforms.js")]

    def prepare(self):
        super(CustomisedForm, self).prepare()
        if self.blank_deleted:
            self.safe_modify('attrs')
            self.attrs['onsubmit'] = 'twd_blank_deleted()'
        if self.disable_enter:
            self.safe_modify('resources')
            self.resources.append(twc.JSSource(src='document.onkeypress = twd_suppress_enter;'))
        if self.prevent_multi_submit:
            self.submit.safe_modify('attrs')
            self.submit.attrs['onclick'] = 'return twd_no_multi_submit(this);'


class CustomisedTableForm(CustomisedForm, twf.TableForm):
    pass
