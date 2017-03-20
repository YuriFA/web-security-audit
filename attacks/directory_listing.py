PATTERN = "Index of {}"

def directory_listing(page, client):
    title = page.document.title
    if title:
        path = page.parsed_url.path
        if title.text == PATTERN.format(path):
            print("Directory Listing in page {}".format(page.url))
