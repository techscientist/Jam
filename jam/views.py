from django import template
from time import gmtime, strftime

from django.shortcuts import get_object_or_404, render
from django.http import  Http404, HttpResponse

from jam.models import Artists, Album
from jam.jam_admin import * 
from jam.jam_api import *
from jam.spotify_api import *
from jam.pitchfork_api import *

import json
import urllib

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

#####################
#  3RD PARTY API KEYS
#####################

spotify_api_key = '509df3f3d7584069a23c2db440960b20'
spotify_api_secret = 'e3826548f35d4ecb88c4eb8032ada051'
OAuth_token = 'BQDbMT3TcgCddi2y7_NehZU54TGQBk0MXbgO9izP5WrCeO40WqLdL98j88zeQwrMIBGj9'

echonest_api_key = 'JXWIZXVWFCDBT9DVG'
echonest_consumer_key = 'd3755c57dc73a9132325cd5bac8d4556'
echonest_shared_secret = '1b5YciWYSia7H0EMMM8rLw'

#####################
#               CACHE
#####################

features_cache = set()

########################
#  FEATURE WRAPPER CLASS
########################

class Feature:

    def __init__(self, name, title, review):
        self.artistName = name
        self.albumTitle = title
        self.featureReview = review

    def __unicode__(self):
        return self.artistName + " " + self.albumTitle + " " + self.featureReview

#######################
#    JAM VIEW FUNCTIONS
#######################

def lets_jam(request):
    # Home Page of JAM
    # Page to display Featured Favorite Albums
    featured_albums_list = list(Album.objects.filter(Favorite=1))

    if featured_albums_list != []:
        no_features = 0
        features = []
        for album in featured_albums_list:
            artist = Artists.objects.get(SpotifyID=album.ArtistID_id)
            feature = Feature(artist.ArtistName, album.AlbumTitle, "TESTING TESTING TESTING TESTINGTESTING TESTING TESTING TESTINGTESTING TESTING TESTING TESTINGTESTING TESTING TESTING TESTINGTESTING TESTING TESTING TESTING")
            features.append(feature)
    else:
        no_features = 1

    return render(request, 'features_home.html', {'no_features': no_features, 'featured_albums': features, 'article_header': "featured albums"})

def lets_jam_recommend(request):
    # Recommendation Page
    if (request.method == 'GET'):
        return render(request, 'lets_jam_recommend.html', {'message': '', 'source': ""})
    else:
        try:

            recommened_item = request.POST['recommened_item']
            json_Search_response_artist, json_Search_response_album = spotify_gen_search(recommened_item)

            if (json_Search_response_album['albums']['items'] != [ ]):
                # Match
                message = "You've Successfully Recommmended: " + recommened_item.title() + "."
                # send_mail('New Jam Recommendation', 'Username: ' + "" + " recommendeds " + recommened_item.title(), 'evralcar@gmail.com', ['evralcar@gmail.com'], fail_silently=False)
                if (Album.objects.filter(AlbumTitle=recommened_item)):
                    # Matching Album
                    source = json_Search_response_album['albums']['items'][0]['images'][1]['url']
                    return render(request, "lets_jam_recommend.html", {'message': message, 'source': source})
                elif(json_Search_response_artist['artists']['items'] != [ ]):
                    # change sourse to get artist picture, not an album picture
                    source = json_Search_response_artist['artists']['items'][0]['images'][1]['url']
                    return render(request, "lets_jam_recommend.html", {'message': "We Have a Match!", 'source': source})
                else:
                    message = "Hey, what do you know, someone has already suggested " + recommened_item.title() + ". \n Probably because you've got good taste in Music!"
                    return render(request, "lets_jam_recommend.html", {'message': message, 'source': source})
            else:
                raise ValueError
        except ValueError:
            # we couldn't find your recommendation, display error message
            return render(request, 'lets_jam_recommend.html', {'message': 'We couldn\'t find that Album', 'source': ""})

def lets_jam_review(request, album_title):
    album_title = url_argument_parse(album_title)
    albumSet = Album.objects.filter(AlbumTitle__icontains=album_title)
    print(albumSet)
    if not albumSet:
        # if empty: No Corresponding Album
        raise Http404  
    else: 
        album_title = albumSet[0].AlbumTitle
        artist_name = Artists.objects.get(SpotifyID=albumSet[0].ArtistID.SpotifyID).ArtistName
        review = "This is where the Full Review is" # Index and grab review.
        return render(request, 'album_review.html', {'albumTitle': album_title, 'artistName': artist_name, 'featureReview': review, 'article_header': "album review"})

######################
# DEPRICATED FUNCTIONS
######################

