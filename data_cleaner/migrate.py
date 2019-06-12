from peewee_migrate import Router
from bgm_tv_spider.models import db

router = Router(db)

# Create migration
router.create('create_database')

# Run migration/migrations
router.run('bgm_tv_spider.models')

# Run all unapplied migrations
router.run(fake=True)
