from xml.etree import ElementTree

from markdown import Extension
from markdown.inlinepatterns import Pattern


class ConvertImgWikiToHtml(Extension):
    """
    职责：将图片链接拓展注册
    """

    def extendMarkdown(self, md):
        image_pattern = ConvertImgWikiToHtmlImagePattern(r"!\[\[(.*?)\]\]")
        md.inlinePatterns.register(image_pattern, "image", 175)


class ConvertImgWikiToHtmlImagePattern(Pattern):
    """
    职责：将 ![[imagename]] 转化为 <img src="/image?name=imagename">
    """

    def handleMatch(self, m):
        imagename = m.group(2)
        element = self.createImageElement(imagename)
        return element

    def createImageElement(self, imagename):
        element = ElementTree.Element("img")
        element.set("src", f"/image?name={imagename}")
        return element


def makeExtension(**kwargs):
    return ConvertImgWikiToHtml(**kwargs)
