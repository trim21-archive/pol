from bgm_tv_spider.models import db
from peewee_migrate import Router

router = Router(db)

# Create migration
router.create('create_database')

# Run migration/migrations
router.run('bgm_tv_spider.models')

# Run all unapplied migrations
router.run(fake=True)
