from aiogram.fsm.state import State, StatesGroup


class AnimeAddFSM(StatesGroup):
    waiting_code = State()
    waiting_title = State()
    waiting_description = State()
    waiting_genres = State()
    waiting_year = State()
    waiting_status = State()
    waiting_vip = State()
    waiting_poster = State()
    confirm = State()


class EpisodeAddFSM(StatesGroup):
    waiting_anime_code = State()
    waiting_episode_num = State()
    waiting_video = State()
    waiting_quality = State()


class SearchFSM(StatesGroup):
    waiting_query = State()


class VipActivateFSM(StatesGroup):
    waiting_code = State()


class RequestAnimeFSM(StatesGroup):
    waiting_name = State()
    waiting_comment = State()


class CreateVipCodeFSM(StatesGroup):
    waiting_duration_days = State()


class BroadcastFSM(StatesGroup):
    waiting_message = State()


class AnimePostFSM(StatesGroup):
    waiting_code = State()


class AnimeDeleteFSM(StatesGroup):
    waiting_code = State()
