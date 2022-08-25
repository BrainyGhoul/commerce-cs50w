from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from .models import User, Listing, Bid, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings": [i for i in Listing.objects.all() if i.active == True]
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    if request.method == 'POST' and request.user.is_authenticated:

        Listing(seller=request.user, title=request.POST["title"], description=request.POST["description"], starting_bid=int(request.POST["starting_bid"]), picture_url=request.POST["picture_url"], category=request.POST["category"]).save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create_listing.html")

def view_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    redirect_to = HttpResponseRedirect(reverse("view_listing", kwargs={"listing_id": listing_id}))
    bids = []
    for i in listing.listing.all():
        bids.append(i.bid_price)
    if len(bids) == 0:
        bids = None
    else:
        bids = max(bids)

    current_bidder = None
    for i in listing.listing.all():
        if i.bid_price == bids:
            current_bidder = i
    
    if bids == None:
        bids = 0
        
    if request.method == "POST" and request.user.is_authenticated:
        try: 
            temp = request.POST["comment_text"]
            Comment(listing=listing, comment_from=request.user, comment=temp, rating=request.POST["rating"]).save()
            return redirect_to
        
        except Exception: 
            try:
                price = float(request.POST["bid_price"])
                if price >= float(listing.starting_bid) and price > float(bids):
                    Bid(Listing=listing, bid_price=price, bidder=request.user).save()
                    return redirect_to
                else:
                    return render(request, "auctions/view_listing.html", {
                        "content": listing,
                        "current_bid": current_bidder,
                        "reject": True,
                        "watchlist": request.user.watch_listing.all(),
                        "not_added": True
                    })
        
            except Exception:
                temp = request.POST["watchlist"]
                if temp == "add":
                    request.user.watch_listing.add(listing)
                elif temp == "remove":
                    request.user.watch_listing.remove(listing)
                return redirect_to

            return render(request, "auctions/view_listing.html", {
                "content": listing,
                "current_bid": current_bidder,
                "reject": True,
                "watchlist": request.user.watch_listing.all()
            })
        
    if request.user.is_authenticated:
        watchlist = request.user.watch_listing.all()
    else:
        watchlist = None
    if not listing.picture_url:
        listing.picture_url = "https://thumbs.dreamstime.com/b/no-image-available-icon-vector-illustration-flat-design-140476186.jpg"
    return render(request, "auctions/view_listing.html", {
        "content": listing,
        "current_bid": current_bidder,
        "comments": listing.listing_name.all(),
        "watchlist": watchlist
    })

def close_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.user.is_authenticated:
        if request.user == listing.seller:
            Listing.objects.filter(pk=listing_id).update(active=False)
            return render(request, "auctions/close_listing.html", {
                "condition": True,
                "listing": listing
            })

        else:
            return render(request, "auctions/close_listing.html", {
                "condition": False,
                "listing": listing
            })
    return render(request, "auctions/close_listing.html", {
        "listing": listing
    })

@login_required
def watchlist(request):

    if request.user.is_authenticated:

        return render(request, "auctions/index.html", {
            "listings": request.user.watch_listing.all(),
            "is_watchlist": True
        })
    
    else:
        return HttpResponseRedirect(reverse("login"))

def categories(request):
    lst = {listing.category for listing in Listing.objects.all()}
    return render(request, "auctions/categories.html", {
        "categories": lst
    })

def view_category(request, name):
    
    listings = [i for i in Listing.objects.all() if i.category == name]

    return render(request, "auctions/index.html", {
        "listings": listings
    })
