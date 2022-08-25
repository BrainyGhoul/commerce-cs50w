from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser): 
    pass

class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    starting_bid = models.IntegerField()
    picture_url = models.URLField(default=None)
    category = models.CharField(max_length=64, default=None)
    active = models.BooleanField(default=True)
    listings = models.ManyToManyField(User, blank=True, related_name="watch_listing")


class Bid(models.Model):
    bid_price = models.IntegerField()
    Listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_name")
    comment_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    comment = models.CharField(max_length=500)
    rating = models.DecimalField(decimal_places=1, max_digits=2)