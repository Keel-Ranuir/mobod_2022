import random
from .random import Random
from .recommender import Recommender
from .top_pop import TopPop


class Collaborative(Recommender):
    def __init__(self, recommendations_redis, tracks_redis, catalog, recommended_tracks):
        self.recommendations_redis = recommendations_redis
        self.fallback = TopPop(tracks_redis, catalog.top_tracks[:100])
        self.catalog = catalog
        self.recommended_tracks = recommended_tracks

    def recommend_from_fallback(self, user: int, prev_track: int, prev_track_time: float) -> int:
        track = self.fallback.recommend_next(user, prev_track, prev_track_time)
        while track in self.recommended_tracks[user]:
            track = self.fallback.recommend_next(user, prev_track, prev_track_time)
        return track

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        if recommendations is not None:
            recommendations = list(self.catalog.from_bytes(recommendations))
            for recommendation in recommendations:
                if recommendation not in self.recommended_tracks[user]:
                    return recommendation

        return self.recommend_from_fallback(user, prev_track, prev_track_time)
