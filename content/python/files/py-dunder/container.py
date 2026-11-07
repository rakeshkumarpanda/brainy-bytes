# 1.1 Special methods and operator overloading
# Example "container" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

class Playlist:
    def __init__(self, songs):
        self.songs = list(songs)

    def __len__(self):                         # len(p)
        return len(self.songs)

    def __getitem__(self, index):              # p[0], p[-1], p[1:3]
        if isinstance(index, slice):
            return Playlist(self.songs[index])
        return self.songs[index]

    def __setitem__(self, index, song):        # p[0] = "new"
        self.songs[index] = song

    def __contains__(self, song):              # "x" in p
        return song.lower() in (s.lower() for s in self.songs)

    def __iter__(self):                        # for s in p
        return iter(self.songs)

    def __repr__(self):
        return f"Playlist({self.songs})"


p = Playlist(["Tum Hi Ho", "Kesariya", "Naatu Naatu", "Jai Ho"])
print(len(p), p[0], p[-1])
print(p[1:3])
p[0] = "Chaiyya Chaiyya"
print("kesariya" in p, "Believer" in p)
for song in p:
    print("-", song)
print(list(reversed(p)))                       # reversed works with __len__ and __getitem__
