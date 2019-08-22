import json

from app.video_website_spider import SupportWebsite

with open('data_manager/patch.json', 'r', encoding='utf8') as f:
    data = json.load(f)
with open('data_manager/patch.json', 'w+', encoding='utf8') as f:
    json.dump(
        {
            key: [x for x in data if x['website'] == key]
            for key in SupportWebsite
        },
        f,
        indent=2,
        ensure_ascii=False,
    )
