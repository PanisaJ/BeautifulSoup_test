from django.db import models

class Tag(models.Model):
    tag_text = models.CharField(max_length=100)
    def __str__(self):
        return self.tag_text

class Webpage(models.Model):
    web_text = models.CharField(max_length=100, default="")
    webpage_url = models.URLField(max_length=100)
    def __str__(self):
        return self.web_text

class Title(models.Model):
    title_text = models.CharField(max_length=100)
    title_url = models.URLField(max_length=100)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    Webpage = models.ForeignKey(Webpage, on_delete=models.CASCADE)
    def __str__(self):
        return self.title


    
