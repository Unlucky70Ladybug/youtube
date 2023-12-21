from django.db import models

from django.contrib.auth.models import User
# Create your models here.

class Video(models.Model):
    #Userモデルを参照する
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(max_length=1000)
    channel = models.TextField(max_length=2000)
    url = models.TextField(max_length=1000)
    publish_time = models.TextField(max_length=1000)
    video_time = models.TextField(max_length=1000)
    pub_date = models.DateTimeField(auto_now_add=True)
    
    
    def get_data(self):
        return [self.title, self.channel, self.url, self.publish_time, self.video_time]
    
    class Meta:
        ordering = ('-pub_date',)#あたらしい順