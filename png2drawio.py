import sys
from jinja2 import Template
import base64
import re
import urllib.parse
import png

DEBUG = False

DRAWIO_TEMPLATE = """<mxfile>
    <diagram id="xxxxxxxxxxxx" name="Page-1">
        <mxGraphModel dx="{{image_width}}" dy="{{image_height}}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{{image_width}}" pageHeight="{{image_height}}" math="0" shadow="0">
            <root>
                <mxCell id="0" />
                <mxCell id="1" parent="0" />
                <mxCell id="2" value="" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;verticalAlign=top;aspect=fixed;imageAspect=0;image=data:image/png,{{png_data_base64}}" vertex="1" parent="1">
                    <mxGeometry x="0" y="0" width="{{image_width}}" height="{{image_height}}" as="geometry" />
                </mxCell>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

png_path = sys.argv[1]

# read png data and convert to base64 string
png_data = open(png_path, "rb").read()
png_data_base64 = base64.b64encode(png_data).decode('utf-8')

# read png by pypng
png_obj = png.Reader(filename=png_path)
png_obj_read = png_obj.read()
image_width = png_obj_read[0]
image_height = png_obj_read[1]

# read xml template
if DEBUG:
    with open("drawio-new-png-template.xml", "r", encoding="utf8") as f: 
        t = Template(f.read())
else:
    t = Template(DRAWIO_TEMPLATE)

# get rendered xml string
drwaio_xml = t.render(
                    png_data_base64 = png_data_base64,
                    image_width = image_width,
                    image_height = image_height
                )

# minimize rendered xml string
drwaio_xml_minimized = re.sub('\s+(?=<)', '', drwaio_xml).replace("\n", "")

# debug output xml
if DEBUG:
    with open("draw-io-new-png.xml", "w", encoding="utf8") as f:
        f.write(drwaio_xml_minimized)

# debug output html
if DEBUG:
    with open("debug-base-template.html", "r", encoding="utf8") as f: 
        t_html = Template(f.read())
        htmltext = t_html.render(
            png_data_base64 = png_data_base64,
        )
        open("debug-base.html", "w").write(htmltext)


# URL encode xml
drawio_png_text = urllib.parse.quote(drwaio_xml_minimized, safe='')

# debug URL encode xml
if DEBUG:
    with open("draw-io-new-png-encoded.xml", "w", encoding="utf8") as f:
        f.write(drawio_png_text)

# binary encode xml
drawio_png_binary = drawio_png_text.encode()
for i, b in enumerate(drawio_png_binary):
    print(hex(b), end=" ")
    if (i+1)%16 == 0:
        print("")
        break


# insert the tEXt chunk in the input png image
# https://stackoverflow.com/questions/9036152/insert-a-text-chunk-into-a-png-image

TEXT_CHUNK_FLAG = b'tEXt'

def generate_chunk_tuple(type_flag, content):
    return tuple([type_flag, content])


def generate_text_chunk_tuple(str_info):
    type_flag = TEXT_CHUNK_FLAG
    return generate_chunk_tuple(type_flag, bytes(str_info, 'utf-8'))


def insert_text_chunk(target, text, index=1):
    if index < 0:
        raise Exception('The index value {} less than 0!'.format(index))

    reader = png.Reader(filename=target)
    chunks = reader.chunks()
    chunk_list = list(chunks)
    for chunk in chunk_list:
        print(chunk[0], len(chunk[1]))
    chunk_item = generate_text_chunk_tuple(text)
    chunk_list.insert(index, chunk_item)

    with open(target+".out.drawio.png", 'wb') as dst_file:
        png.write_chunks(dst_file, chunk_list)


def _insert_text_chunk_to_png_test():
    src = png_path
    insert_text_chunk(src, "mxfile\0"+drawio_png_text, index=2)

# write png
_insert_text_chunk_to_png_test()