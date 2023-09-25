from django.db import models

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class Intent(models.Model):
    name = models.CharField(max_length=1000)
    group_id = models.IntegerField()

    def __str__(self):
        return self.name

class Pattern(models.Model):
    name = models.CharField(max_length=1000)
    intent_id = models.IntegerField()

    def __str__(self):
        return self.name

class Response(models.Model):
    name = models.CharField(max_length=1000)
    intent_id = models.IntegerField()

    def __str__(self):
        return self.name

class Chats(models.Model):
    chat = models.CharField(max_length=1000000)

    def __str__(self):
        return self.chat