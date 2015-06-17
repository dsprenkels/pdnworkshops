from django.forms import ModelForm, EmailField

from pdn.workshops.models import Workshop, Inschrijving

class ChangeAliasForm(ModelForm):
	class Meta:
		model = Alias
		fields = ['source', 'target']

class CreateListForm(ModelForm):
	class Meta:
		model = List
		fields = ['name', 'description', 'moderate_members', 'moderate_nonmembers']

class EditListForm(ModelForm):
	add_mod = EmailField(required=False)

	class Meta:
		model = List
		fields = ['description', 'subject_prefix', 'moderate_members', 'moderate_nonmembers']
