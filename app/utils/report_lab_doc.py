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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Rect, String, Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart3D
from reportlab.pdfbase import pdfmetrics
import json
from datetime import datetime
from django.conf import settings

class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        page_width = 21*cm  # Assuming A4 page width
        page_height = 29.7*cm  # Assuming A4 page height

        left_margin = 1*cm
        right_margin = 1*cm
        top_margin = 2.5*cm
        bottom_margin = 2.5*cm

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
            canvas.setFont('Helvetica', 24)
            canvas.setFillColor(colors.blue)  # Set the color to blue
            canvas.drawString(1 * cm, 11 * inch, "ISAIX")  # Adjust the y-coordinate to position the header
            canvas.setFont('Helvetica', 9)
            canvas.drawImage(f'{settings.BASE_DIR}/static/isaix-logo.png', 1*cm, 0.8*cm, width=3.2*cm, height=1*cm)
            canvas.drawString(18.5 * cm, 0.5 * inch, f"Page {doc.page}")  # Adjust the y-coordinate to position the footer
            canvas.linkURL("https://www.isaix.com", (1*inch, 2*cm, 2*inch, 2*cm), color=colors.black, thickness=0.5, relative=1)
            canvas.setStrokeColor(colors.grey)
            canvas.line(1*cm, 2.5*cm, 1*cm+self.width+3*cm, 2.5*cm)  # Draw a line at the top of the footer
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

h1_header = PS(name = "HeaderTitle",
    font='Arial',
    fontSize = 42,
    alignment = TA_CENTER,
    spaceAfter=42,
    textColor=colors.blue)

h2_header = PS(name= 'HeaderSubTitle',
    font='Arial',
    ontSize=12, 
    spaceAfter=10,
    alignment=TA_CENTER)

def generate_doc(cname, date, vulnerabilities, risk_levels, output_path, hosts=[[]],  multiple_ip=False):

    """
    Generates a vulnerability scan report in PDF format.

    :param cname: The name of the company for which the report is generated.
    :param date: The date of scan completion.
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
    doc = MyDocTemplate(output_path)
    section_number = 1

    story = []
    toc = TableOfContents()

    toc.levelStyles = [h1_toc, h2_toc]

    # HEADER
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph('ISAIX', h1_header))
    story.append(Paragraph('Scan Report', h2_header))
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph('Created for: {}'.format(cname), h2_header))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph('Created on: {}'.format(date), h2_header))
    story.append(PageBreak())

    # TOC
    story.append(toc)

    # Intro
    intro_sub_section_number = 1
    story.append(PageBreak())
    story.append(Paragraph('<a name="intro"></a><b>{}. Introduction</b>'.format(section_number), h1))

    story.append(Paragraph('<a name="welcome"></a><b>{}.{} Welcome</b>'.format(section_number, intro_sub_section_number), h2))
    story.append(Paragraph("Welcome to our comprehensive cybersecurity vulnerability scan report. "
                                "The purpose of this report is to provide detailed insights into the "
                                "security posture of your information system.", content))
    intro_sub_section_number = intro_sub_section_number + 1
    
    story.append(Paragraph('<a name="imp"></a><b>{}.{} Why This Scan Is Important</b>'.format(section_number, intro_sub_section_number), h2))
    intro_sub_section_number = intro_sub_section_number + 1
    story.append(Paragraph("In today's digital era, the threat landscacontenttantly evolving, with new vulnerabilities emerging regularly. These vulnerabilities, if left undetected, could lead to serious breaches, causing loss of data, financial losses, and damage to your organization's reputation.", content))

    story.append(Paragraph('<a name="goal"></a><b>{}.{} Our Goal</b>'.format(section_number, intro_sub_section_number), h2))
    story.append(Paragraph("With this vulnerability scan, we aim to identify, categorize, and prioritize potential vulnerabilities in your system. Our approach includes a detailed analysis of the network and system components, using the latest tools and techniques in the cybersecurity domain. The subsequent sections will outline our findings, recommendations, and strategies to mitigate the detected vulnerabilities.", content))
    intro_sub_section_number = intro_sub_section_number + 1

    story.append(Paragraph("We encourage you to review this report thoroughly and consider the recommended steps to enhance the security posture of your organization.", content))
    if multiple_ip :
        story.append(Paragraph('<a name="goal"></a><b>{}.{} Testing Scope</b>'.format(section_number, intro_sub_section_number), h2))
        intro_sub_section_number = intro_sub_section_number + 1
        story.append(Paragraph("Per {}'s request 3 public IP addresses which are hosting 10 domains that must be penetration tested by 3rd party. Here is the list:".format(cname)))
        story.append(Spacer(1, 1*inch))

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

        # Add the style to the table
        table.setStyle(style)

        story.append(table)
    section_number = section_number + 1
    summary_section_number = 1

    # Summary Page
    story.append(PageBreak())
    story.append(Paragraph('<a name="summary"></a><b>{}. Summary</b>'.format(section_number), h1))

    story.append(Paragraph('<a name="exec"></a><b>{}.{} Executive Summary</b>'.format(section_number, summary_section_number), h2))
    story.append(Paragraph("The executive summary provides a high-level overview of the cybersecurity scanning tool's findings and key takeaways. It aims to provide a concise and clear understanding of the overall security posture of the system being scanned.", content))

    story.append(Paragraph("ISAIX's Cybersecurity Scanning Tool Report has successfully assessed the security vulnerabilities and risks within the targeted system. By analyzing the scan results and findings, we have identified potential areas of concern that demand immediate attention. This executive summary presents an overview of the scan results, our key findings, and a comprehensive risk assessment to facilitate informed decision-making regarding the system's security.", content))

    story.append(Paragraph('<a name="results"></a><b>{}.{} Scan Results</b>'.format(section_number, summary_section_number), h2))
    story.append(Paragraph("The scan results section delves into the specific vulnerabilities and weaknesses uncovered during the cybersecurity scanning process. It provides a detailed account of the security issues discovered and presents relevant metrics and statistics to quantify the severity and prevalence of each vulnerability.", content))

    # Count number of each severity category
    crit = risk_levels['critical']
    high = risk_levels['high']
    med = risk_levels['medium']
    low = risk_levels['low']
    info = risk_levels['informational']
    story.append(Paragraph("During the comprehensive scan conducted by ISAIX's Cybersecurity Scanning Tool, we identified several critical and high-risk vulnerabilities within the target system. These vulnerabilities expose potential avenues for unauthorized access, data breaches, and system compromise. Our scan results revealed a total of {} vulnerabilities, categorized as critical, high, medium, and low risk based on their potential impact and exploitability. The detailed breakdown of the vulnerabilities is as follows:".format(sum([crit, high, med, low])), content))

    
    
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
    # Risk Evaluation    
    story.append(Paragraph('{}. Risk Evaluation'.format(section_number), h1))
    story.append(Paragraph("We used CVSS [ Common Vulnerability Scoring System (CVSS) ] in this project. It's an open industry standard for assessing the severity of computer system security vulnerabilities. CVSS attempts to assign severity scores to vulnerabilities, allowing responders to prioritize responses and resources according to threat. Scores are calculated based on a formula that depends on several metrics that approximate ease and impact of an exploit. Scores range from 0 to 10, with 10 being the most severe. While many utilize only the CVSS Base score for determining severity, temporal and environmental scores also exist, to factor in availability of mitigations and how widespread vulnerable systems are within an organization, respectively.", content))

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
    story.append(Paragraph('{}. Summary of Findings'.format(section_number), h1))
    story.append(Paragraph('In this section, the results of the external reconnaissance, vulnerability detection and penetration tests are represented.', content))

    story.append(Paragraph('{}.{} Major Vulnerabilities List'.format(section_number, summary_find_section_num), h2))

    table_header = [Paragraph('Vulnerability', table_header_style), Paragraph('System', table_header_style), Paragraph('Risk Level', table_header_style), Paragraph('Number of Instances', table_header_style), Paragraph('Alert Detection Tool', table_header_style)]

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
                obj['tool']
            ]

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

    majorVulnTable = Table(top_vulns,  colWidths=[9.9*cm, 1.8*cm, 2.4*cm, 2.1*cm, 2.5*cm])
    majorVulnTable.setStyle(style)
    story.append(majorVulnTable)

    story.append(PageBreak())

    # Summary Overview
    if multiple_ip:
        section_number = section_number + 1
        story.append(Paragraph('{}. Scan Overview'.format(section_number), h1))
        story.append(Paragraph('This section represents the Number of Occurrences for each identified vulnerability per IP / Host along with their Risk Levels. Please note that the Number of Occurrence corresponds increases if the same vulnerability is found on another web site on the same IP/Host:', content))

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
    story.append(Paragraph('{}. Detailed Vulnerabilities Analysis'.format(section_number), h1))

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

            
            table = KeepTogether([
                Paragraph('<b><a name="{}"/>{}.{} {}</b>'.format(alert['alert_ref'],section_number, i+1, alert['error']), h2 if 'error' in alert else 'N/A'),
                table, 
                Spacer(1, 5),  
                Paragraph('<b>Description:</b> {}'.format(alert['alert_json']['description']), content), 
                Paragraph('<b>Solution: </b> {}'.format(alert['alert_json']['solution'] if 'solution' in alert['alert_json'] else 'N/A'), content),
                Paragraph('<b>CVSS 3: </b> {}'.format(cvvs3), content),
                Paragraph('<b>CVSS 2: </b> {}'.format(cvvs2), content),
                Paragraph('<b>Tool: </b> {}'.format(alert['tool']), content)
                ])

            story.append(table)
            story.append(Spacer(1, 1*cm))
        

    doc.multiBuild(story)
