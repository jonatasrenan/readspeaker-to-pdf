import sys

def get_image(url):
    from PIL import Image
    import requests
    from io import BytesIO
    response = requests.get(url)
    print(url)
    if response.content:
        return Image.open(BytesIO(response.content))


def get_page_from_any_server(uid, page):
    global servers
    for server in servers:
        url = "https://%s/docreader/api/get_image.php?name=%s&p=%s" % (server, uid, page)
        image = get_image(url)
        if image:
            servers = [server] + [s for s in servers if s != server]
            return image


def get_all_pages(uid, page=1):
    pages = []
    actual_page = get_page_from_any_server(uid, page)
    pages += [actual_page]
    if actual_page:
        pages += get_all_pages(uid, page+1)
    return [page for page in pages if page]


def convert_to_pdf(name, pages):
    for i, image in enumerate(pages):
        image.save("%s_%s.png" % (name, i))

    from fpdf import FPDF
    pdf = FPDF()
    for image in ["%s_%s.png" % (name, i) for i, _ in enumerate(pages)]:
        pdf.add_page()
        x = 0; y = 0; w = 210; h = 297
        pdf.image(image, x, y, w, h)
    pdf.output("%s.pdf" % name, "F")

    for i, image in enumerate(pages):
        import os
        os.remove("%s_%s.png" % (name, i))


servers = [
    'docreader.readspeaker.com',
    'docreader01-se.readspeaker.com',
    'docreader02-se.readspeaker.com',
    'docreader03-se.readspeaker.com',
]

if len(sys.argv) < 2:
    print("Need pass uid as argument")
    exit

uid = sys.argv[1]

convert_to_pdf(uid, get_all_pages(uid))
print("%s.pdf generated" % uid)
