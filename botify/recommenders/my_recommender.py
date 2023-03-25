from collections import defaultdict

from .recommender import Recommender
from .user_based import Collaborative
from .top_pop import TopPop
import random


class MyRecommender(Recommender):
    def __init__(self, tracks_redis, recommendations_svd_redis, catalog):
        self.tracks_redis = tracks_redis
        self.catalog = catalog
        self.recommended_tracks = defaultdict(set)
        self.fallback = TopPop(tracks_redis, catalog.top_tracks[:100])

    def recommend_from_fallback(self, user: int, prev_track: int, prev_track_time: float) -> int:
        track = self.fallback.recommend_next(user, prev_track, prev_track_time)
        while track in self.recommended_tracks[user]:
            track = self.fallback.recommend_next(user, prev_track, prev_track_time)
        self.recommended_tracks[user].add(track)
        return track

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.recommend_from_fallback(user, prev_track, prev_track_time)

        previous_track = self.catalog.from_bytes(previous_track)
        recommendations = previous_track.recommendations
        if not recommendations or prev_track_time < 0.5:
            return self.recommend_from_fallback(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        for track in shuffled:
            if track not in self.recommended_tracks[user]:
                self.recommended_tracks[user].add(track)
                return track

        return self.recommend_from_fallback(user, prev_track, prev_track_time)
