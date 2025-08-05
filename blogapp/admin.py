from django.contrib import admin
from blogapp.models import Post, Tag, Comment, Subscriber, Profile, WebsiteMetadata

# Register your models here.
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Subscriber)
admin.site.register(Profile)
admin.site.register(WebsiteMetadata)
