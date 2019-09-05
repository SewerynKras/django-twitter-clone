from django import forms
from tweets import models


class TweetForm(forms.ModelForm):
    text = forms.CharField(required=True, label="",
                           widget=forms.HiddenInput(attrs={
                               'id': 'new-tweet-text-form'}))

    class Meta:
        model = models.Tweet
        fields = ['text']


class ImagesForm(forms.ModelForm):
    image_1 = forms.ImageField(required=False, label="",
                               widget=forms.HiddenInput(attrs={
                                    'id': 'new-tweet-image1-form'}))
    image_2 = forms.ImageField(required=False, label="",
                               widget=forms.HiddenInput(attrs={
                                    'id': 'new-tweet-image2-form'}))
    image_3 = forms.ImageField(required=False, label="",
                               widget=forms.HiddenInput(attrs={
                                    'id': 'new-tweet-image3-form'}))
    image_4 = forms.ImageField(required=False, label="",
                               widget=forms.HiddenInput(attrs={
                                    'id': 'new-tweet-image4-form'}))

    class Meta:
        model = models.Images
        fields = ['image_1', 'image_2', 'image_3', 'image_4']

# class NewCommentForm():
#     class Meta:
#         model = models.Comment
#         fields = ['text']


# class RetweetForm():
#     class Meta:
#         model = models.Retweet
#         fields = ['text']


# class PoolForm():
#     class Meta:
#         model = models.Poll
#         fields = ['choice1_text', 'choice2_text',
#                   'choice3_text', 'choice4_text']
