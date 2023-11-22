import math
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Spacer, KeepTogether
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import Table, TableStyle
from reportlab.platypus.frames import Frame
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.graphics.shapes import Rect, String, Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart3D
from reportlab.pdfbase import pdfmetrics
import json
from datetime import datetime
from django.conf import settings
from xml.sax.saxutils import escape
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Arial', f'{settings.FONTS_PATH}Arial.ttf'))

class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, logo, role, is_client, scan_date, **kw):
        self.allowSplitting = 0
        self.logo = logo
        self.scan_date = scan_date
        self.is_client = is_client
        self.role = role
        BaseDocTemplate.__init__(self, filename, **kw)
        page_width = 21*cm  # Assuming A4 page width
        page_height = 29.7*cm  # Assuming A4 page height

        left_margin = 1*cm
        right_margin = 1*cm
        top_margin = 2.5*cm
        bottom_margin = 3*cm
        
        x1 = left_margin
        y1 = bottom_margin
        width = page_width - (left_margin + right_margin)
        height = page_height - (top_margin + bottom_margin)

        template = PageTemplate('normal', [Frame(x1, y1, width, height, id='F1')], onPage=self.onPage)

        self.addPageTemplates(template)
        # Add a list to hold your table of contents entries.
        self.table_of_contents_entries = []

    # Generates Header and Footer on all pages except heading page
    def onPage(self, canvas, doc):
        if doc.page > 1:  # Skip applying headers and footers on the first page
            canvas.saveState()
            canvas.setFont('Arial', 24)
            canvas.drawImage(f'{settings.BASE_DIR}/static/isaix-logo.png', 1 * cm, 11 * inch, width=3.2*cm, height=1*cm)
            canvas.setFont('Arial', 9)
            canvas.drawString(1*cm, 0.5 * inch, "CONFIDENTIEL")
            canvas.drawString(18.5 * cm, 0.5 * inch, f"Page {doc.page}")  # Adjust the y-coordinate to position the footer
            canvas.linkURL("https://www.isaix.com", (1*inch, 2*cm, 2*inch, 2*cm), color=colors.black, thickness=0.5, relative=1)
            canvas.setStrokeColor(colors.grey)
            canvas.line(1*cm, 2.5*cm, 1*cm+self.width+3*cm, 2.5*cm)  # Draw a line at the top of the footer
            canvas.restoreState()
        else:
            canvas.saveState()
            canvas.drawImage(f'{settings.BASE_DIR}/static/report-banner.jpg', 0 * cm, 3.98 * inch, width=21*cm, 
            height=15.25*cm)
            if self.role.cover_content_access or (self.is_client and self.role.id==4):
                try:
                    canvas.drawImage(f"{settings.MEDIA_ROOT}{self.logo}", 14.2 * cm, 1.25 * inch, width=2*cm, 
                    height=2*cm)
                except Exception as e:
                    canvas.drawImage(f'{settings.BASE_DIR}/static/isaix-logo-1.png', 14.2 * cm, 1.25 * inch, width=2*cm, 
                    height=2*cm)
            canvas.setFont('Arial', 18)
            canvas.setFillColor(colors.white)
            canvas.drawString(1.5 * cm, 9.15 * inch, "Évaluation de la vulnérabilité externe")
            canvas.setFont('Arial', 14)
            canvas.drawString(1.5 * cm, 8.70 * inch, "Produit par les services IsaiX Cyber")
            canvas.setFont('Arial', 12)
            canvas.setFillColor(colors.black)
            canvas.drawRightString(19.8 * cm, 1 * inch, f"Date d'analyse : {self.scan_date}")
            # story.append(Paragraph(f'Production Date: {scan_date}', PS(name='Custom', fontSize=9, alignment=TA_RIGHT)))
            canvas.restoreState()

    # Stores bookmarks for headers to be used in Table of Content
    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))
            elif style == 'Heading2':
                key = 'h2-%s' % self.seq.nextf('heading2')
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (1, text, self.page, key))

    # Add this method to handle TOCEntry notifications.
    def handle_toc_entry(self, args):
        level, text, pageNum = args
        self.table_of_contents_entries.append((level, text, pageNum))

h1 = PS(name = 'Heading1',
 font='Arial',
 fontSize = 18,
 leading = 16,
 spaceAfter=20)
h2 = PS(name = 'Heading2',
 font='Arial',
 fontSize = 12,
 leading = 14,
 textColor = colors.blue,
 spaceAfter=10)

h1_toc = PS(name = 'Heading1',
 font='Arial',
 fontSize = 14,
 leading = 16,
 spaceAfter=32)
h2_toc = PS(name = 'Heading2',
 font='Arial',
 fontSize = 12,
 leading = 14,
 leftIndent = 10,
 textColor = colors.blue,
 spaceAfter=10)

content = PS(name = 'Content',
    font='Arial',
    fontSize=12, 
    spaceAfter=15,
    leading = 14,
    alignment=TA_JUSTIFY)

styles = getSampleStyleSheet()
link_style = PS(
    'Hyperlink',
    font='Arial',
    parent=styles['Normal'],
    fontSize=12,
    spaceAfter=15,
    underline=True,
    leading = 14,
    alignment=TA_JUSTIFY
)

bullet_style = PS(name = 'B&N',
    parent=styles['Bullet'],
    font='Arial',
    fontSize=12,
    spaceAfter=15,
    leading = 14,
    alignment=TA_JUSTIFY,
    leftIndent=20,
    bulletIndent = 20
)

content_layout = PS(
    name = 'ContentLayout',
    font='Arial',
    fontSize=12,
    alignment=TA_JUSTIFY,
    topMargin=78,
    bottomMargin=90,
    borderColor = colors.Color(red=(238.0/255),green=(238.0/255),blue=(238.0/255)),
    backColor = colors.Color(red=(238.0/255),green=(238.0/255),blue=(238.0/255)),
    borderRadius=1,
    borderWidth =1,
    textColor = colors.black,
    borderPadding = 10,
    leftIndent=0.15 * inch,
    spaceBefore=6,
    # spaceAfter=25,
    leading = 14
)

h1_header = PS(name = "HeaderTitle",
    font='Arial',
    fontSize = 42,
    alignment = TA_CENTER,
    spaceAfter=42,
    textColor=colors.blue)

h2_header = PS(name= 'HeaderSubTitle',
    font='Arial',
    fontSize=12, 
    spaceAfter=10,
    alignment=TA_CENTER)

def generate_doc(role, active_plan, cname, scan_date, vulnerabilities, user_name, order, risk_levels, output_path, hosts=[[]],  multiple_ip=False):

    """
    Generates a vulnerability scan report in PDF format.

    :param cname: The name of the company for which the report is generated.
    :param scan_date: The date of scan completion.
    :param vulnerabilities: The vulnerability data.
    vulnerabilities must be in the following format:
        {"alerts":
            {
                "name of alert":{
                    "name": string,
                    "description": string,
                    "urls" (optional): [],
                    "instances": number,
                    "cvss": number,
                    "solution": string,
                    "risk": "Critical" | "High" | "Medium" | "Low" | "Log",
                    "tool": string
                },
                ...
            }
        }

    Hierarchy must be followed but order is not important.
    If one of the sub-attributes of "name of alert" is not present, it will be replaced with "N/A"

    :param hosts: The list of hosts and their details (optional).
        [['192.195.4.1', 'nsi.isaix.com', (1, 2, 3, 4, 5)]]
        list of lists: each list has: ip address, host url, 5-tuple with count of each vulnerability type:
        (Critical, High, Medium, Low, Log)
    :param multiple_ip: Flag indicating whether multiple IP addresses are involved (default is False).
    if multiple_ip = False -> no overview section and no need for hosts input

    """
    # Build story.
    doc = MyDocTemplate(output_path, order.company_logo, role, order.is_client, scan_date)
    section_number = 1

    story = []
    toc = TableOfContents()

    toc.levelStyles = [h1_toc, h2_toc]

    complexities = {
        'critical':'Critique',
        'high':'Élevée',
        'medium':'Moyenne',
        'low':'Faible',
        'info':'Info',
        'informational':'Informative'
    }

    # HEADER
    story.append(Spacer(1, 0.10*inch))
    story.append(Paragraph('Rapport exécutif', PS(name='Custom', fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor("#395c9a"), font='Arial')))
    
    # Add content only if role has access of it
    if role.cover_content_access or (order.is_client and role.id==4):
        story.append(Spacer(1, 6.37*inch))
        story.append(Spacer(1, 0.35*inch))
        story.append(Paragraph('Présenté à :', PS(name='Custom', fontSize=12, textColor=colors.HexColor("#395c9a"), leftIndent=8, font='Arial')))
        story.append(Spacer(1, 0.20*inch))
        user_name = (order.client_name if order.is_client and role.id==4 else user_name)
        user_table = Table(
        [
            [
                Paragraph(f'{user_name}', PS(name='Custom', fontSize=12, font='Arial'))   
            ],[
                Paragraph(f'{order.company_name if order.company_name else ""}', PS(name='Custom', fontSize=12, font='Arial'))
            ],[
                Paragraph(f'{order.company_address if order.company_address else ""}', PS(name='Custom', fontSize=12, font='Arial'))
            ]
        ], colWidths=10*cm, hAlign='LEFT')
        style = TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica'),
            # ('GRID', (0,0), (-1,-1), 1, colors.black)  # Add a black grid around the cells
        ])
        story.append(user_table)
        user_table.setStyle(style)



    # TOC
    story.append(PageBreak())
    story.append(toc)

    # Intro
    intro_sub_section_number = 1
    intro_numbering = 1
    story.append(PageBreak())
    story.append(Paragraph('<a name="intro"></a><b>{}. Introduction</b>'.format(section_number), h1))
    story.append(Paragraph('<a name="welcome"></a><b>{}.{} Objectif</b>'.format(section_number, intro_sub_section_number), h2))
    story.append(Paragraph("Bienvenue dans le rapport d'analyse de vulnérabilité IsaiX Cyber de niveau 1 généré par notre portail hébergé sur le web et nos outils d'analyse automatisés à l'adresse <a href='https://scanner.isaix.com/'><font color=blue>https://scanner.isaix.com/</font></a>. L'objectif de ce rapport est double :", link_style))
    story.append(Paragraph(f"{intro_numbering}. Pour les chefs d'entreprise : fournir une compréhension des vulnérabilités techniques de vos actifs web pour offrir une nouvelle ligne de vue de la gouvernance de votre cyber-résilience et évaluer votre cyber-risque commercial.", bullet_style))
    intro_numbering +=1
    story.append(Paragraph(f"{intro_numbering}. Pour les ressources informatiques : fournir des informations détaillées sur les vulnérabilités de vos actifs web et les références pour remédier ces vulnérabilités.", bullet_style))
    intro_sub_section_number = intro_sub_section_number + 1
    
    story.append(Paragraph("<a name='imp'></a><b>{}.{} Gérer le risque cyber</b>".format(section_number, intro_sub_section_number), h2))
    story.append(Paragraph("Dans le paysage actuel des menaces, les cybercriminels développent chaque jour de nouvelles vulnérabilités pour attaquer votre infrastructure et exploiter votre entreprise. L'exploitation de toute vulnérabilité dans votre cybersécurité peut entraîner des risques financiers, opérationnels et juridiques. Parmi ces risques, citons :", content))
    story.append(Paragraph("<bullet>&bull;</bullet>Le vol ou la perte d'informations par un accès non autorisé et malveillant", bullet_style))
    story.append(Paragraph("<bullet>&bull;</bullet>Interruption de service causée par des systèmes compromis", bullet_style))
    story.append(Paragraph("<bullet>&bull;</bullet>Atteinte à la réputation résultant de fuites ou d'une perte de contrôle et d'une mauvaise orientation de vos actifs web", bullet_style))
    story.append(Paragraph("<bullet>&bull;</bullet>Rançon ou chantage résultant d'un vol", bullet_style))
    story.append(Paragraph("<bullet>&bull;</bullet>Menaces physiques sur les biens ou le personnel par l'intrusion et le contrôle des équipements", bullet_style))
    story.append(Paragraph("<bullet>&bull;</bullet>Infractions à la réglementation et amendes", bullet_style))
    story.append(Paragraph("Pour évaluer le risque commercial associé à une vulnérabilité particulière, celle-ci doit être considérée dans le contexte du système dans lequel elle se trouve, la probabilité que la vulnérabilité soit utilisée par des acteurs malveillants et l'impact potentiel sur l'entreprise si elle était exploitée.", content))
    story.append(Paragraph("L'évaluation régulière de vos vulnérabilités par des tierces parties, la maintenance permanente et diligente de vos systèmes de cybersécurité et la formation régulière de vos employés et partenaires sont des fonctions essentielles de la gouvernance.", content))
    story.append(Paragraph("", content))
    intro_sub_section_number = intro_sub_section_number + 1

    story.append(PageBreak())
    story.append(Paragraph("<a name='goal'></a><b>{}.{}  L'analyse du scan vulnérabilité</b>".format(section_number, intro_sub_section_number), h2))
    story.append(Paragraph("Cette évaluation de niveau 1 a été réalisée par un service automatisé qui utilise un certain nombre d'outils de cybersécurité de source ouverte communément reconnus et des analyses propriétaires pour simuler des attaques ou des exploitations sur les adresses IP cibles évaluées par l'entreprise.", content))
    intro_sub_section_number = intro_sub_section_number + 1
    if multiple_ip :
        story.append(Paragraph('<a name="goal"></a><b>{}.{} Portée des tests</b>'.format(section_number, intro_sub_section_number), h2))
        intro_sub_section_number = intro_sub_section_number + 1
        story.append(Paragraph("IsaiX Cyber a traité les adresses IP cibles saisies par l'intermédiaire de sa plateforme. Il s'agit des adresses suivantes"))
        story.append(Spacer(1, 0.4*inch))
        story.append(Paragraph('<b>IPs / Domains / Hôtes :</b>', h2_header))
        story.append(Spacer(1, 0.2*inch))
        
        # Domain(hosts) table
        table_header = ["Domaine IP", "Nom de domaine"]
        table_data = [[row[0], row[1]] for row in hosts]
        table_data.insert(0, table_header)
        table = Table(table_data, colWidths=7*cm)
        # Add some style to the table (borders, background colors, fonts, etc.)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),  # Add a grey background color to header row
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),  # Change the header text color to white

            ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # Align all text to center
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),  # Change the font of the header row to Helvetica-Bold
            ('FONTSIZE', (0,0), (-1,0), 14),  # Change the font size of the header row to 14

            ('BOTTOMPADDING', (0,0), (-1,0), 12),  # Add more space at the bottom of the header row text
            ('GRID', (0,0), (-1,-1), 1, colors.black)  # Add a black grid around the cells
        ])
        story.append(table)
        story.append(Spacer(1, 0.8*inch))
        # Add the style to the table
        table.setStyle(style)

    story.append(Paragraph("<a name='imp'></a><b>{}.{} Exclusion de responsabilité et limitation de l'analyse</b>".format(section_number, intro_sub_section_number), h2))
    story.append(Paragraph("Bien qu'IsaiX Cyber puisse découvrir de nombreux vecteurs de menaces, aucun système ne peut garantir l'identification de toutes les menaces possibles. IsaiX Cyber n'offre aucune garantie, représentation ou certification légale concernant les applications ou les systèmes qu'il analyse. Rien dans ce document n'est destiné à représenter ou à garantir que les tests de sécurité ont été complets et sans erreur, ni à représenter ou à garantir que l'application ou les systèmes qu'il analyse sont adaptés à la tâche, exempts d'autres défauts que ceux signalés, ou conformes aux normes de l'industrie.", content))
    story.append(Paragraph("Ce rapport ne peut pas et ne protège pas contre les pertes personnelles ou professionnelles résultant de l'utilisation des applications ou des systèmes décrits.", content))
    story.append(Paragraph(f"Ce rapport contient des informations sur les systèmes et/ou les applications web qui existaient à la {scan_date}.", content))
    story.append(Paragraph("L'analyse d'IsaiX Cyber est une évaluation « moment donné » de niveau 1, d'une adresse web externe uniquement et il est donc possible que des vulnérabilités non détectées par l'analyse d'IsaiX existent sur les :", content))
    story.append(Paragraph("a) Réseaux internes;", bullet_style))
    story.append(Paragraph("b) Applications VOIP ou mobiles;", bullet_style))
    story.append(Paragraph("c) Équipements opérationnels;", bullet_style))
    story.append(Paragraph("qui n'ont pas été analysés par notre système, que la configuration des ressources web dans l'environnement a pu changer ou que de nouvelles menaces sont apparues depuis l'analyse d'IsaiX.", content))
    intro_sub_section_number = intro_sub_section_number + 1

    story.append(Paragraph("<a name='imp'></a><b>{}.{} Distribution du présent rapport</b>".format(section_number, intro_sub_section_number), h2))
    story.append(Paragraph("IsaiX recommande que ce rapport soit conservé et diffusé uniquement dans un environnement sécurisé. En acceptant la livraison de ce rapport, l'entreprise dégage IsaiX de toute responsabilité en cas de dommages résultant de sa distribution. IsaiX n'offre aucune garantie que ce fichier PDF n'a pas été modifié par la partie destinataire pour inclure ou omettre des informations qui ne figurent pas dans la version originale de ce rapport exécutif.", content))
    section_number = section_number + 1
    summary_section_number = 1

    # Summary Page
    story.append(PageBreak())
    story.append(Paragraph('<a name="summary"></a><b>{}. Résumé</b>'.format(section_number), h1))

    if active_plan or role.id==1:
        story.append(Paragraph('<a name="exec"></a><b>{}.{} Résumé</b>'.format(section_number, summary_section_number), h2))
        story.append(Paragraph("Ce rapport présente les résultats de la reconnaissance externe et de la détection des vulnérabilités effectuées par IsaiX. Cette analyse a été réalisée en utilisant un accès non accrédité via une approche de test « blackbox » qui analyse vos actifs en contact avec l'extérieur (ex. applications web, services web, sites web de l'entreprise) pour révéler les vulnérabilités et les mauvaises configurations du serveur web. Ces actifs sont les plus susceptibles d'être attaqués et leurs vulnérabilités sont souvent les plus exploitées.", content))
        story.append(Paragraph("Cette évaluation des vulnérabilités peut avoir identifié des failles que votre entreprise devrait traiter avec diligence afin d'empêcher leur exploitation, en tenant compte de la nature, de la gravité et du contexte du risque associé à chaque vulnérabilité. Les détails des vulnérabilités identifiées et leur gravité sont présentés dans ce document et des références à deux bases de données standard de l'industrie de la cybersécurité, le Common Vulnerabilities and Exposures (CVE) et le Common Weakness Enumeration (CWE), sont fournies pour plus de détails.", content))
        summary_section_number+=1
    
    story.append(Paragraph('<a name="results"></a><b>{}.{} Profil de risque</b>'.format(section_number, summary_section_number), h2))
    story.append(Paragraph("Les vulnérabilités identifiées par l'analyse sont regroupées et classées pour chaque cible dans les catégories suivantes : critique, élevée, moyenne, faible et informative. Plus la vulnérabilité est évaluée à un niveau élevé, plus il est probable qu'elle soit exploitée comme moyen d'attaque entraînant, par exemple seulement ; un accès non autorisé, des violations de données, des suppressions et des vols ou une perturbation du système.", content))
    story.append(Paragraph("Le nombre, le type et la gravité des vulnérabilités identifiées dans ce rapport peuvent révéler la qualité de la maintenance de vos systèmes. Pour évaluer le risque global pour les activités de votre entreprise, vous devez tenir compte du contexte de la vulnérabilité, de la valeur de l'actif qui pourrait être compromise, du type de données qui pourraient être perdues ou volées, ainsi que de l'impact d'une violation.", content))
    story.append(Paragraph("La répartition des vulnérabilités sous forme de diagramme à barres est la suivante :", content))

    # Count number of each severity category
    crit = risk_levels['critical']
    high = risk_levels['high']
    med = risk_levels['medium']
    low = risk_levels['low']
    info = risk_levels['informational']
    
    # Bar Chart
    chart = VerticalBarChart3D()
    chart.data = [[crit, high, med, low, info]]
    max_val = max(chart.data[0])
    chart.width = 300
    chart.height = 200
    chart.x = int(doc.width / 2)-150
    chart.y = 5
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(chart.data[0])+10
    # chart.valueAxis.valueStep = 5


    chart.categoryAxis.labels.boxAnchor = 'ne'
    chart.categoryAxis.labels.dx = 8
    chart.categoryAxis.labels.dy = -2
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.categoryNames = [complexities.get('critical'), complexities.get('high'), complexities.get('medium'), complexities.get('low'), complexities.get('info')]
    chart.bars[(0,0)].fillColor = colors.maroon
    chart.bars[(0,1)].fillColor = colors.red
    chart.bars[(0,2)].fillColor = colors.orange
    chart.bars[(0,3)].fillColor = colors.green
    chart.bars[(0,4)].fillColor = colors.blue


    # add values in each bar
    bar_labels = []
    for i, value in enumerate(chart.data[0]):
        if value > 0:
            x_coord = chart.x + (i * (chart.width / len(chart.data[0]))) + (chart.width / (2 * len(chart.data[0]))) # centering the label
            y_coord = chart.y + chart.height * (value / chart.valueAxis.valueMax) - 11 # type: ignore # 5 units above the top of the bar
            bar_label = String(x_coord, y_coord, str(value),
                            fontName='Helvetica', fontSize=10, textAnchor="middle", fillColor=colors.white) # change fill to white
            bar_labels.append(bar_label)

    header_style = PS(
        name='ChartHeader',
        fontName='Helvetica-Bold',  # Change the font name
        fontSize=14,
        textColor=colors.blue  # Change the text color
    )

    drawing = Drawing(500, 275)
    drawing.add(chart)

    # add bar labels to drawing
    for bar_label in bar_labels:
        drawing.add(bar_label)
    header_text = "Vulnérabilités trouvées"
    header_style = getSampleStyleSheet()["Heading2"]
    header_style.fontName = "Helvetica-Bold"  # Set the font name to Helvetica-Bold
    header_style.fontSize = 16  # Set the font size to 16

    # Create the header string
    header_string = String(150, 250, header_text, fontName=header_style.fontName, fontSize=header_style.fontSize,
                        fill=header_style.textColor)

    # Add the header string to the drawing
    drawing.add(header_string)

    story.append(drawing)
    story.append(PageBreak())
    section_number = section_number + 1

    if active_plan or role.id==1:
        # Risk Evaluation
        story.append(Paragraph('<a name="risk_evaluation"></a><b>{}. Évaluation des risques</b>'.format(section_number), h1))
        story.append(Paragraph("Deux systèmes de classification standard bien connus de l'industrie ont été appliqués pour évaluer la gravité des vulnérabilités. Il s'agit des versions 3.0 et 2.0 du Common Vulnerability Scoring System (CVSS) : Common Vulnerability Scoring System (CVSS) versions 3.0 et 2.0. CVSS attribue des scores de gravité pour faciliter la hiérarchisation des plans d'action en fonction de la menace. Les notes sont calculées sur la base d'une formule qui dépend de plusieurs paramètres permettant d'évaluer la facilité et l'impact d'un exploit. Les notes vont de 0 à 10, 10 étant la note la plus élevée.", content))

        table_header_style = PS(name='tableHead',
                        textColor= colors.white,
                        alignment = TA_CENTER,
                        fontSize = 11,
                        leading = 10
                        )


        # Define your data for the table
        risk_eval_table_data = [
            [Paragraph('Sévérité', table_header_style), Paragraph('CVSS v3.0', table_header_style), Paragraph('CVSS v2.0', table_header_style), Paragraph('Définition', table_header_style)],
            [complexities.get('critical'), '9.0-10.0', 'Pas de support',Paragraph("La présence d'une faille est confirmée et elle est actuellement exploitée ou facilement exploitable par des attaquants sur l'internet. Sans attention immédiate, la réputation et les activités de l'entreprise seront compromises.")],
            [complexities.get('high'), '7.0-8.9', '7.0-10.0',Paragraph("La présence d'un défaut est confirmée. L'exploitation de cette vulnérabilité ne nécessite pas de très grandes capacités techniques et/ou matérielles très élevées.")],
            [complexities.get('medium'), '4.0-6.9', '4.0-6.9',Paragraph("La présence d'un défaut doit être confirmée. La configuration n'est pas optimale et doit être améliorée, mais cela n'a pas d'impact immédiat sur la sécurité du système. Les vulnérabilités sont plus difficiles à exploiter et peuvent conduire à un déni de service et à une perte de confidentialité.")],
            [complexities.get('low'), '0.1-3.9', '0.0-3.9',Paragraph("La présence d'un défaut n'a pas pu être déterminée avec certitude, cependant, plusieurs signes indiquent que le système est vulnérable, et qu'une exploration plus poussée est nécessaire pour confirmer l'existence de cette faille. Ces vulnérabilités peuvent entraîner une perte de confidentialité.")],
        ]

        # Get the sample style sheet
        styles = getSampleStyleSheet()


        # Create the table with the data
        risk_table = Table(risk_eval_table_data, colWidths=[2*cm, 3*cm, 3*cm, 10.5*cm])  # Adjust the column widths here

        # Add some style to the table (borders, background colors, fonts, etc.)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),  # Grey background color for header row
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),  # Change the header text color to white
            ('ALIGN', (0,0), (2,-1), 'CENTER'),  # Center align the header and the first 2 columns of data
            ('VALIGN', (0,0), (2,-1), 'MIDDLE'),  # Center justify the header and the first 2 columns of data
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),  # Change the font of the header row to Helvetica-Bold
            ('FONTSIZE', (0,0), (-1,0), 10),  # Change the font size of the header row to 10
            ('BOTTOMPADDING', (0,0), (-1,0), 12),  # Add more space at the bottom of the header row text
            ('BACKGROUND', (0,1), (0,1), colors.purple),  # Add purple background color to first row, first cell
            ('BACKGROUND', (0,2), (0,2), colors.red),  # Add red background color to second row, first cell
            ('BACKGROUND', (0,3), (0,3), colors.orange),  # Add orange background color to third row, first cell
            ('BACKGROUND', (0,4), (0,4), colors.yellow),  # Add yellow background color to fourth row, first cell
            ('GRID', (0,0), (-1,-1), 1, colors.black),  # Add a black grid around the cells
            ('TEXTCOLOR', (0,1), (0, -1), colors.white), # Make font color white for all severity
            ('TEXTCOLOR', (0,4), (0, 4), colors.black), # Make font color black for Low severity
        ])


        # Add the style to the table
        risk_table.setStyle(style)

        # Append the table to the story
        story.append(risk_table)

        story.append(PageBreak())

        # Summary of Findings
        section_number = section_number + 1
        summary_find_section_num = 1
        story.append(Paragraph('<a name="summary_of_findings"></a><b>{}. Résumé des résultats</b>'.format(section_number), h1))
        story.append(Paragraph("Cette section présente les résultats des analyses externes.", content))

        story.append(Paragraph('{}.{} Liste des principales vulnérabilités'.format(section_number, summary_find_section_num), h2))

        if role.tool_access:
            table_header = [Paragraph('Vulnérabilité', table_header_style), Paragraph('Système', table_header_style), Paragraph("Niveau de risque", table_header_style), Paragraph("Nombre d'instances", table_header_style), Paragraph("Outil de détection d'alerte", table_header_style)]
        else:
            table_header = [Paragraph('Vulnérabilité', table_header_style), Paragraph('Système', table_header_style), Paragraph("Niveau de risque", table_header_style), Paragraph("Nombre d'instances", table_header_style)]
        top_vulns = []

        # Only get alerts with high enough risk
        for i, obj in enumerate(vulnerabilities.values()):
            if obj.get('complexity') in ['Critical', 'High', 'Medium', 'Low', 'Informational']:
                alert_ref = obj['alert_ref']
                error = obj['error']
                extracted_data = [
                    Paragraph('<a href="#{}" color="blue">{}</a>'.format(alert_ref,error), style=styles["Normal"]),
                    cname,
                    obj['complexity'],
                    obj['instances'],
                    Paragraph(obj['tool'], style=styles["Normal"])
                ]
                if not role.tool_access:
                    del extracted_data[4]

                top_vulns.append(extracted_data)
    
        top_vulns.insert(0, table_header)

        color_dict = {
            'Critical': {'bg_color': colors.purple, 'font_color': colors.white},
            'High': {'bg_color': colors.red, 'font_color': colors.white},
            'Medium': {'bg_color': colors.orange, 'font_color': colors.white},
            'Low': {'bg_color': colors.yellow, 'font_color': colors.black},
            'Informational': {'bg_color': colors.blue, 'font_color': colors.white},
        }

        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (1, 1), (-1, -1), 'MIDDLE'),
        ])

        for index, row in enumerate(top_vulns):
            if index > 0:  # Skip header row
                level = row[2]
                if level in color_dict:
                    style.add('BACKGROUND', (2, index), (2, index), color_dict[level]['bg_color'])
                    style.add('TEXTCOLOR', (2, index), (2, index), color_dict[level]['font_color'])
                    row[2]=complexities[row[2].lower()]

        if role.tool_access:
            majorVulnTable = Table(top_vulns,  colWidths=[9.5*cm, 2.2*cm, 2.4*cm, 2.1*cm, 2.5*cm])
        else:
            majorVulnTable = Table(top_vulns,  colWidths=[9.5*cm, 2.2*cm, 3.5*cm, 3.5*cm])
        majorVulnTable.setStyle(style)
        story.append(majorVulnTable)

        story.append(PageBreak())


        # Scan Overview
        if multiple_ip:
            section_number = section_number + 1
            story.append(Paragraph('<a name="scan_overview"></a><b>{}. Aperçu du scan</b>'.format(section_number), h1))
            story.append(Paragraph("Cette section indique le nombre d'occurrences de chaque vulnérabilité identifiée par IP/hôte, ainsi que leur niveau de risque. Veuillez noter que le nombre d'occurrences augmente si la même vulnérabilité est détectée sur un autre site web de la même IP/hôte :", content))

            style = TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.purple),  # color for header cell in column 1
                ('BACKGROUND', (1, 0), (1, 0), colors.red),  # color for header cell in column 2
                ('BACKGROUND', (2, 0), (2, 0), colors.orange),  # color for header cell in column 3
                ('BACKGROUND', (3, 0), (3, 0), colors.yellow),  # color for header cell in column 4
                ('BACKGROUND', (4, 0), (4, 0), colors.blue),  # color for header cell in column 5
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),  # Change the header text color to white
                ('TEXTCOLOR', (3, 0), (3, 0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # Align all text to center
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),  # Change the font of the header row to Helvetica-Bold
                ('FONTSIZE', (0,0), (-1,0), 14),  # Change the font size of the header row to 14
                ('BOTTOMPADDING', (0,0), (-1,0), 12),  # Add more space at the bottom of the header row text
                ('GRID', (0,0), (-1,-1), 1, colors.black),  # Add a black grid around the cells
                # ('TEXTCOLOR', (0,1), (0, -1), colors.white), # Make font color of Severity to white
                # ('TEXTCOLOR', (0,4), (0, 4), colors.black), # Make black color for severity Low
            ])
            # Scan overview for multi-host
            for host in hosts:
                story.append(Paragraph(text="Host: {}".format(host[0]), style=h2))
                host_info = [
                    host[2],
                    [complexities.get('critical'), complexities.get('high'), complexities.get('medium'), complexities.get('low'), complexities.get('info')]
                ]
                host_info_table = Table(host_info, colWidths=(3.65*cm,3.65*cm,3.65*cm,3.65*cm,3.65*cm))
                
                host_info_table.setStyle(style)
                story.append(host_info_table)
                story.append(Spacer(1, 1*cm))


            story.append(PageBreak())

        # Detailed vulernability Analysis
        section_number = section_number + 1
        # story.append(Paragraph('<a name="detailed_vulernability_analysis"></a><b>{}. Analyse détaillée des vulnérabilités</b>'.format(section_number), h1))

        for i, alert in enumerate(vulnerabilities.values()):

                extracted_data = [
                    alert['error'],
                    cname,
                    alert['complexity']
                ]
                alert_info = [['Facteur de risque: {}'.format(complexities[alert['complexity'].lower()]), 'Occurrences: {}'.format(alert['instances'])]]
                styles = getSampleStyleSheet()
                cell_style = styles["BodyText"]

                

                table = Table(alert_info, colWidths=(9.3*cm))
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # First row first column alignment
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # First row second column alignment
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align to the middle
                    ('WORDWRAP', (0, 0), (-1, -1), 1),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8.5),
                ])

                if alert['complexity'] == 'Critical':
                    style.add('BACKGROUND', (0, 0), (-1, 0), colors.purple)
                elif alert['complexity'] == 'High':
                    style.add('BACKGROUND', (0, 0), (-1, 0), colors.red)
                elif alert['complexity'] == 'Medium':
                    style.add('BACKGROUND', (0, 0), (-1, 0), colors.orange)
                elif alert['complexity'] == 'Low':
                    style.add('BACKGROUND', (0, 0), (-1, 0), colors.yellow)
                    style.add('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
                else:
                    style.add('BACKGROUND', (0, 0), (-1, 0), colors.blue)


                table.setStyle(style)
                # This is where we render the vulnerability information
                cvvs3 = "N/A"
                cvvs2 = "N/A"
                if alert['alert_json'].get('cvvs3'):
                    cvvs3 = alert['alert_json']['cvvs3']['base_score']
                if alert['alert_json'].get('cvvs2'):
                    cvvs2 = alert['alert_json']['cvvs2']['base_score']

                
                vul_detail = [
                    Paragraph('<a name="detailed_vulernability_analysis"></a><b>{}. Analyse détaillée des vulnérabilités</b>'.format(section_number), h1),
                    Paragraph('<b><a name="{}"/>{}.{} {}</b>'.format(alert['alert_ref'],section_number, i+1, alert['error']), h2 if 'error' in alert else 'N/A'),
                    table, 
                    Spacer(1, 5),  
                    Paragraph('<b>Description:</b> {}'.format(escape(alert['alert_json']['description'])), content), 
                    Paragraph('<b>Solution: </b> {}'.format(alert['alert_json']['solution'] if 'solution' in alert['alert_json'] else 'N/A'), content),
                    Paragraph('<b>CVSS 3: </b> {}'.format(cvvs3), content),
                    Paragraph('<b>CVSS 2: </b> {}'.format(cvvs2), content),
                    Paragraph('<b>Outil: </b> {}'.format(alert['tool']), content),
                    Paragraph('<b>CWE: </b> {}'.format(alert.get('cwe_ids','N/A')), content),
                    Paragraph('<b>Preuve: </b>', content),
                    Paragraph(escape(alert.get('evidence','N/A')).replace("&amp;","&").replace("&lt;br/&gt;","<br/>"), content_layout)
                    ]
                
                if i!=0:
                    del vul_detail[0]

                if not role.tool_access:
                    del vul_detail[7]
                
                table = KeepTogether(vul_detail)

                story.append(table)
                story.append(Spacer(1, 1*cm))
        

    doc.multiBuild(story)
