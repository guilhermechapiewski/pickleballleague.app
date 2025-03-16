class ShortLink:
    def __init__(self, link, destination_link):
        self.link = link
        self.destination_link = destination_link

    def __str__(self):
        return f"{self.link} -> {self.destination_link}"
    
    def to_object(self):
        return {
            "link": self.link,
            "destination_link": self.destination_link
        }
    
    @staticmethod
    def from_object(object):
        return ShortLink(object["link"], object["destination_link"])