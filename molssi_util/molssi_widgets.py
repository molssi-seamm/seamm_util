# -*- coding: utf-8 -*-

"""A collection of compound Tk/ttk widgets for the MolSSI workflow framework.

The goal of these widgets is twofold: to make it easier for developers
to implement dialogs with compound widgets, and to naturally
standardize the user interface presented to the user.

For example, a common need in molecular simulations is to input a
quantity with units. Typically this would be presented as an
entryfield widget with a label, and followed by a combobox or pulldown
menu with possible units.  For example, to specify a temperature for
e.g. MD, the dialog might present something like

    Temperature: [           ] K
                               C
                               F

where the KCF is the units pulldown. In native Tk/ttk this requires
two or three widgets: a label, an entryfield and e.g. a combobox for
the units. It might be possible to use the label on the entryfield,
but often it is not possible to line up the labels nicely for a clean,
tabular style.
"""

# from molssi_workflow import ureg
from molssi_workflow import Q_, units_class  # nopep8
import logging
import Pmw
import tkinter as tk
import tkinter.ttk as ttk

logger = logging.getLogger(__name__)


default_units = {
    '[length]': ['Å', 'pm', 'nm', 'um'],
    '[length] ** 3': ['Å**3', 'pm**3', 'nm**3', 'um**3'],
    '[mass]': ['g', 'kg', 'tonne', 'lb', 'ton'],
    '[substance]': ['mol'],
    '[temperature]': ['K', 'degC', 'degF', 'degR'],
    '[mass] / [length] ** 3': ['g/mL', 'kg/L', 'kg/m**3', 'g/mol/Å**3'],  # nopep8
    '[time]': ['fs', 'ps', 'ns', 'us', 'ms', 's'],
    '[length] * [mass] / [substance] / [time] ** 2': ['kcal/mol/Å', 'kJ/mol/Å', 'eV/Å'],  # nopep8
    '[length] * [mass] / [time] ** 2': ['kcal/mol/Å', 'kJ/mol/Å', 'eV/Å'],  # nopep8
    '[length] / [time] ** 2': ['m/s**2', 'ft/s**2', 'Å/fs**2'],
    '[mass] / [length] / [time] ** 2': ['Pa', 'atm', 'bar', 'psi', 'ksi'],
}

options = {
    'labeledentry': {
        'variable': 'variable'
    },
    'labeledcombobox': {
        'variable': 'variable'
    },
    'unitentry': {
        'as_quantity': 'as_quantity',
        'variable': 'variable'
    },
    'unitcombobox': {
        'as_quantity': 'as_quantity',
        'variable': 'variable'
    },
    'label': {
        'labelanchor': 'anchor',
        'labelbackground': 'background',
        'labelborderwidth': 'borderwidth',
        'class_': 'class_',
        'compound': 'compound',
        'cursor': 'cursor',
        'labelfont': 'font',
        'labelforeground': 'foreground',
        'labelimage': 'image',
        'labeljustify': 'justify',
        'labelpadding': 'padding',
        'labelrelief': 'relief',
        'style': 'style',
        'labeltakefocus': 'takefocus',
        'labeltext': 'text',
        'labeltextvariable': 'textvariable',
        'labelunderline': 'underline',
        'labelwidth': 'width',
        'labelwraplength': 'wraplength',
    },
    'checkbutton': {
        'class_': 'class_',
        'command': 'command',
        'compound': 'compound',
        'cursor': 'cursor',
        'image': 'image',
        'offvalue': 'offvalue',
        'onvalue': 'onvalue',
        'style': 'style',
        'takefocus': 'takefocus',
        'text': 'text',
        'textvariable': 'textvariable',
        'underline': 'underline',
        'variable': 'variable',
        'width': 'width',
    },
    'entry': {
        'class_': 'class_',
        'cursor': 'cursor',
        'exportselection': 'exportselection',
        'font': 'font',
        'invalidcommand': 'invalidcommand',
        'justify': 'justify',
        'show': 'show',
        'style': 'style',
        'takefocus': 'takefocus',
        'textvariable': 'textvariable',
        'validate': 'validate',
        'validatecommand': 'validatecommand',
        'width': 'width',
        'xscrollcommand': 'xscrollcommand'
    },
    'combobox': {
        'class_': 'class_',
        'cursor': 'cursor',
        'exportselection': 'exportselection',
        'justify': 'justify',
        'height': 'height',
        'postcommand': 'postcommand',
        'state': 'state',
        'style': 'style',
        'takefocus': 'takefocus',
        'textvariable': 'textvariable',
        'values': 'values',
        'width': 'width'
    },
    'units': {
        'class_': 'class_',
        'cursor': 'cursor',
        'exportselection': 'exportselection',
        'unitsheight': 'height',
        'unitsjustify': 'justify',
        'postcommand': 'postcommand',
        'style': 'style',
        'unitstakefocus': 'takefocus',
        'unitstextvariable': 'textvariable',
        'unitsvalidate': 'validate',
        'unitsvalidatecommand': 'validatecommand',
        'unitswidth': 'width',
        'unitsxscrollcommand': 'xscrollcommand',
    }
}


def align_labels(widgets, sticky=None):
    """Align the labels of a given list of widgets"""
    if len(widgets) <= 1:
        return

    widgets[0].update_idletasks()

    # Determine the size of the maximum length label string.
    max_width = 0
    for widget in widgets:
        width = widget.grid_bbox(0, 0)[2]
        if width > max_width:
            max_width = width

    # Adjust the margins for the labels such that the child sites and
    # labels line up.
    for widget in widgets:
        if sticky is not None:
            widget.label.grid(sticky=sticky)
        widget.grid_columnconfigure(0, minsize=max_width)


class LabeledEntry(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        self.variable = kwargs.get('variable', None)
        
        # label
        self.labeltext = kwargs.get('labeltext', '')
        self.labeltextvariable = kwargs.get('labeltext', None)
        self.labeljustify = kwargs.get('labeljustify', 'right')
        self.labelpadding = kwargs.get('labelpadding', 0)

        self.label = ttk.Label(
            self,
            text=self.labeltext,
            justify=self.labeljustify,
            padding=self.labelpadding
        )

        # entry
        self.justify = kwargs.get('justify', tk.LEFT)
        self.entrywidth = kwargs.get('width', 15)

        self.entry = ttk.Entry(
            self,
            justify=self.justify,
            width=self.entrywidth
        )

        self.show('all')
        self.config(**kwargs)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def show(self, *args):
        """Show only the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        for slave in self.grid_slaves():
            slave.grid_forget()

        show_all = (len(args) == 0 or args[0] == 'all')
        
        if show_all or 'label' in args:
            self.label.grid(row=0, column=0, sticky=tk.E)

        if show_all or 'entry' in args:
            self.entry.grid(row=0, column=1, sticky=tk.EW)
            
    def set(self, value):
        """Set the value of the entry widget"""

        self.entry.delete(0, tk.END)
        if value is None:
            return

        self.entry.insert(0, value)

    def get(self):
        """return the current value"""
        value = self.entry.get()
        return value

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        labeledentry = options['labeledentry']
        label = options['label']
        entry = options['entry']
        for k, v in kwargs.items():
            if k in labeledentry and labeledentry[k] in self.__dict__:
                self.__dict__[labeledentry[k]] = v
            elif k in label:
                self.label.config(**{label[k]: v})
            elif k in entry:
                self.entry.config(**{entry[k]: v})
            else:
                raise RuntimeError("Unknown option '{}'".format(k))


class LabeledComboBox(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        # labeledcombobox
        self.variable = kwargs.get('variable', None)
        
        # label
        self.labeltext = kwargs.get('labeltext', '')
        self.labeltextvariable = kwargs.get('labeltext', None)
        self.labeljustify = kwargs.get('labeljustify', 'right')
        self.labelpadding = kwargs.get('labelpadding', 0)

        self.label = ttk.Label(
            self,
            text=self.labeltext,
            justify=self.labeljustify,
            padding=self.labelpadding
        )

        # combobox
        self.height = kwargs.get('height', 7)
        self.width = kwargs.get('width', 20)
        self.state = kwargs.get('state', 'normal')

        self.combobox = ttk.Combobox(
            self,
            height=self.height,
            width=self.width,
            state=self.state
        )

        self.show('all')
        self.config(**kwargs)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def show(self, *args):
        """Show only the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        for slave in self.grid_slaves():
            slave.grid_forget()

        show_all = (len(args) == 0 or args[0] == 'all')
        
        if show_all or 'label' in args:
            self.label.grid(row=0, column=0, sticky=tk.E)

        if show_all or 'combobox' in args:
            self.combobox.grid(row=0, column=1, sticky=tk.EW)

    def set(self, value):
        """Set the value of the widget"""

        if value is None:
            return

        self.combobox.set(value)

    def get(self):
        """return the current value"""
        value = self.combobox.get()
        return value

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        labeledcombobox = options['labeledcombobox']
        label = options['label']
        combobox = options['combobox']
        for k, v in kwargs.items():
            if k in labeledcombobox and labeledcombobox[k] in self.__dict__:
                self.__dict__[labeledcombobox[k]] = v
            elif k in label:
                self.label.config(**{label[k]: v})
            elif k in combobox:
                self.combobox.config(**{combobox[k]: v})
            else:
                raise RuntimeError("Unknown option '{}'".format(k))


class UnitEntry(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        # unitentry
        self.as_quantity = kwargs.get('as_quantity', False)
        self.variable = kwargs.get('variable', None)
        
        # label
        self.labeltext = kwargs.get('labeltext', '')
        self.labeltextvariable = kwargs.get('labeltext', None)
        self.labeljustify = kwargs.get('labeljustify', 'right')
        self.labelpadding = kwargs.get('labelpadding', 0)

        # entry
        self.justify = kwargs.get('justify', tk.LEFT)
        self.entrywidth = kwargs.get('width', 15)

        # combobox
        self.unitsheight = kwargs.get('unitsheight', 7)
        self.unitswidth = kwargs.get('unitswidth', 10)
        self.unitsstate = kwargs.get('unitsstate', 'readonly')

        self.label = ttk.Label(
            self,
            text=self.labeltext,
            justify=self.labeljustify,
            padding=self.labelpadding
        )

        self.entry = ttk.Entry(
            self,
            justify=self.justify,
            width=self.entrywidth
        )

        self.units = ttk.Combobox(
            self,
            height=self.unitsheight,
            width=self.unitswidth,
            state=self.unitsstate
        )

        self.show('all')
        self.config(**kwargs)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def show(self, *args):
        """Show only the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        for slave in self.grid_slaves():
            slave.grid_forget()

        show_all = (len(args) == 0 or args[0] == 'all')
        
        if show_all or 'label' in args:
            self.label.grid(row=0, column=0, sticky=tk.E)

        if show_all or 'entry' in args:
            self.entry.grid(row=0, column=1, sticky=tk.EW)

        if show_all or 'units' in args:
            self.units.grid(row=0, column=2, sticky=tk.W)
            
    def set(self, value, unit_string=None):
        """Set the the value and units"""

        self.entry.delete(0, tk.END)
        if value is None:
            return

        # the value may have units or be a plain value
        if isinstance(value, units_class):
            self.entry.insert(0, value.magnitude)

            dimensionality = value.dimensionality
            current_units = self.units.cget('values')
            if len(current_units) > 0:
                for unit in current_units:
                    if Q_(unit).dimensionality != dimensionality:
                        self.units.configure(values=[])
                        current_units = []
                        break

            if len(current_units) == 0:
                self.set_units([*default_units[str(dimensionality)], ''])
                self.units.set(
                    '{0.units:~}'.format(value).replace(' ', '')
                )
        elif unit_string:
            self.entry.insert(0, value)

            dimensionality = Q_(unit_string).dimensionality
            current_units = self.units.cget('values')
            if len(current_units) > 0:
                for unit in current_units:
                    if Q_(unit).dimensionality != dimensionality:
                        self.units.configure(values=[])
                        current_units = []
                        break

            if len(current_units) == 0:
                self.set_units([*default_units[str(dimensionality)], ''])
                self.units.set(unit_string)
        else:
            self.entry.insert(0, value)
            self.set_units('all')
            self.units.set('')

    def get(self):
        """return the current value with units"""
        value = self.entry.get()
        unit = self.units.get()
        if unit == '':
            return value
        elif self.as_quantity:
            try:
                magnitude = float(value)
                return Q_(magnitude, unit)
            except:
                return (value, unit)
        else:
            return (value, unit)

    def set_units(self, values=None):
        # logger.debug('set_units: ' + str(values))
        if values is None:
            dimensionality = str(self.get().dimensionality)
            self.units.config(values=default_units[dimensionality])
        elif values == 'all':
            tmp = ['']
            for key in default_units:
                tmp += default_units[key]
            self.units.config(values=tmp)
        else:
            self.units.config(values=values)

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        unitentry = options['unitentry']
        label = options['label']
        entry = options['entry']
        units = options['units']
        for k, v in kwargs.items():
            if k in unitentry and unitentry[k] in self.__dict__:
                self.__dict__[unitentry[k]] = v
            elif k in label:
                self.label.config(**{label[k]: v})
            elif k in entry:
                self.entry.config(**{entry[k]: v})
            elif k in units:
                self.units.config(**{units[k]: v})
            else:
                raise RuntimeError("Unknown option '{}'".format(k))


class UnitComboBox(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        # unitcombobox
        self.as_quantity = kwargs.get('as_quantity', False)
        self.variable = kwargs.get('variable', None)
        
        # label
        self.labeltext = kwargs.get('labeltext', '')
        self.labeltextvariable = kwargs.get('labeltext', None)
        self.labeljustify = kwargs.get('labeljustify', 'right')
        self.labelpadding = kwargs.get('labelpadding', 0)

        # combobox
        self.height = kwargs.get('height', 7)
        self.width = kwargs.get('width', 20)
        self.state = kwargs.get('state', 'normal')

        # units combobox
        self.unitsheight = kwargs.get('unitsheight', 7)
        self.unitswidth = kwargs.get('unitswidth', 10)
        self.unitsstate = kwargs.get('unitsstate', 'readonly')

        self.label = ttk.Label(
            self,
            text=self.labeltext,
            justify=self.labeljustify,
            padding=self.labelpadding
        )

        self.combobox = ttk.Combobox(
            self,
            height=self.height,
            width=self.width,
            state=self.state
        )

        self.units = ttk.Combobox(
            self,
            height=self.unitsheight,
            width=self.unitswidth,
            state=self.unitsstate
        )

        self.show('all')
        self.config(**kwargs)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def show(self, *args):
        """Show only the specified subwidgets.
        'all' or no arguments reverts to showing all"""

        for slave in self.grid_slaves():
            slave.grid_forget()

        show_all = (len(args) == 0 or args[0] == 'all')
        
        if show_all or 'label' in args:
            self.label.grid(row=0, column=0, sticky=tk.E)

        if show_all or 'combobox' in args:
            self.combobox.grid(row=0, column=1, sticky=tk.EW)

        if show_all or 'units' in args:
            self.units.grid(row=0, column=2, sticky=tk.W)

    def set(self, value, unit_string=None):
        """Set the the value and units"""

        if value is None:
            return

        # the value may have units or be a plain value
        if isinstance(value, units_class):
            self.combobox.set(value.magnitude)

            dimensionality = value.dimensionality
            current_units = self.units.cget('values')
            if len(current_units) > 0:
                for unit in current_units:
                    if Q_(unit).dimensionality != dimensionality:
                        self.units.configure(values=[])
                        current_units = []
                        break

            if len(current_units) == 0:
                self.set_units([*default_units[str(dimensionality)], ''])
                self.units.set(
                    '{0.units:~}'.format(value).replace(' ', '')
                )
        elif unit_string:
            self.combobox.set(value)

            dimensionality = Q_(unit_string).dimensionality
            current_units = self.units.cget('values')
            if len(current_units) > 0:
                for unit in current_units:
                    if Q_(unit).dimensionality != dimensionality:
                        self.units.configure(values=[])
                        current_units = []
                        break

            if len(current_units) == 0:
                self.set_units([*default_units[str(dimensionality)], ''])
                self.units.set(unit_string)
        else:
            self.combobox.set(value)
            self.set_units('all')
            self.units.set('')

    def get(self):
        """return the current value with units"""
        value = self.combobox.get()
        if value in self.combobox.cget('values'):
            return value
        else:
            unit = self.units.get()
            if unit == '':
                return value
            elif self.as_quantity:
                try:
                    magnitude = float(value)
                    return Q_(magnitude, unit)
                except:
                    return (value, unit)
            else:
                return (value, unit)

    def set_units(self, values=None):
        # logger.debug('set_units: ' + str(values))
        if values is None:
            dimensionality = str(self.get().dimensionality)
            self.units.config(values=default_units[dimensionality])
        elif values == 'all':
            tmp = ['']
            for key in default_units:
                tmp += default_units[key]
            self.units.config(values=tmp)
        else:
            self.units.config(values=values)

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        unitcombobox = options['unitcombobox']
        label = options['label']
        combobox = options['combobox']
        units = options['units']
        for k, v in kwargs.items():
            if k in unitcombobox and unitcombobox[k] in self.__dict__:
                self.__dict__[unitcombobox[k]] = v
            elif k in label:
                self.label.config(**{label[k]: v})
            elif k in combobox:
                self.combobox.config(**{combobox[k]: v})
            elif k in units:
                self.units.config(**{units[k]: v})
            else:
                raise RuntimeError("Unknown option '{}'".format(k))


if __name__ == '__main__':
    # Create demo in root window for testing.
    class Example(object):
        def __init__(self):
            # Create the dialog.
            self.dialog = Pmw.Dialog(
                root,
                buttons=('OK', 'Apply'),
                defaultbutton='OK',
                title='Unit entry',
                command=self.execute)

            # Add the widgets to the dialog
            self.unit_entry = UnitEntry(
                self.dialog.interior(),
                labeltext='Density',
            )
            self.unit_entry.set(Q_('13.6', 'g/cm**3'))
            self.unit_entry.pack(side="top", fill="both", expand=True)

            self.unit_combobox = UnitComboBox(
                self.dialog.interior(),
                labeltext='Density',
            )
            self.unit_combobox.set(Q_('13.6', 'g/cm**3'))
            self.unit_combobox.pack(side="top", fill="both", expand=True)

        def execute(self, result):
            value = self.unit_entry.get()
            if isinstance(value, units_class):
                print('Entry: {:~P}'.format(value))
            else:
                print('Entry: {}'.format(value))

            value = self.unit_combobox.get()
            if isinstance(value, units_class):
                print('Combobox: {:~P}'.format(value))
            else:
                print('Combobox: {}'.format(value))

            if result not in ('Apply', 'Help'):
                self.dialog.deactivate(result)
                root.destroy()

    root = tk.Tk()
    Pmw.initialise(root)
    root.withdraw()
    widget = Example()
    root.mainloop()
