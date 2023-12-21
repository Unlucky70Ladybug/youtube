from django import forms
import datetime
from django.contrib.auth.models import User
import regex

class AccountForm(forms.ModelForm):
    # パスワード入力：非表示対応
    password = forms.CharField(widget=forms.PasswordInput(),label="パスワード")

    class Meta():
        # ユーザー認証
        model = User
        # フィールド指定
        fields = ('username','password')
        # フィールド名指定
        labels = {'username':"ユーザー名",'password':"パスワード"}
    
    def clean_username(self):
        clean_username = self.cleaned_data.get('username')
        if regex.match(r'^(?=[A-Za-z0-9@.+_-]{1,150}$)(?![\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Han}]+$).*',clean_username) is None:
            raise forms.ValidationError('150文字以内、アルファベット、数字、@/./+/-/_のみ')
        return clean_username
    
class ItemForm(forms.Form):
    apikey = forms.CharField(widget=forms.PasswordInput(),label='APIkeyを入れてください')
    min_count = forms.IntegerField(label='最低限の再生回数', min_value=0)
    max_count = forms.IntegerField(label='最大の再生回数', min_value=0)
    keyword = forms.CharField(label='キーワード', empty_value=False, required=False)
    min_year = forms.IntegerField(label='何年から探しますか？', min_value=2005, max_value=int(datetime.date.today().year))
    min_month = forms.IntegerField(label='何月から探しますか？',min_value=1, max_value=12)
    min_day = forms.IntegerField(label='何日から探しますか？', min_value=1)
    
    def clean_min_count(self):
        my_min_count = self.cleaned_data.get('min_count')
        if my_min_count is not None:
            #小数点を含んでいる場合
            if my_min_count != int(my_min_count):
                raise forms.ValidationError('整数を入力してください')
        return my_min_count
    
    def clean_max_count(self):
        my_min_count = self.cleaned_data.get('min_count')
        my_max_count = self.cleaned_data.get('max_count')
        if my_max_count is not None:
            #小数点を含んでいる場合
            if my_max_count != int(my_max_count):
                raise forms.ValidationError('整数を入力してください')
                
            elif my_max_count < my_min_count:
                raise forms.ValidationError(str(my_min_count) + 'よりも多い数を入れてください')
        return my_max_count
    
    def clean_min_month(self):
        my_year = self.cleaned_data.get('min_year')#正しい年を取得
        my_month = self.cleaned_data.get('min_month')
        if my_month is not None:
            if int(my_year) == int(datetime.date.today().year):
                if int(my_month) > int(datetime.date.today().month):
                    raise forms.ValidationError(str(datetime.date.today().month)+\
                                                '月以内の月を入れてください')
        return my_month
    
    def clean_min_day(self):
        my_year = self.cleaned_data.get('min_year')#正しい年を取得
        my_month = self.cleaned_data.get('min_month')#正しい月を習得
        my_day = self.cleaned_data.get('min_day')
        
        if my_day is not None:
            if leap_year(my_year) == True and my_month == 2 and my_day > 29:
                raise forms.ValidationError('29日以内の日にちを入れてください')
                
            elif leap_year(my_year) == False and my_month ==2 and my_day > 28:
                raise forms.ValidationError('28日以内の日にちを入れてください')
            
            elif my_year == datetime.date.today().year and\
                    my_month == datetime.date.today().month and\
                    my_day > datetime.date.today().day:
                        raise forms.ValidationError(str(datetime.date.today().day)+\
                                                    '日以内の日にちを入れてください')
            
            elif my_month in [1, 3, 5, 7, 8, 10, 12] and my_day > 31:
                raise forms.ValidationError('31日以内の日にちを入れてください')
                
            elif my_month in [4, 6, 9, 11] and my_day > 30:
                raise forms.ValidationError('30日以内の日にちを入れてください')
                
        return my_day
        
class GenreForm(forms.Form):
    genre = [
        ('10', '音楽'),
        ('1', '映画とアニメ'),
        ('2', '自動車と乗り物'),
        ('15', 'ペットと動物'),
        ('17', 'スポーツ'),
        ('19', '旅行とイベント'),
        ('20', 'ゲーム'),
        ('22', 'ブログ'),
        ('23', 'コメディー'),
        ('24','エンターテインメント'),
        ('25','ニュースと政治'),
        ('26','ハウツーとスタイル'),
        ('27','教育'),
        ('28','科学と技術')
    ]
    genre = forms.ChoiceField(label='ジャンル',\
                choices=genre)

class VideoTimeForm(forms.Form):
    video_time = [
        ('short', '４分未満'),
        ('medium', '4~20分未満'),
        ('long', '20以上')
    ]
    video_time = forms.ChoiceField(label='動画時間',\
                choices=video_time, widget=forms.Select(attrs={'size':1}))

class OrderForm(forms.Form):
    order = [
        ('viewCount', 'リソースを再生回数の多い順'),
        ('date', 'リソースを作成日の新しい順'),
        ('rating', 'リソースを評価の高い順'),
        ('relevance', 'リソースを検索クエリの関連性が高い順'),
        ('title', 'リソースをタイトルのアルファベット順'),
        ('videoCount', 'アップロード動画の番号順(降順)')
    ]
    order = forms.ChoiceField(label='オーダー',\
                choices=order)
class GetnumFrom(forms.Form):
    video_num = forms.IntegerField(label='手に入れたい動画数', min_value=1)

#うる年か調べる
def leap_year(year):
    # 4で割り切れる年はうる年です。
    # ただし、100で割り切れる年はうる年ではありません。
    # ただし、400で割り切れる年はうる年です。
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False

