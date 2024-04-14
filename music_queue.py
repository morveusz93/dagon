from yt import YoutubeAudio


class MusicQueue:
    def __init__(self):
        self._queue: list[YoutubeAudio] = []
        self._history: list[YoutubeAudio] = []

    def add(self, el: YoutubeAudio):
        self._queue.append(el)

    def get(self):
        if not self.is_empty():
            return self._queue[0]

    def get_all(self):
        return self._queue

    def clear(self):
        self._queue = []

    def skip_queue(self, el: YoutubeAudio):
        self._queue.insert(0, el)

    def is_empty(self):
        return len(self._queue) == 0

    def remove_first(self):
        song = self._queue.pop(0)
        self._history.insert(0, song)
        return song

    def get_history(self):
        return self._history

    def get_last_song(self):
        if self._history:
            return self._history[0]
