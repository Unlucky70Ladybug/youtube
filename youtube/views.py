from django.shortcuts import render
from .models import Video
from .forms import ItemForm,GenreForm,VideoTimeForm,OrderForm,GetnumFrom,AccountForm
from googleapiclient.discovery import build
import isodate
from googleapiclient.errors import HttpError
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.

def user_login(request):
    params={
        
            "msg":"",
        }
    if request.method == 'POST':
        name = request.POST.get('userid')
        pw = request.POST.get('password')
        
        # Djangoの認証
        user = authenticate(username=name, password=pw)
        
        if user is not None:
            if user.is_active:
                # ログインさせる
                login(request, user)
                # ページ移動
                return HttpResponseRedirect(reverse('index'))
            else:
                # アカウントが無効な場合
                params["msg"] = "アカウントが有効でありません"
                return render(request,"youtube/login.html",context=params)
        else:
            # ユーザー認証が失敗
            params["msg"] = "ユーザー名またはパスワードが違います"
            return render(request,"youtube/login.html",context=params)
    elif request.method == 'GET':
        return render(request, 'youtube/login.html', context=params)
    
@login_required(login_url='/youtube/')
def user_logout(request):
    logout(request)
    #ログイン画面へ
    return HttpResponseRedirect(reverse('Login'))    
    #return render(request,'youtube/login.html')
    
@login_required(login_url='/youtube/')
def videos(request):
    params = {
        
        'title':'youtube_search',
        
        'msg':'',
        
        'form':ItemForm(),
        
        'genre':GenreForm(),
        
        'video_time': VideoTimeForm(),
        
        'order':OrderForm(),
    
        'video_num': GetnumFrom(),
        
        'youtube_video':None,
        
        }
    if request.method == 'POST':
        
        #取得した動画を得る
        youtube_videos = request.session.get('youtube_videos', None)
        
        if youtube_videos != None:
            
            params['youtube_video'] = youtube_videos
        
        #既に登録したか調べる
        video_num = Video.objects.filter(user=request.user, url=request.POST["url"]).count()
        if video_num > 0:
            params["msg"] =  "その動画は既に登録されています"
            return render(request,'youtube/index.html',params)
        
        #ここからお気に入り登録する
        video = Video()
        video.user = request.user
        video.title = request.POST["title"]
        video.channel = request.POST["channel"]
        video.url = request.POST["url"]
        video.publish_time =  request.POST["publish_time"]
        video.video_time = request.POST["video_time"]
        video.save()
        params["msg"] = "登録しました"
        
        return render(request,'youtube/index.html',params)
    return render(request, "youtube/test.html",context=params)

class AccountRegistration(TemplateView):
    def __init__(self):
       self.params = {
           
       "account_form": AccountForm(),
       
       "msg":""
       }
       
       # Get処理
    def get(self,request):
        self.params["account_form"] = AccountForm()
        return render(request,"youtube/register.html",context=self.params)
    
    # Post処理
    def post(self,request):
        if request.POST['name'] == '戻る':
            return render(request,"youtube/login.html")
        
        elif request.POST['name'] == '登録': 
            item = AccountForm(request.POST)
            # フォーム入力の有効検証
            if item.is_valid():
                # アカウント情報をDB保存
                account = item.save()
                # パスワードをハッシュ化
                account.set_password(account.password)
                # ハッシュ化パスワード更新
                account.save()
                self.params["msg"] = "登録しました"
    
            else:
                # フォームが有効でない場合
                self.params["msg"] = "正しく入力させていないか、既にそのユーザー名は登録させています"
                return render(request,"youtube/register.html",context=self.params)
    
            return render(request,"youtube/register.html",context=self.params)
        
@login_required(login_url='/youtube/')
def favorites(request):
    params = {
        
        "UserID":request.user,
        
        "msg":"",
        
        "youtube_video": None
        }
    if (request.method == 'GET'):
        #既に登録してある動画を得る
        favorites_video = get_favorites(request.user)
        #お気に入り動画がない時
        if favorites_video != None:
            params["youtube_video"] = favorites_video
        else:
            params["msg"] = "登録されている動画はありません"
        return render(request,"youtube/favorites.html",context=params)
    
    elif (request.method == 'POST'):
        #名前とURLからお気に入りを削除
        delete_video = Video.objects.filter(user=request.user, url=request.POST["youtube_url"])
        delete_video.delete()
        params["msg"] = "削除しました"
        #既に登録してある動画を得る
        favorites_video = get_favorites(request.user)
        if favorites_video != None:
            params["youtube_video"] = favorites_video
        
        return render(request,"youtube/favorites.html",context=params)
    

@login_required(login_url='/youtube/')
def index(request):
    params={
        'title':'youtube_search',
        
        'msg':'',
            
        'form':ItemForm(),
            
        'genre':GenreForm(),
            
        'video_time': VideoTimeForm(),
            
        'order':OrderForm(),
        
        'video_num': GetnumFrom(),
            
        'youtube_video':None
    }
    if (request.method == 'POST'):
        
        #バリデーションがあっているか調べる
        item = ItemForm(request.POST)
        genre = GenreForm(request.POST)
        videotime = VideoTimeForm(request.POST)
        order = OrderForm(request.POST)
        videonum = GetnumFrom(request.POST)
        
        if item.is_valid() and genre.is_valid() and videotime.is_valid()\
            and order.is_valid() and videonum.is_valid():
                #バリデーションが成功の場合の処理
                #ItemFormを使う
                params['form']=ItemForm(request.POST)
           
                #Choiceフォームを使う
                params['genre']=GenreForm(request.POST)
           
                #VideoTimeFormを使う
                params['video_time']=VideoTimeForm(request.POST)
           
                #OrderFormを使う
                params['order']=OrderForm(request.POST)
           
                #GetnumFormを使う
                params['video_num']= GetnumFrom(request.POST)
           
                #動画を調べる
                youtube_list=youtube_search(
                    request,params,\
                    request.POST['apikey'],int(request.POST['min_count']),
                    int(request.POST['max_count']),request.POST['keyword'],
                    request.POST['min_year'],request.POST['min_month'],
                    request.POST['min_day'],request.POST['genre'],
                    request.POST['video_time'],request.POST['order'],
                    int(request.POST['video_num'])
                    )
                #youtube_listがlist型か調べる
                if isinstance(youtube_list, list) and len(youtube_list) > 0:
                    params['youtube_video']=[]
                    #paramsに動画を渡す
                    for item in youtube_list:
                        params['youtube_video'].append(item)
                    #取った動画を保存する　セッション変数として他のviews.py内ある関数に送る
                    request.session['youtube_videos'] = youtube_list
                
        else:
            #バリデーションが失敗の場合の場合
            params['form']=ItemForm(request.POST)
            params['video_num']= GetnumFrom(request.POST)
            params['genre']=GenreForm(request.POST)
            params['video_time']=VideoTimeForm(request.POST)
            params['order']=OrderForm(request.POST)
        
    return render(request,'youtube/index.html',params)

#これ以降はビュー関数ではなく普通の関数======================================================================

def youtube_search(request, params, apikey, min_count, max_count, keyword, min_year, min_month, min_day, genre, video_time, video_order, video_num):
    URL_video = 'https://www.youtube.com/embed/'
    youtube = build('youtube', 'v3', developerKey=apikey)
    youtube_list = []

    nextPagetoken = None
    title = ""
    url = ""
    channel = ""
    publishTime = ""

    while len(youtube_list) < video_num and (nextPagetoken is not None or not youtube_list):
        try:
            search_response = youtube.search().list(
                part='id,snippet',
                q=keyword,  # 検索したい文字列を指定
                order=video_order,
                type="video",  # 検索対象のタイプを指定
                maxResults=min(video_num - len(youtube_list), 50), #最大50件まで取得
                videoDuration=video_time,  # 動画時間
                publishedAfter="{0}-{1}-{2}T00:00:00Z".format(min_year, min_month, min_day),
                regionCode='JP',
                videoCategoryId=genre,
                pageToken=nextPagetoken
            ).execute()
            
            for search_result in search_response['items']:
                view_result = youtube.videos().list(part="statistics, contentDetails", id=search_result["id"]["videoId"]).execute()
                result_view_count = int(view_result['items'][0]['statistics'].get('viewCount'))
                view_time_result = view_result['items'][0]['contentDetails']['duration']
                result_view_time = int(isodate.parse_duration(view_time_result).total_seconds())#PT3M45Sを225秒に
                if min_count <= result_view_count <= max_count and result_view_time > 60:
                    channel = search_result['snippet']['channelTitle']  # 動画投稿者
                    title = search_result['snippet']['title']  # タイトル
                    url = URL_video + search_result['id']['videoId']  # 動画のURL
                    view_count = result_view_count  # 再生回数
                    publishTime = search_result['snippet']['publishTime']  # 投稿日
                    time_hms = get_time(result_view_time)#時間を得る
                    
                    if len(youtube_list) < video_num:
                        youtube_list.append([title, channel, view_count, url, publishTime, time_hms])
            try:
                nextPagetoken = search_response.get("nextPageToken")
                if not nextPagetoken:
                    if len(youtube_list) == 0:
                        params['msg'] = "目的の動画はありませんでした"
                    else:
                        params['msg'] = "目標の動画数はありませんでした"
                    return youtube_list
            except KeyError:
                params['msg'] = "次のページトークンがありません。"
                return youtube_list
            
        except HttpError as e:
            # APIキーのエラー処理
            if "API key not valid" in str(e):
                params['msg'] = "APIkeyが正しくありません 動画を取得できませんでした"
                
            # クォータ制限の処理
            elif e.resp.status == 403 and "quotaExceeded" in str(e):
                params['msg'] = "APIkeyの制限に達しました 動画を取得できませんでした"
            return render(request, 'youtube/index.html', params)

    return youtube_list

def get_time(seconds):
    hours, remainder = divmod(seconds, 3600) # 3600秒 = 1時間
    minutes, seconds = divmod(remainder, 60) # 60秒 = 1分
    if hours < 1:
        return f"{minutes}分{seconds}秒"
    return f"{hours}時間{minutes}分{seconds}秒"

def get_favorites(request_user):
    #userがrequest_userのものを全て得る
    if Video.objects.filter(user = request_user).count() > 0:
        video_data = Video.objects.filter(user = request_user)
        video_list = []
        for item in video_data:
            #video_listに持ってきたモデルを追加する
            video_list.append(item.get_data())
        return video_list
    else:
        return None