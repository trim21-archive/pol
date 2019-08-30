from app.db_models import BilibiliBangumi, BilibiliEpisode

from .bilibili import Bilibili


def test_init():
    Bilibili()


def test_submit_ep():
    Bilibili.ep(
        ep_id=893707,
        url='https://www.bilibili.com/bangumi/play/ep276614',
    )
    BilibiliBangumi.get(
        subject_id=271724,
        media_id=28221412,
        season_id=28013,
    )

    BilibiliEpisode.get(
        source_ep_id=276614,
        ep_id=893707,
        subject_id=271724,
    )


def test_submit_bangumi():
    Bilibili.subject(
        subject_id=262939,
        # url='https://www.bilibili.com/bangumi/play/ep276477/',
        url='https://www.bilibili.com/bangumi/media/md28221399/',
    )
    BilibiliBangumi.get(
        subject_id=262939,
        media_id=28221399,
        season_id=28002,
    )

    Bilibili.subject(
        271724,
        'https://www.bilibili.com/bangumi/media/md28221412',
    )
    BilibiliBangumi.get(
        subject_id=271724,
        media_id=28221412,
        season_id=28013,
    )
