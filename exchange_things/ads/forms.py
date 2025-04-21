from django import forms
from .models import Ad, ExchangeProposal


class CreateAd(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image',
                    'category', 'condition']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'image': 'Фото',
            'category': 'Категория',
            'condition': 'Состояние'
        }


class CreatedExchange(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']
        labels = {
            'ad_sender': 'Вы предлагаете',
            'comment': 'Комментарий'
        }


class CategoryForm(forms.Form):
    category = forms.CharField(max_length=50)


class SearchForm(forms.Form):
    search = forms.CharField(max_length=50)

