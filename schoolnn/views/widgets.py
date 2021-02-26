""" The module 'widget' contains all customized widget classes """

from django import forms


class ImageCheckboxWidget(forms.CheckboxSelectMultiple):
    """ Custom CheckBox Widget for selecting multiple images """

    template_name = "widgets/multi_checkbox_widget.html"
