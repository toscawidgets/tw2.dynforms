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
        self.attrs['id'] = self.child._compound_id() + ':view'
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
    src = twc.Link(modname=__name__, filename="static/del.png")


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


class GrowingGridLayout(object): # twf.GridLayout
    if 0:
        """A grid of input widgets that can dynamically grow on the client. This is useful for allowing users to enter a list of items that can vary in length. The widgets are presented as a grid, with each field being a column. Delete and undo functionality is provided. To function correctly, the widget must appear inside a CustomisedForm."""

        resources = [twc.JSLink(modname=__name__, filename="static/dynforms.js")]
        validator = StripBlanks()

        extra = twc.Variable(default=2) # User shouldn't modify this

        @classmethod
        def post_define(cls):
            # add del/id to child.children
            if not hasattr(cls.child.children, 'del'):
                cls.child.children.append(DeleteButton('del'))
            #children.append(twf.HiddenField('id', validator=fe.validators.Int))

        def prepare(self):
            super(GrowingGridLayout, self).prepare()
            self.undo_url = twc.Link(modname=__name__, filename="static/undo.png").link
            # last two rows have delete hidden (and hidingbutton) and get onchange
            for r in (self.c[-2], self.c[-1]):
                for c in r.c:
                    c.safe_modify('attrs')
                    if c.id == 'del' or isinstance(c, HidingButton):
                        c.attrs['style'] = 'display:none;' + c.attrs.get('style', '')
                    else:
                        c.attrs['onchange'] = 'twd_grow_add(this);' + c.attrs.get('onchange', '')
            # last row is hidden
            self.c[-1].safe_modify('attrs')
            self.c[-1].attrs['style'] = 'display:none;' + self.c[-1].attrs.get('style', '')


#--
# Hiding forms
#--
class HidingContainerMixin(object):
    """Mixin to add hiding functionality to a container widget. The developer can use multiple inheritence to combine this class with a container widget, e.g. ListFieldSet. For this to work correctly, the container must make use of the container_attrs parameter on child widgets."""

    def prepare(self):
        super(HidingContainerMixin, self).prepare()

        # generate children_deep
        # map hiding_root_ids to hiding_root, similarly hiding_ctrls

        visible = self.process_hiding(self.hiding_root, set(self.hiding_root))
        for w in self.hiding_ctrls:
            if w not in visible:
                w.safe_modify('container_attrs')
                w.container_attrs['style'] = 'display:none;' + w.container_attrs.get('style', '')

    def process_hiding(self, widgets, visible):
        for w in widgets:
            if isinstance(w, HidingComponentMixin):
                val = w.value
                for v,cs in w.mapping.iteritems():
                    if w in visible and ((v == val) or (isinstance(val, list) and (v in val))):
                        visible.update(cs)
                    self.process_hiding(cs, visible)
        return visible

    def _validate(self, value):
        1 # !!!

    @classmethod
    def xxpost_define(cls):
        """
        Verify the mapping - check all controls exist and there are no loops
        generate hiding_root and non_hiding
        """
        cls.hiding_ctrls = set()
        parents = {}
        id_stem_len = getattr(cls, 'id', None) and len(cls.id) + 1 or 0
        for c in []: # TBD cls.children_deep:
            if isinstance(c, HidingComponentMixin):
                dep_ctrls = set()
                for m in c.mapping.values():
                    dep_ctrls.update(m)
                cls.hiding_ctrls.update(dep_ctrls)
                for d in dep_ctrls:
                    cur = self
                    for el in d.split('.'):
                        if not cur.children._widget_dct.has_key(el):
                            raise twc.WidgetError('Widget referenced in mapping does not exist: ' + d)
                        cur = cur.children[el]
                    parents.setdefault(d, set())
                    for dd in [d] + list(parents[d]):
                        if dd in parents.get(c._id, []):
                            raise twc.WidgetError('Mapping loop caused by: ' + c.id)
                    parents[d].add(c.id[id_stem_len:])
                    parents[d].update(parents.get(c.id[id_stem_len:], []))
        cls.hiding_root = [c._id for c in cls.children
            if issubclass(c, HidingComponentMixin) and not parents.has_key(c.id)] # TBD id_elem?
        hiding_ctrl_ids = set(x.replace('.', '_') for x in self.hiding_ctrls)
        cls.non_hiding = [(hasattr(c, 'name') and c.name or '')[name_stem_len:] for c in [] # cls.children_deep
                            if (c.id or '')[id_stem_len:] not in hiding_ctrl_ids]


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
        mapping = twc.encode(self.mapping)
        self.safe_modify('resources')
        # TBD: optimise dupes
        self.resources.append(twc.JSSource('twd_mapping_store["%s"] = %s;' % (self.id, mapping)))

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
        a = twc.JSLink(modname='tw2.dynforms', filename='static/calendar/lang/calendar-%s.js' % self.language).req()
        b = twc.JSFuncCall(function='Calendar.setup', args=dict(
            inputField = self._compound_id(),
            ifFormat = self.validator.format,
            button = self._compound_id() + ':trigger',
            showsTime = self.show_time,
        )).req()
        twc.core.request_local().setdefault('resources', set()).update(r for r in (a,b))
        aa = twc.Link(modname='tw2.dynforms', filename='static/office-calendar.png').req()
        aa.prepare()
        self.cal_src = aa.link


class CalendarDateTimePicker(CalendarDatePicker):
    """
    A JavaScript calendar system for picking dates and times.
    """
    validator = twc.DateTimeValidator
    show_time = True
