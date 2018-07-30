from allauth.account.forms import LoginForm
# from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, PrependedAppendedText, FormActions)

class MyLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)
        # You don't want the `remember` field?
        # if 'remember' in self.fields.keys():
        #     del self.fields['remember']

        helper = FormHelper()
        helper.form_show_labels = False
        helper.layout = Layout(
            
        #     PrependedText('username', '<span class="input-group-addon"><i class="glyphicon glyphicon-user"></i></span>'),
        #     PrependedText('password', '<span class="input-group-addon"><i class="glyphicon glyphicon-lock"></i></span>'),
        #     FormActions(Submit('login', 'login', css_class='btn-primary'))
        )
        self.helper = helper