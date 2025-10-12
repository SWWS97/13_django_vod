from django import forms


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs.update({"class": "form-control"})
            # isinstance(object(검사할 객체), class_or_tuple(비교할 클래스, 또는 클래스들의 튜플)) => True or False
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"rows": 4})
