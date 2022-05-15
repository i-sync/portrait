from app.library.config import configs

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

class Page(object):

    def __init__(self, item_count, page_index=1, page_size=configs.page_size, page_show=configs.page_show):
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)
        if self.page_count > page_show:
            self.page_show = page_show - 6 # remomve first and last page.
        else:
            self.page_show = page_show
        if (item_count == 0) or (page_index > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_prev = self.page_index > 1
        self.pagelist()
        if item_count == 0:
            self.prefix=[]
            self.suffix=[]
            self.page_list=[]


    def __str__(self):
        return 'item_count: {}, page_count: {}, page_index: {}, page_size: {}, page_show: {}, offset: {}, limit: {}'.format(self.item_count, self.page_count, self.page_index, self.page_size, self.page_show, self.offset, self.limit)

    __repr__ = __str__

    def pagelist(self):
        left = 2
        right = self.page_count
        self.prefix = [1]
        if self.page_count > 1:
            self.suffix = [self.page_count]
        else:
            self.suffix = []

        if self.page_count > self.page_show:
            self.prefix = list(range(1, 4))
            self.suffix = list(range(self.page_count - 2, self.page_count + 1))
            left = self.page_index - self.page_show // 2
            if left < 4:
                left = 4
            right = left + self.page_show
            if right > self.page_count - 2:
                right = self.page_count - 2
                left = right - self.page_show

        self.page_list = list(range(left, right))


class PageAll(object):
    """list all page number"""

    def __init__(self, item_count, page_index=1, page_size=configs.page_size):
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)

        if (item_count == 0) or (page_index > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_prev = self.page_index > 1
        if item_count == 0:
            self.page_list=[]
        else:
            self.page_list=range(1, self.page_count + 1)


    def __str__(self):
        return 'item_count: {}, page_count: {}, page_index: {}, page_size: {},  offset: {}, limit: {}'.format(self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__
