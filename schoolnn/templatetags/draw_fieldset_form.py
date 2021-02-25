from django.template import Library
from django.template.base import Node, Variable, VariableDoesNotExist

register = Library()


class FieldsetFormNode(Node):
    def __init__(self, variables):
        self.variables = list(map(Variable, variables))
        self.form = self.fieldsets = None

    def render(self, context):
        # No parameters given
        if len(self.variables) < 2:
            return ""

        if len(self.variables) == 2:
            try:
                self.form = self.variables[0].resolve(context)
                self.fieldsets = self.variables[1].resolve(context)
            except VariableDoesNotExist:
                print(
                    "Fieldsets variable or Form variable not set in context."
                )
                return ""

        form_html = []
        append_to_form = form_html.append
        self.form.auto_id = True

        fieldset_template = (
            "<fieldset%(id)s>"
            "<h2><legend>%(legend)s</legend></h2>"
            "%(fields)s"
            "</fieldset>"
        )

        for fieldset in self.fieldsets:
            context = {}
            id = fieldset["id"]
            if id:
                context["id"] = f' id="{id}"'
            else:
                context["id"] = ""

            context["legend"] = fieldset["headline"]
            fields = fieldset["fields"]
            context["fields"] = self.get_fields_html(fields)
            append_to_form(fieldset_template % context)
        return "".join(form_html)

    def get_fields_html(self, fields):
        fields_html = []
        append = fields_html.append
        for field_name in fields:
            field = self.form[field_name]
            help_text = ""
            errors = ""
            if field.help_text:
                help_text = "<span>%s</span>" % field.help_text
            if self.form[field_name].errors:
                errors = str(self.form[field_name].errors)
            append(
                f"{errors}<label for='{field_name}'>{field.label}</label>"
                f"{str(field)} {help_text}"
            )
        return "".join(fields_html)


@register.tag
def draw_fieldset_form(parser, token):
    return FieldsetFormNode(token.split_contents()[1:])
