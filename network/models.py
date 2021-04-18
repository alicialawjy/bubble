from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    relationship = models.ManyToManyField('self', through='Follow', symmetrical=False, related_name='related_to')

class Follow(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', blank=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower', blank=True)
    unique_together = ['from_user','to_user']

def rename(instance,filename):
    filename = f'{instance.id}'
    return filename

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wrote')
    content = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, blank=True, related_name='liked')
    replies = models.ManyToManyField('self', related_name='related_to', symmetrical=False)

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "first_name": self.author.first_name,
            "last_name": self.author.last_name,
            "content": self.content,
            "likes": self.likes,
            "time": self.time.strftime("%b %d %Y, %I:%M %p")
        }



