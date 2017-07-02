from LinkGrabberDjango import apigrabber


class VideoObject(object):
    def __init__(self, posts, desc, rating, startyear, title,poster,state,genre):
        self.posts = posts
        self.desc = desc
        self.rating = rating
        self.startyear = startyear
        self.title = title
        self.poster = poster
        self.state = state
        self.genre = genre


"""tasks2 = apigrabber.createdetails("11877")

tasks = {
    1: VideoObject(
        posts = reversed(tasks2["posts"]),
        desc= tasks2["desc"],
        rating= tasks2['rating'],
        startyear= tasks2['startyear'],
        title= tasks2['title'],
        poster= tasks2['poster'],
        state= tasks2['state'],
        genre= tasks2['genre']
                   )
}"""
