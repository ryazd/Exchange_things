from .models import Ad


def search_function(ads, search):
    result = []
    search = search.lower()
    for ad in ads:
        title = ad.title.lower()
        description = ad.description.lower()
        if search in title or search in description:
            result.append(ad)

    return result

