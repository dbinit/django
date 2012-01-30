from django import db
from django.conf import settings
from django.test import TestCase

from models import (User, UserProfile, UserStat, UserStatResult, StatDetails,
    AdvancedUserStat, Image, Product, Parent1, Parent2, Child1, Child2)

class ReverseSelectRelatedTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username="test")
        userprofile = UserProfile.objects.create(user=user, state="KS",
                                                 city="Lawrence")
        results = UserStatResult.objects.create(results='first results')
        userstat = UserStat.objects.create(user=user, posts=150,
                                           results=results)
        details = StatDetails.objects.create(base_stats=userstat, comments=259)

        user2 = User.objects.create(username="bob")
        results2 = UserStatResult.objects.create(results='moar results')
        advstat = AdvancedUserStat.objects.create(user=user2, posts=200, karma=5,
                                                  results=results2)
        StatDetails.objects.create(base_stats=advstat, comments=250)
        p1 = Parent1(name1="Only Parent1")
        p1.save()
        c1 = Child1(name1="Child1 Parent1", name2="Child1 Parent2")
        c1.save()
        p2 = Parent2(name2="Child2 Parent2")
        p2.save()
        c2 = Child2(name1="Child2 Parent1", parent2=p2)
        c2.save()

    def test_basic(self):
        def test():
            u = User.objects.select_related("userprofile").get(username="test")
            self.assertEqual(u.userprofile.state, "KS")
        self.assertNumQueries(1, test)

    def test_follow_next_level(self):
        def test():
            u = User.objects.select_related("userstat__results").get(username="test")
            self.assertEqual(u.userstat.posts, 150)
            self.assertEqual(u.userstat.results.results, 'first results')
        self.assertNumQueries(1, test)

    def test_follow_two(self):
        def test():
            u = User.objects.select_related("userprofile", "userstat").get(username="test")
            self.assertEqual(u.userprofile.state, "KS")
            self.assertEqual(u.userstat.posts, 150)
        self.assertNumQueries(1, test)

    def test_follow_two_next_level(self):
        def test():
            u = User.objects.select_related("userstat__results", "userstat__statdetails").get(username="test")
            self.assertEqual(u.userstat.results.results, 'first results')
            self.assertEqual(u.userstat.statdetails.comments, 259)
        self.assertNumQueries(1, test)

    def test_forward_and_back(self):
        def test():
            stat = UserStat.objects.select_related("user__userprofile").get(user__username="test")
            self.assertEqual(stat.user.userprofile.state, 'KS')
            self.assertEqual(stat.user.userstat.posts, 150)
        self.assertNumQueries(1, test)

    def test_back_and_forward(self):
        def test():
            u = User.objects.select_related("userstat").get(username="test")
            self.assertEqual(u.userstat.user.username, 'test')
        self.assertNumQueries(1, test)

    def test_not_followed_by_default(self):
        def test():
            u = User.objects.select_related().get(username="test")
            self.assertEqual(u.userstat.posts, 150)
        self.assertNumQueries(2, test)

    def test_follow_from_child_class(self):
        def test():
            stat = AdvancedUserStat.objects.select_related('user', 'statdetails').get(posts=200)
            self.assertEqual(stat.statdetails.comments, 250)
            self.assertEqual(stat.user.username, 'bob')
        self.assertNumQueries(1, test)

    def test_follow_inheritance(self):
        def test():
            stat = UserStat.objects.select_related('user', 'advanceduserstat').get(posts=200)
            self.assertEqual(stat.advanceduserstat.posts, 200)
            self.assertEqual(stat.user.username, 'bob')
            self.assertEqual(stat.advanceduserstat.user.username, 'bob')
        self.assertNumQueries(1, test)

    def test_nullable_relation(self):
        im = Image.objects.create(name="imag1")
        p1 = Product.objects.create(name="Django Plushie", image=im)
        p2 = Product.objects.create(name="Talking Django Plushie")

        self.assertEqual(len(Product.objects.select_related("image")), 2)

    def test_parent_only(self):
        Parent1.objects.select_related('child1').get(name1="Only Parent1")

    def test_multiple_subclass(self):
        with self.assertNumQueries(1):
            p = Parent1.objects.select_related('child1').get(name1="Child1 Parent1")
            self.assertEqual(p.child1.name2, u"Child1 Parent2")

    def test_onetoone_with_subclass(self):
        with self.assertNumQueries(1):
            p = Parent2.objects.select_related('child2').get(name2="Child2 Parent2")
            self.assertEqual(p.child2.name1, u"Child2 Parent1")
