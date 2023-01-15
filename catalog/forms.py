from django import forms
from .models import Review, Feedback, Bidders
from django.utils.translation import gettext_lazy as _


class ReviewForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label_suffix="", label=_('review'))

    class Meta:
        model = Review
        fields = ('body',)

class BiddersForm(forms.ModelForm):
    amount = forms.DecimalField(label=_('Amount'), widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                label_suffix="")

    class Meta:
        model = Bidders
        fields = ('amount',)


class FeedbackForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}), label=_('Email'), label_suffix="")
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label_suffix="", label=_('Body'))

    class Meta:
        model = Feedback
        fields = ('email', 'body')

