import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor('#e11d48') # Rose Red Accent
    DARK_BG = colors.HexColor('#0f172a') # Dark Slate Navy
    TEXT_MAIN = colors.HexColor('#1e293b')
    ACCENT_BG = colors.HexColor('#f8fafc')
    BORDER_COLOR = colors.HexColor('#cbd5e1')

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=DARK_BG,
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=PRIMARY,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=DARK_BG,
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MAIN,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_box_style = ParagraphStyle(
        'CodeBox',
        fontName='Courier-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f1f5f9'),
        borderColor=colors.HexColor('#cbd5e1'),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # Header Title Banner
    story.append(Paragraph("ITS Attendance System — Laptop Setup & User Guide", title_style))
    story.append(Paragraph("Information Technology Society (ITS) • Official Cross-Laptop Deployment Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=14))

    # Section 1: Overview
    story.append(Paragraph("1. System Overview & Offline Capability", heading_style))
    story.append(Paragraph("The <b>ITS Attendance System</b> is a 100% offline native desktop application. It requires <b>NO internet connection, NO Wi-Fi, and NO software installations</b> (Node.js/Python are not required on co-officer laptops). All database transactions and barcode scans execute locally in under <b>0.5 milliseconds</b>.", body_style))

    # Section 2: Step-by-Step Setup
    story.append(Paragraph("2. How to Set Up & Run on Any Windows Laptop", heading_style))
    
    steps = [
        ("Step 1: Extract Folder", "Copy the zip archive <b>ITS_Attendance_System_Shared_Release_2026.zip</b> or setup folder onto your laptop or USB flash drive. Right-click the ZIP file and select <b>Extract All</b>."),
        ("Step 2: Create Desktop Shortcut", "Double-click <b>Create Desktop Shortcut.bat</b> inside the extracted folder. This automatically creates an <i>ITS Attendance System</i> launch icon on your Windows Desktop."),
        ("Step 3: Launch Application", "Double-click <b>ITS Attendance System.exe</b> (or your Desktop shortcut). The system will open immediately in full-screen responsive view."),
        ("Step 4: Plug in Barcode Scanner", "Plug any USB 1D/2D Barcode Scanner into your laptop. The scanner works out-of-the-box with zero configuration.")
    ]

    table_data = []
    for step_title, step_desc in steps:
        table_data.append([
            Paragraph(f"<b>{step_title}</b>", body_style),
            Paragraph(step_desc, body_style)
        ])

    step_table = Table(table_data, colWidths=[150, 380])
    step_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_BG),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(step_table)
    story.append(Spacer(1, 10))

    # Section 3: Event Check-in Workflows
    story.append(Paragraph("3. Event Check-in Workflows", heading_style))
    story.append(Paragraph("• <b>Scanning Barcode ID Cards (2nd, 3rd, 4th Years):</b> Point the USB barcode scanner at the student's ID card. The system verifies the ID, logs attendance, and plays a green chime instantly.", bullet_style))
    story.append(Paragraph("• <b>Name Search Check-in (1st Years & Transferees):</b> Type the student's First or Last Name in the search bar. An interactive candidate popup opens showing all matching profiles.", bullet_style))
    story.append(Paragraph("• <b>On-the-Fly Barcode Linking (Dual Option Modal):</b> When selecting a 1st Year student marked <b>[⚠️ PENDING BARCODE]</b>, a custom dialog window opens offering two choices:<br/>"
                           "&nbsp;&nbsp;1. <b>Scan / Type Barcode ID:</b> Point USB scanner at their physical card OR manually type ID number to permanently link it to their profile.<br/>"
                           "&nbsp;&nbsp;2. <b>Log Without Linking:</b> Check them in under their temporary ID if they don't have a card with them.", bullet_style))

    # Section 4: Exporting Excel Reports
    story.append(Paragraph("4. Exporting Attendance Excel Reports", heading_style))
    story.append(Paragraph("Click <b>Export Logs (CSV)</b> on the sidebar. The system opens the native <b>Windows Save As Dialog</b> with an automatically generated smart filename:<br/>"
                           "• <b>[Event_Title]_[PeriodTag]_[Date].xlsx</b> (e.g. <i>JUMPSTART_DAY_2_Morning_Time_IN_2026-09-11.xlsx</i>)<br/>"
                           "• The export includes <b>ONLY actually scanned students</b> (no empty non-attendees) with column widths formatted automatically.", body_style))

    # Section 5: Troubleshooting & Support
    story.append(Paragraph("5. Troubleshooting & Best Practices", heading_style))
    story.append(Paragraph("• <b>System Freeze Protection:</b> The application has built-in WAL database journaling and freeze-proof error handling. If an error occurs, click the <b>Refresh System</b> button to re-sync.<br/>"
                           "• <b>Multiple Laptops:</b> If running 2 or more laptop desks simultaneously, combine the exported Excel files after the event or use a single laptop database.", body_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR, spaceAfter=8))
    story.append(Paragraph("<i>Developed for the Information Technology Society (ITS) • Holy Cross of Davao College</i>", ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor('#64748b'), alignment=1)))

    doc.build(story)
    print(f"Generated Setup Guide PDF at: {filename}")

if __name__ == '__main__':
    target_1 = r"C:\DESKTOP FILES\ITS Attendance System - Final Standalone Release\ITS_Attendance_System_Setup_Guide.pdf"
    target_2 = r"C:\DESKTOP FILES\ITS-Attendance-System\ITS_Attendance_System_Setup_Guide.pdf"
    generate_pdf(target_1)
    generate_pdf(target_2)
