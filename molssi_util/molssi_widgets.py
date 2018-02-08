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

from molssi_workflow import units, Q_  # nopep8
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
}

options = {
    'unitentry': {
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


class UnitEntry(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        # label
        self.labeltext = kwargs.get('labeltext', '')
        self.labeltextvariable = kwargs.get('labeltext', None)
        self.labeljustify = kwargs.get('labeljustify', 'right')
        self.labelpadding = kwargs.get('labelpadding', 0)

        # entry
        self.justify = kwargs.get('justify', tk.LEFT)
        self.entrywidth = kwargs.get('entrywidth', 10)

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
        self.label.grid(row=0, column=0, sticky=tk.E)

        self.entry = ttk.Entry(
            self,
            justify=self.justify,
            width=self.entrywidth
        )
        self.entry.grid(row=0, column=1, sticky=tk.EW)

        self.units = ttk.Combobox(
            self,
            height=self.unitsheight,
            width=self.unitswidth,
            state=self.unitsstate
        )
        self.units.grid(row=0, column=2, sticky=tk.W)

        self.config(**kwargs)

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self, value):
        self.set(value)

    def set(self, value):
        """Set the the value and units"""

        self.entry.delete(0, tk.END)
        if value is None:
            return

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
            self.set_units(default_units[str(dimensionality)])
        self.units.set(
            '{0.units:~}'.format(value).replace(' ', '')
        )

    def get(self):
        """return the current value with units"""
        magnitude = float(self.entry.get())
        unit = self.units.get()
        return Q_(magnitude, unit)

    def set_units(self, values=None):
        # logger.debug('set_units: ' + str(values))
        if values is None:
            dimensionality = str(self.get().dimensionality)
            self.units.config(values=default_units[dimensionality])
        else:
            self.units.config(values=values)

    def config(self, **kwargs):
        """Set the configuration of the megawidget"""
        unitentry = options['unitentry']
        label = options['label']
        entry = options['entry']
        unit = options['units']
        for k, v in kwargs.items():
            if k in unitentry and unitentry[k] in self.__dict__:
                self.__dict__[unitentry[k]] = v
            elif k in label:
                self.label.config(**{label[k]: v})
            elif k in entry:
                self.entry.config(**{entry[k]: v})
            elif k in unit:
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

            # Add the widget to the dialog
            self.unit_entry = UnitEntry(
                self.dialog.interior(),
                labeltext='Density',
            )
            self.unit_entry.set(Q_('13.6', 'g/cm**3'))
            self.unit_entry.pack(side="top", fill="both", expand=True)

            def execute(self, result):
                print(result)
                print('{:~P}'.format(self.unit_entry.get()))
                if result not in ('Apply', 'Help'):
                    self.dialog.deactivate(result)
                    root.destroy()

    root = tk.Tk()
    Pmw.initialise(root)
    root.withdraw()
    widget = Example()
    root.mainloop()
