# Waystream EPUB inspection

- path: `artifacts/epubs/way_stream_sanctuary/way_stream_sanctuary__corporate_managers__burnout__overwhelm.epub`
- bytes:  1749304
- sha256: b9ca5f30e4dc771b702af3b1bf49a974a879e36fc8eea9bdabb5efd75421298b
- tip SHA inspected against: 8338e5f30dd9f7d9691179e359571f7d730ec100

## ZIP members (first 40)
```
Archive:  artifacts/epubs/way_stream_sanctuary/way_stream_sanctuary__corporate_managers__burnout__overwhelm.epub
  Length      Date    Time    Name
---------  ---------- -----   ----
       20  06-25-2026 09:15   mimetype
      251  06-25-2026 09:15   META-INF/container.xml
     3293  06-25-2026 09:15   EPUB/content.opf
  1718172  06-25-2026 09:15   EPUB/cover.png
      340  06-25-2026 09:15   EPUB/cover.xhtml
      835  06-25-2026 09:15   EPUB/style/default.css
      877  06-25-2026 09:15   EPUB/title.xhtml
     7220  06-25-2026 09:15   EPUB/chapter_01.xhtml
    10369  06-25-2026 09:15   EPUB/chapter_02.xhtml
     9127  06-25-2026 09:15   EPUB/chapter_03.xhtml
     4781  06-25-2026 09:15   EPUB/chapter_04.xhtml
     9131  06-25-2026 09:15   EPUB/chapter_05.xhtml
     7618  06-25-2026 09:15   EPUB/chapter_06.xhtml
     8625  06-25-2026 09:15   EPUB/chapter_07.xhtml
     6439  06-25-2026 09:15   EPUB/chapter_08.xhtml
     7313  06-25-2026 09:15   EPUB/chapter_09.xhtml
     4957  06-25-2026 09:15   EPUB/chapter_10.xhtml
     5976  06-25-2026 09:15   EPUB/chapter_11.xhtml
     5521  06-25-2026 09:15   EPUB/chapter_12.xhtml
     2335  06-25-2026 09:15   EPUB/toc.ncx
     1461  06-25-2026 09:15   EPUB/nav.xhtml
---------                     -------
  1814661                     21 files
```

## Required package files
- PASS exists: mimetype
- PASS exists: META-INF/container.xml
- mimetype content: `application/epub+zip`

## container.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile media-type="application/oebps-package+xml" full-path="EPUB/content.opf"/>
  </rootfiles>
</container>
```

- OPF path: `EPUB/content.opf`
- PASS OPF exists

## OPF spine / manifest excerpt
```xml
<?xml version='1.0' encoding='utf-8'?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="id" version="3.0" prefix="rendition: http://www.idpf.org/vocab/rendition/#">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <meta property="dcterms:modified">2026-06-25T09:15:02Z</meta>
    <meta name="generator" content="Ebook-lib 0.20.0"/>
    <dc:identifier id="id">phoenix-omega-45d562b70bc30e87</dc:identifier>
    <dc:title>After the Flame: When Everything Is Too Much: A Real Talk Guide to Burnout Recovery for Managers</dc:title>
    <dc:language>en</dc:language>
    <dc:creator id="creator">Theo Castellan</dc:creator>
    <dc:publisher>Waystream Sanctuary</dc:publisher>
    <dc:description>A Real Talk Guide to Burnout Recovery for Managers. A therapeutic book by Theo Castellan, published by Waystream Sanctuary. Part of the Phoenix Omega series.</dc:description>
    <dc:subject></dc:subject>
    <dc:date>2026-06-25</dc:date>
    <dc:rights>Written for emotional clarity: secular, somatic language for managers navigating burnout — not medical advice; seek professional care when you need it.</dc:rights>
    <meta name="cover" content="cover-img"></meta>
  </metadata>
  <manifest>
    <item href="cover.png" id="cover-img" media-type="image/png" properties="cover-image"/>
    <item href="cover.xhtml" id="cover" media-type="application/xhtml+xml"/>
    <item href="style/default.css" id="style" media-type="text/css"/>
    <item href="title.xhtml" id="chapter_0" media-type="application/xhtml+xml"/>
    <item href="chapter_01.xhtml" id="chapter_1" media-type="application/xhtml+xml"/>
    <item href="chapter_02.xhtml" id="chapter_2" media-type="application/xhtml+xml"/>
    <item href="chapter_03.xhtml" id="chapter_3" media-type="application/xhtml+xml"/>
    <item href="chapter_04.xhtml" id="chapter_4" media-type="application/xhtml+xml"/>
    <item href="chapter_05.xhtml" id="chapter_5" media-type="application/xhtml+xml"/>
    <item href="chapter_06.xhtml" id="chapter_6" media-type="application/xhtml+xml"/>
    <item href="chapter_07.xhtml" id="chapter_7" media-type="application/xhtml+xml"/>
    <item href="chapter_08.xhtml" id="chapter_8" media-type="application/xhtml+xml"/>
    <item href="chapter_09.xhtml" id="chapter_9" media-type="application/xhtml+xml"/>
    <item href="chapter_10.xhtml" id="chapter_10" media-type="application/xhtml+xml"/>
    <item href="chapter_11.xhtml" id="chapter_11" media-type="application/xhtml+xml"/>
    <item href="chapter_12.xhtml" id="chapter_12" media-type="application/xhtml+xml"/>
    <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
    <item href="nav.xhtml" id="nav" media-type="application/xhtml+xml" properties="nav"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="nav"/>
    <itemref idref="chapter_0"/>
    <itemref idref="chapter_1"/>
    <itemref idref="chapter_2"/>
    <itemref idref="chapter_3"/>
    <itemref idref="chapter_4"/>
    <itemref idref="chapter_5"/>
    <itemref idref="chapter_6"/>
    <itemref idref="chapter_7"/>
    <itemref idref="chapter_8"/>
    <itemref idref="chapter_9"/>
    <itemref idref="chapter_10"/>
    <itemref idref="chapter_11"/>
    <itemref idref="chapter_12"/>
  </spine>
</package>
```

- sample content doc: `/tmp/waystream_epub_inspect.CtKX4o/EPUB/chapter_08.xhtml`

## Tiny readable excerpt
```
Chapter 8 Chapter 8 The People You're Rescuing I see my own boss in the way I operate now. He was someone who handled everything with perfect composure, who never seemed rattled, who modeled the belief that you solve problems by working harder and showing less vulnerability. I became him. And now people are becoming me. Crouch a little closer. The grain of the wood becomes visible. I want to sit with you in the inheritance pattern. The leaders who came before me showed me what leadership looks l
```

TEMP_EXTRACT=/tmp/waystream_epub_inspect.CtKX4o
