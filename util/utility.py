from configparser import ConfigParser, ExtendedInterpolation


CONFIG = ConfigParser(interpolation=ExtendedInterpolation())
try:
    CONFIG.read('../conf/application.ini')
except:
    print('Application configuration file read failed.')
    exit(1)


class History:
    def __init__(self, obj):
        self.obj = obj

    def has_id(self, sid):
        return self.obj.get(sid) is None

    def add_chapter(self, sid, chapter):
        if not self.has_id(sid):
            self.obj[sid] = []
        self.obj[sid].append(chapter)

    def chapter_count(self, sid):
        if not self.has_id(sid):
            return 0
        else:
            return len(self.obj[sid])
