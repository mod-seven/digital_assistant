from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docxtpl import InlineImage


class FloatingImage(InlineImage):
    """Плаваюче зображення Word за текстом,
    центроване по горизонталі відносно сторінки.
    """

    def __init__(
        self,
        tpl,
        image_descriptor,
        width=None,
        height=None,
        pos_y=0,
    ):
        super().__init__(
            tpl,
            image_descriptor,
            width=width,
            height=height,
        )
        self.pos_y = pos_y

    def _insert_image(self):
        # Створюємо зображення через docxtpl
        inline_xml = self.tpl.current_rendering_part.new_pic_inline(
            self.image_descriptor,
            self.width,
            self.height,
        ).xml

        drawing = parse_xml(inline_xml)

        # Знаходимо wp:inline
        if drawing.tag == qn("wp:inline"):
            inline = drawing
        else:
            inline_nodes = drawing.xpath(".//wp:inline")
            if not inline_nodes:
                return super()._insert_image()
            inline = inline_nodes[0]

        # Створюємо плаваюче зображення
        anchor = OxmlElement("wp:anchor")
        anchor.set("distT", "0")
        anchor.set("distB", "0")
        anchor.set("distL", "0")
        anchor.set("distR", "0")
        anchor.set("simplePos", "0")
        anchor.set("relativeHeight", "251658240")
        anchor.set("behindDoc", "1")
        anchor.set("locked", "0")
        anchor.set("layoutInCell", "1")
        anchor.set("allowOverlap", "1")

        # Обов'язковий елемент простого позиціювання
        simple_pos = OxmlElement("wp:simplePos")
        simple_pos.set("x", "0")
        simple_pos.set("y", "0")
        anchor.append(simple_pos)

        # Горизонтальне центрування відносно сторінки
        position_h = OxmlElement("wp:positionH")
        position_h.set("relativeFrom", "page")

        align_h = OxmlElement("wp:align")
        align_h.text = "center"

        position_h.append(align_h)
        anchor.append(position_h)

        # Вертикальна позиція відносно абзацу
        position_v = OxmlElement("wp:positionV")
        position_v.set("relativeFrom", "paragraph")

        pos_offset_v = OxmlElement("wp:posOffset")
        pos_offset_v.text = str(self.pos_y)

        position_v.append(pos_offset_v)
        anchor.append(position_v)

        # Переносимо розміри зображення
        for tag in ("wp:extent", "wp:effectExtent"):
            element = inline.find(qn(tag))
            if element is not None:
                anchor.append(element)

        # Зображення не впливає на розташування тексту
        anchor.append(OxmlElement("wp:wrapNone"))

        # Переносимо графічні властивості
        for tag in (
            "wp:docPr",
            "wp:cNvGraphicFramePr",
            "a:graphic",
        ):
            element = inline.find(qn(tag))
            if element is not None:
                anchor.append(element)

        # Формуємо XML для docxtpl
        return (
            "</w:t></w:r>"
            "<w:r><w:drawing>%s</w:drawing></w:r>"
            '<w:r><w:t xml:space="preserve">' % anchor.xml
        )

    def __unicode__(self):
        return self._insert_image()

    def __str__(self):
        return self._insert_image()

    def __html__(self):
        return self._insert_image()
