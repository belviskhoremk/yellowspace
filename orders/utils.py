from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings


class PDFReceiptGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Company header style
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=10
        ))

        # Receipt title style
        self.styles.add(ParagraphStyle(
            name='ReceiptTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#e74c3c'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))

        # Customer info style
        self.styles.add(ParagraphStyle(
            name='CustomerInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=6
        ))

        # Order info style
        self.styles.add(ParagraphStyle(
            name='OrderInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#7f8c8d')
        ))

        # Total style
        self.styles.add(ParagraphStyle(
            name='Total',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#95a5a6')
        ))

    def generate_receipt(self, order):
        """Generate PDF receipt for an order"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        # Container for the 'Flowable' objects
        elements = []

        # Add company header
        elements.append(Paragraph("YellowSpace", self.styles['CompanyHeader']))
        elements.append(Paragraph("Quality Products • Fast Delivery • Great Service", self.styles['Normal']))
        elements.append(Spacer(1, 20))

        # Add receipt title
        elements.append(Paragraph("ORDER RECEIPT", self.styles['ReceiptTitle']))
        elements.append(Spacer(1, 20))

        # Order information section
        order_info_data = [
            ['Order ID:', f'#{order.id}'],
            ['Order Date:', order.ordered_at.strftime('%B %d, %Y at %I:%M %p')],
            ['Status:', 'Confirmed' if not order.delivered else 'Delivered'],
        ]

        order_info_table = Table(order_info_data, colWidths=[2 * inch, 3 * inch])
        order_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(order_info_table)
        elements.append(Spacer(1, 20))

        # Customer information section
        elements.append(Paragraph("CUSTOMER INFORMATION", self.styles['Heading3']))
        elements.append(Spacer(1, 10))

        customer_info_data = [
            ['Name:', order.customer_name],
            ['Phone:', order.phone_number],
            ['Email:', order.email or 'Not provided'],
            ['Address:', order.address],
        ]

        if order.notes:
            customer_info_data.append(['Notes:', order.notes])

        customer_info_table = Table(customer_info_data, colWidths=[1.5 * inch, 4 * inch])
        customer_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(customer_info_table)
        elements.append(Spacer(1, 30))

        # Order items section
        elements.append(Paragraph("ORDER ITEMS", self.styles['Heading3']))
        elements.append(Spacer(1, 10))

        # Items table header
        items_data = [['Item', 'Quantity', 'Unit Price', 'Total']]

        # Add items
        for item in order.items.all():
            items_data.append([
                item.product.name,
                str(item.quantity),
                f'${item.product.price:.2f}',
                f'${item.total_price():.2f}'
            ])

        # Add total row
        total_price = order.total_price()
        items_data.append(['', '', 'TOTAL:', f'${total_price:.2f}'])

        items_table = Table(items_data, colWidths=[3 * inch, 1 * inch, 1.2 * inch, 1.2 * inch])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('ALIGN', (0, 1), (0, -2), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -2), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 8),

            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(items_table)
        elements.append(Spacer(1, 30))

        # Payment information
        elements.append(Paragraph("PAYMENT INFORMATION", self.styles['Heading3']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Payment Method: Bank Transfer/Mobile Money", self.styles['CustomerInfo']))
        elements.append(Paragraph("Status: Confirmed", self.styles['CustomerInfo']))
        elements.append(Spacer(1, 30))

        # Footer
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Thank you for your business!", self.styles['Footer']))
        elements.append(
            Paragraph("For any questions, please contact us at support@yellowspace.com", self.styles['Footer']))
        elements.append(Paragraph("Visit us at www.yellowspace.com", self.styles['Footer']))

        # Build PDF
        doc.build(elements)

        # FileResponse
        buffer.seek(0)
        return buffer