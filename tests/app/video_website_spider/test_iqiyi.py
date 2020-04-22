import pytest

from app.db.mysql import Session
from app.db_models import sa
from app.video_website_spider.iqiyi import Iqiyi


def test_init():
    Iqiyi()


def test_valid_ep_url():
    pass


def test_valid_subject_url():
    pass


def test_submit_ep(db_session: Session):
    values = {"subject_id": 239816, "ep_id": 831189, "source_ep_id": "v_19rr5fzwtg"}
    db_session.query(sa.EpIqiyi).filter_by(**values).delete()

    db_session.commit()

    Iqiyi.ep(
        ep_id=831189, url="https://www.iqiyi.com/v_19rr5fzwtg.html",
    )

    try:
        db_session.query(sa.EpIqiyi).filter_by(**values)
    except Exception:
        raise

    finally:
        db_session.close()


@pytest.mark.skip
def test_submit_bangumi(db_session: Session):
    bangumi_values = {"subject_id": 219200, "bangumi_id": "a_19rrh1ss1p"}
    ep_values = {
        "source_ep_id": "v_19rrfjvdww",
        "ep_id": 767808,
        "subject_id": 219200,
        "title": "擅长捉弄的高木同学 第3集",
    }

    db_session.query(sa.BangumiIqiyi).filter_by(**bangumi_values).delete()
    db_session.query(sa.EpIqiyi).filter_by(**ep_values).delete()
    db_session.commit()

    Iqiyi.subject(
        subject_id=219200, url="https://www.iqiyi.com/a_19rrh1ss1p.html",
    )

    db_session.query(sa.BangumiIqiyi).filter_by(**bangumi_values).one()
    db_session.query(sa.EpIqiyi).filter_by(**ep_values).one()
