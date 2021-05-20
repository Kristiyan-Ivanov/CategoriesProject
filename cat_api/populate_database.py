import os
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

# tells django where the settings.py modules are located
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cat_api.settings')
import django

django.setup()
from categories.models import Category


def populate_database():
    categories = [
        {'name': 'Foods',
         'description': "General food category.",
         'image': 'https://i1.wp.com/www.eatthis.com/wp-content/uploads/2020/12/unhealthiest-foods-planet.jpg',
         'parent': None,
         'similar_categories': []
         },
        {'name': 'Fruits And Vegetables',
         'description': "All types of fruits and vegetables",
         'image': 'https://www.heart.org/-/media/aha/h4gm/article-images/fruit-and-vegetables.jpg',
         'parent': 'Foods',
         'similar_categories': []
         },
        {'name': 'Apple',
         'description': "An apple a day keeps the doctor away",
         'image': '',
         'parent': 'Fruits And Vegetables',
         'similar_categories': []
         },
        {'name': 'Pear',
         'description': "",
         'image': '',
         'parent': 'Fruits And Vegetables',
         'similar_categories': ['Apple']
         },
        {'name': 'Banana',
         'description': "Bananas",
         'image': '',
         'parent': 'Fruits And Vegetables',
         'similar_categories': []
         },
        {'name': 'Meat',
         'description': "Yummy",
         'image': '',
         'parent': 'Foods',
         'similar_categories': []
         },
        {'name': 'Pork',
         'description': "",
         'image': '',
         'parent': 'Meat',
         'similar_categories': []
         },
        {'name': 'Veal',
         'description': "",
         'image': '',
         'parent': 'Meat',
         'similar_categories': []
         },
    ]

    for c in categories:
        add_category(c['name'], c['description'], c['image'], c['parent'], c['similar_categories'])


def add_category(name, description, image_url, parent, similar_categories):
    print("Adding {} category".format(name))
    category = Category.objects.get_or_create(name=name)[0]
    category.name = name
    category.description = description

    if len(image_url) > 0:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urlopen(image_url).read())
        img_temp.flush()
        category.image.save(os.path.basename(image_url), img_temp)

    if parent:
        parent_object = Category.objects.get(name=parent)
        category.parent = parent_object
    for c in similar_categories:
        category.similar.add(Category.objects.get(name=c))
    category.save()


if __name__ == '__main__':
    print("Populating project's database")
    populate_database()
