from django import forms

class CompareForm(forms.Form):
    candidat1 = forms.CharField(widget=Select)
    candidat2 = forms.CharField(widget=Select)
