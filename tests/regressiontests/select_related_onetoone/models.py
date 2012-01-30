from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()

    def __unicode__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)

    def __unicode__(self):
        return "%s, %s" % (self.city, self.state)


class UserStatResult(models.Model):
    results = models.CharField(max_length=50)

    def __unicode__(self):
        return 'UserStatResults, results = %s' % (self.results,)


class UserStat(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    posts = models.IntegerField()
    results = models.ForeignKey(UserStatResult)

    def __unicode__(self):
        return 'UserStat, posts = %s' % (self.posts,)


class StatDetails(models.Model):
    base_stats = models.OneToOneField(UserStat)
    comments = models.IntegerField()

    def __unicode__(self):
        return 'StatDetails, comments = %s' % (self.comments,)


class AdvancedUserStat(UserStat):
    karma = models.IntegerField()


class Image(models.Model):
    name = models.CharField(max_length=100)


class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.OneToOneField(Image, null=True)


class Parent1(models.Model):
    name1 = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name1


class Parent2(models.Model):
    name2 = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name2


class Child1(Parent1, Parent2):
    other = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name1


class Child2(Parent1):
    parent2 = models.OneToOneField(Parent2)
    other = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name1
