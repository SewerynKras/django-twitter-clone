from django import forms
from tweets import models


class NewTweetForm(forms.ModelForm):
    class Meta:
        model = models.Tweet
        fields = ['text']


class NewCommentForm():
    class Meta:
        model = models.Comment
        fields = ['text']


class RetweetForm():
    class Meta:
        model = models.Retweet
        fields = ['text']


class PoolForm():
    class Meta:
        model = models.Poll
        fields = ['choice1_text', 'choice2_text',
                  'choice3_text', 'choice4_text']
