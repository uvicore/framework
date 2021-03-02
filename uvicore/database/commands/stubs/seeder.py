import uvicore
#from faker import Faker
from xx_vendor.xx_appname.models import xx_ModelName
from uvicore.support.dumper import dump, dd


@uvicore.seeder()
async def seed():
    uvicore.log.item('Seeding xx_modelname')
    xx_modelname_items = []
    fake = Faker()
    for _ in range(2):
        title = fake.text(max_nb_chars=50)
        xx_modelname = xx_ModelName(
            slug=fake.slug(title),
            title=title,
            creator_id=1,
        )
        xx_modelname_items.append(xx_modelname)

    # Bulk insert
    await xx_ModelName.insert(xx_modelname_items)
