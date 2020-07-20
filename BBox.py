#class BBox to check boundries

class BBox(object):

    def __init__(self, left, bottom, right=None, top=None):
        self.left = left
        self.bottom = bottom
        self.right = right if right else left
        self.top = top if top else bottom

    def isIn(self, bb):
        return self.left >= bb.left and self.bottom >= bb.bottom and self.right <= bb.right and self.top <= bb.top

