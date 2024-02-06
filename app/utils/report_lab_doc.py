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
from bs4 import BeautifulSoup
import traceback
import logging
logger = logging.getLogger('django')
import re

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
            canvas.drawString(1*cm, 0.5 * inch, "CONFIDENTIAL")
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
                    canvas.drawImage(f"{settings.MEDIA_ROOT}{self.logo}", 15.30 * cm, 1.25 * inch, width=2*cm, 
                    height=2*cm)
                except Exception as e:
                    canvas.drawImage(f'{settings.BASE_DIR}/static/isaix-logo-1.png', 15.30 * cm, 1.25 * inch, width=2*cm, 
                    height=2*cm)
            canvas.setFont('Arial', 18)
            canvas.setFillColor(colors.white)
            canvas.drawString(1.5 * cm, 9.15 * inch, "External Vulnerability Assessment")
            canvas.setFont('Arial', 14)
            canvas.drawString(1.5 * cm, 8.70 * inch, "Produced by IsaiX Cyber Services")
            canvas.setFont('Arial', 12)
            canvas.setFillColor(colors.black)
            canvas.drawRightString(19.8 * cm, 1 * inch, f'Scan Date: {self.scan_date}')
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

    # Sanitize unclosed tags
    def fix_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        fixed_html = str(soup).replace("<br/>","\n")
        return fixed_html

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
    cve_regex = "(CVE-[0-9]{4}-[0-9]{4,})"
    try:

        # Build story.
        doc = MyDocTemplate(output_path, order.company_logo, role, order.is_client, scan_date)
        section_number = 1

        story = []
        toc = TableOfContents()

        toc.levelStyles = [h1_toc, h2_toc]

        # HEADER
        story.append(Spacer(1, 0.10*inch))
        story.append(Paragraph('Executive Report', PS(name='Custom', fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor("#395c9a"), font='Arial')))
        
        # Add content only if role has access of it
        if role.cover_content_access or (order.is_client and role.id==4):
            story.append(Spacer(1, 6.37*inch))
            story.append(Spacer(1, 0.35*inch))
            story.append(Paragraph('Presented to:', PS(name='Custom', fontSize=12, textColor=colors.HexColor("#395c9a"), leftIndent=8, font='Arial')))
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
        story.append(Paragraph('<a name="welcome"></a><b>{}.{} Purpose</b>'.format(section_number, intro_sub_section_number), h2))
        story.append(Paragraph('Welcome to the IsaiX Cyber Level 1 vulnerability scan report generated through our web-hosted portal and automated scanning tools at <a href="https://scanner.isaix.com/"><font color=blue>https://scanner.isaix.com/</font></a>. The purpose of this report is twofold:', link_style))
        story.append(Paragraph(f"{intro_numbering}. For business leaders: to provide an understanding of the technical vulnerabilities of your web assets and offer a new line of sight to support the governance of your cyber resilience and assess your cyber business risk.", bullet_style))
        intro_numbering +=1
        story.append(Paragraph(f"{intro_numbering}. For IT support resources: to provide detailed insights into the vulnerabilities of your web assets and the references for the remediation of the vulnerabilities.", bullet_style))
        intro_sub_section_number = intro_sub_section_number + 1
        
        story.append(Paragraph('<a name="imp"></a><b>{}.{} Managing your Cyber Risk</b>'.format(section_number, intro_sub_section_number), h2))
        story.append(Paragraph("In today's threat landscape, cyber criminals are developing new vulnerabilities daily to attack your infrastructure and exploit your business. Exploitation of any vulnerability in your cyber security may create financial, operational and legal exposure and risks. Some of these risks include:", content))
        story.append(Paragraph("<bullet>&bull;</bullet>Theft or loss of information through unauthorized and malicious access", bullet_style))
        story.append(Paragraph("<bullet>&bull;</bullet>Disruption of service caused by compromised systems", bullet_style))
        story.append(Paragraph("<bullet>&bull;</bullet>Reputation damage resulting from leaks or a loss of control and mis-direction of your web assets", bullet_style))
        story.append(Paragraph("<bullet>&bull;</bullet>Ransom or blackmail resulting from theft", bullet_style))
        story.append(Paragraph("<bullet>&bull;</bullet>Physical threats to property or personnel through intrusion and control of equipment", bullet_style))
        story.append(Paragraph("<bullet>&bull;</bullet>Regulatory breaches and fines", bullet_style))
        story.append(Paragraph("To assess the business risk associated with a particular vulnerability, the vulnerability must beviewed in the context of the system in which it is found, the likelihood that the vulnerability could be used by malicious actors and the potential impact to the business if it were exploited.", content))
        story.append(Paragraph("Routine, 3rd party assessment of your vulnerabilities and diligent ongoing maintenance of your cyber security systems and the regular training of employees and partners are essential functions of governance.", content))
        story.append(Paragraph("", content))
        intro_sub_section_number = intro_sub_section_number + 1

        story.append(Paragraph('<a name="goal"></a><b>{}.{} The Vulnerability Scan</b>'.format(section_number, intro_sub_section_number), h2))
        story.append(Paragraph("This Level 1 assessment was conducted by an automated service that uses a number of commonly recognized open-source cyber security tools and proprietary scans to simulate attacks or exploitations on the target IP addresses assessed by the company.", content))
        intro_sub_section_number = intro_sub_section_number + 1
        if multiple_ip :
            story.append(Paragraph('<a name="goal"></a><b>{}.{} Testing Scope</b>'.format(section_number, intro_sub_section_number), h2))
            intro_sub_section_number = intro_sub_section_number + 1
            story.append(Paragraph("IsaiX Cyber processed target IP addresses entered through its platform. These were:"))
            story.append(Spacer(1, 0.4*inch))
            story.append(Paragraph('<b>IPs / Domains / Hosts :</b>', h2_header))
            story.append(Spacer(1, 0.2*inch))
            
            # Domain(hosts) table
            table_header = ["IP Address", "Domain Name"]
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

        story.append(Paragraph('<a name="imp"></a><b>{}.{} Disclaimer of Liability and Limitation of the Scan</b>'.format(section_number, intro_sub_section_number), h2))
        story.append(Paragraph("While IsaiX Cyber can discover numerous threat vectors, no system can guarantee the identification of all possible threats. IsaiX Cyber offers no warranties, representations or legal certifications concerning the applications or systems it scans. Nothing in this document is intended to represent or warrant that security testing was complete and without error, nor does this document represent or warrant that the application or systems it scans are suitable to the task, free of other defects than reported, or compliant with any industry standards.", content))
        story.append(Paragraph("This report cannot and does not protect against personal or business loss as the result of use of the applications or systems described.", content))
        story.append(Paragraph(f'This report contains information on the systems and/or web applications that existed as of {scan_date}.', content))
        story.append(Paragraph("IsaiX Cyber’s scanning is a “point in time”, level 1 assessment of external web address (es) only and as such it is possible that vulnerabilities not found by the IsaiX scan exists on:", content))
        story.append(Paragraph("a) Internal networks;", bullet_style))
        story.append(Paragraph("b) VOIP or mobile applications;", bullet_style))
        story.append(Paragraph("c) Operating equipment;", bullet_style))
        story.append(Paragraph("which have not been scanned by our system or that the configuration of the web assets in the environment could have changed, or that new threats have emerged since the IsaiX scan was conducted.", content))
        intro_sub_section_number = intro_sub_section_number + 1

        story.append(Paragraph('<a name="imp"></a><b>{}.{} Distribution of this Report</b>'.format(section_number, intro_sub_section_number), h2))
        story.append(Paragraph("IsaiX recommends that this report be maintained and circulated in a secure environment only. By accepting delivery of this report, the company holds IsaiX harmless of any damages resulting from its distribution.The offers no guarantees that this PDF file has not been edited by the receiving party to include or omit any information not present on the original output of this Executive Report.", content))
        section_number = section_number + 1
        summary_section_number = 1

        # Summary Page
        story.append(PageBreak())
        story.append(Paragraph('<a name="summary"></a><b>{}. Summary</b>'.format(section_number), h1))

        if active_plan or role.id==1:
            story.append(Paragraph('<a name="exec"></a><b>{}.{} Executive Summary</b>'.format(section_number, summary_section_number), h2))
            story.append(Paragraph("This report presents the results of the external reconnaissance and vulnerability detection conducted by IsaiX. This scan was conducted using non-credentialed access via a black-box testing approach which scans your external-facing assets (ex. web applications, web services, company websites) to reveal vulnerabilities and web server misconfigurations. These assets are most susceptible to attack and their vulnerabilities are frequently the most exploited.", content))
            story.append(Paragraph("This vulnerability assessment may have identified flaws that your company should address diligently in order to prevent their exploitation, in consideration of the nature, severity and context of the risk associated with each vulnerability. The details of the vulnerabilities identified, their severity is presented in this document and references to two cyber security industry standard database resources, the Common Vulnerabilities and Exposures (CVE) and the Common Weakness Enumeration (CWE), are provided for further details.", content))
            summary_section_number+=1
        
        story.append(Paragraph('<a name="results"></a><b>{}.{} Risk Profile</b>'.format(section_number, summary_section_number), h2))
        story.append(Paragraph("Vulnerabilities identified by the scan are grouped and classified for each target as critical, high, medium, low, and informative. The higher the vulnerability is rated, the greater the likelihood that this vulnerability could be exploited as avenues of attack resulting in, for example only, unauthorized access, data breaches, deletions and theft or system system disruption.", content))
        story.append(Paragraph("The number, type and severity of the identified vulnerabilities, identified in this report may reveal how well your systems are being maintained. To assess the overall risk to your business operations you must consider the context of the vulnerability, value of the asset that could be compromised, the type of data that could be lost or stolen, against the impact of a breach.", content))
        story.append(Paragraph("The bar graph breakdown of the vulnerabilities are as follows:", content))

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
        chart.categoryAxis.categoryNames = ['Critical', 'High', 'Medium', 'Low', 'Info']
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
        header_text = "Vulnerabilities Found"
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
            story.append(Paragraph('<a name="risk_evaluation"></a><b>{}. Risk Evaluation</b>'.format(section_number), h1))
            story.append(Paragraph("Two well-known industry standard classification systems were applied to assess the severity of vulnerabilities. These were: Common Vulnerability Scoring System (CVSS) versions 3.0 and 2.0. CVSS assigns severity scores to facilitate the prioritization of action plans according to the threat. Scores are calculated based on a formula that depends on several metrics that approximate ease and impact of an exploit. Scores range from 0 to 10, with 10 being the most severe.", content))

            table_header_style = PS(name='tableHead',
                            textColor= colors.white,
                            alignment = TA_CENTER,
                            fontSize = 11,
                            leading = 10
                            )


            # Define your data for the table
            risk_eval_table_data = [
                [Paragraph('Severity', table_header_style), Paragraph('CVSS v3.0', table_header_style), Paragraph('CVSS v2.0', table_header_style), Paragraph('Definition', table_header_style)],
                ['Critical', '9.0-10.0', 'Not supporting',Paragraph('The presence of a flaw is confirmed and is currently exploited or easily exploited by attackers on the Internet. Without immediate attention, the reputation and operations of the company will be compromised.')],
                ['High', '7.0-8.9', '7.0-10.0',Paragraph('The presence of a fault is confirmed. Exploitation of this vulnerability does not require very high technical and / or material capacities.')],
                ['Medium', '4.0-6.9', '4.0-6.9',Paragraph('The presence of a fault is to be confirmed. The configuration is not optimal and should be improved, however, this has no immediate impact on the security of the system. More difficult vulnerabilities to exploit that can lead to a denial of service and possibly loss of confidentiality')],
                ['Low', '0.1-3.9', '0.0-3.9',Paragraph('The presence of a fault could not be determined with certainty, however, there are several signs that the system is vulnerable, and that further exploration is needed to confirm the existence of this flaw. These vulnerabilities can lead to loss of confidentiality')],
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
            story.append(Paragraph('<a name="summary_of_findings"></a><b>{}. Summary of Findings</b>'.format(section_number), h1))
            story.append(Paragraph('In this section, the results of the external scans are represented.', content))

            story.append(Paragraph('{}.{} Major Vulnerabilities List'.format(section_number, summary_find_section_num), h2))

            if role.tool_access:
                table_header = [Paragraph('Vulnerability', table_header_style), Paragraph('System', table_header_style), Paragraph('Risk Level', table_header_style), Paragraph('No. of Instances', table_header_style), Paragraph('Alert Detection Tool', table_header_style)]
            else:
                table_header = [Paragraph('Vulnerability', table_header_style), Paragraph('System', table_header_style), Paragraph('Risk Level', table_header_style), Paragraph('No. of Instances', table_header_style)]
            top_vulns = []

            # Only get alerts with high enough risk
            for i, obj in enumerate(vulnerabilities.values()):
                if obj.get('complexity') in ['Critical', 'High', 'Medium', 'Low', 'Informational']:
                    alert_ref = obj['alert_ref']
                    error = obj['error']
                    extracted_data = [
                        Paragraph('<a href="#{}" color="blue">{}</a>'.format(alert_ref, escape(doc.fix_html(error))), style=styles["Normal"]),
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

            if role.tool_access:
                majorVulnTable = Table(top_vulns,  colWidths=[9.9*cm, 1.8*cm, 2.4*cm, 2.1*cm, 2.5*cm])
            else:
                majorVulnTable = Table(top_vulns,  colWidths=[9.9*cm, 1.8*cm, 3.5*cm, 3.5*cm])
            majorVulnTable.setStyle(style)
            story.append(majorVulnTable)

            story.append(PageBreak())

            # Scan Overview
            if multiple_ip:
                section_number = section_number + 1
                story.append(Paragraph('<a name="scan_overview"></a><b>{}. Scan Overview</b>'.format(section_number), h1))
                story.append(Paragraph('This section represents the Number of Occurrences for each identified vulnerability per IP / Host along with their risk level. Please note that the Number of Occurrence increases if the same vulnerability is found on another website on the same IP/Host:', content))

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
                        ['Critical', 'High', 'Medium', 'Low', 'Info']
                    ]
                    host_info_table = Table(host_info, colWidths=(3.65*cm,3.65*cm,3.65*cm,3.65*cm,3.65*cm))
                    
                    host_info_table.setStyle(style)
                    story.append(host_info_table)
                    story.append(Spacer(1, 1*cm))


                story.append(PageBreak())

            # Detailed vulernability Analysis
            section_number = section_number + 1
            # story.append(Paragraph('<a name="detailed_vulernability_analysis"></a><b>{}. Detailed vulernability Analysis</b>'.format(section_number), h1))

            for i, alert in enumerate(vulnerabilities.values()):

                    extracted_data = [
                        alert['error'],
                        cname,
                        alert['complexity']
                    ]
                    alert_info = [['Risk Factor: {}'.format(alert['complexity']), 'Occurences: {}'.format(alert['instances'])]]
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
                        Paragraph('<a name="detailed_vulernability_analysis"></a><b>{}. Detailed vulernability Analysis</b>'.format(section_number), h1),
                        Paragraph('<b><a name="{}"></a>{}.{} {}</b>'.format(alert['alert_ref'],section_number, i+1, escape(doc.fix_html(alert['error']))), h2 if 'error' in alert else 'N/A'),
                        table,
                        Spacer(1, 5),
                        KeepTogether(Paragraph('<b>Description:</b> {}'.format(escape(doc.fix_html(alert['alert_json']['description']))), content)),
                        Paragraph('<b>Solution: </b> {}'.format(alert['alert_json']['solution'] if 'solution' in alert['alert_json'] else 'N/A'), content),
                        Paragraph('<b>CVSS 3: </b> {}'.format(cvvs3), content),
                        Paragraph('<b>CVSS 2: </b> {}'.format(cvvs2), content),
                        Paragraph('<b>Tool: </b> {}'.format(alert['tool']), content),
                        Paragraph('<b>CWE: </b> {}'.format(alert.get('cwe_ids','N/A')), content),
                        Paragraph('<b>Evidence: </b>', content),
                        Paragraph(escape(doc.fix_html(alert.get('evidence','N/A'))), content_layout)
                        ]
                    
                    # Add Extra field called CVE in vulnerability details if tool is openvas
                    if alert['tool'] == "openvas":
                        cves = list(re.findall(cve_regex,alert.get('alert_json', {}).get('reference','')))
                        cves = ", ".join(cves) if cves else "N/A"
                        vul_detail.insert(10,
                            Paragraph('<b>CVE: </b> {}'.format(cves), content),
                        )
                    
                    if i!=0:
                        del vul_detail[0]
                    
                    if not role.tool_access:
                        del vul_detail[7]
                    
                    table = KeepTogether(vul_detail)
                    story.append(table)
                    story.append(Spacer(1, 1*cm))
            
        doc.multiBuild(story)
    
    except Exception as e:
        traceback.print_exc()
        logger.error(str(e))
        raise Exception("Something went wrong")