class Notice:
    def __init__(self, num, link, title, category, created_at, content, updated_at=None, status=0):
        self.num = num
        self.link = link
        self.title = title
        self.category = category
        self.created_at = created_at
        self.updated_at = updated_at
        self.content = content
        self.updated_at = updated_at
        self.status = status

    def getList(self):
        return [self.num, self.link, self.title, self.category, self.created_at, self.content, self.updated_at, self.status]