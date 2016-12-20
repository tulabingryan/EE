from django import forms

class loginForm(forms.Form):
	# name = forms.CharField()
	ID = forms.CharField()

class responseForm(forms.Form):
	response = forms.FloatField()

class hiddenForm(forms.Form):
	ID = forms.CharField(label='ID', max_length=256, widget=forms.HiddenInput()) 
	response_key = forms.IntegerField(label='KEY', widget=forms.HiddenInput()) 