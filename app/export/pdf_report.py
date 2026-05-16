"""
Agro AI — PDF Report Generator
Professional branded PDF reports using ReportLab.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.settings import EXPORT_DIR

logger = logging.getLogger("agro_ai.export.pdf")


class PDFReportGenerator:
    """
    Professional PDF hisobot yaratish.
    ReportLab orqali branded, vizual, professional.
    """

    def __init__(self, account_id: str = "agro_uruglar", brand: str = "@agro_uruglar_"):
        self.account_id = account_id
        self.brand = brand
        self.output_dir = EXPORT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_strategy_report(
        self,
        stats: Optional[Dict] = None,
        recommendations: List[str] = None,
        ideas: List[Dict] = None,
        title: str = "Viral Strategiya Hisoboti",
    ) -> Optional[str]:
        """
        To'liq strategiya PDF hisoboti.
        Returns: fayl yo'li yoki None.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import cm, mm
            from reportlab.platypus import (
                Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
            )
        except ImportError:
            logger.error("reportlab o'rnatilmagan: pip install reportlab")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.account_id}_strategy_{timestamp}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath), pagesize=A4,
            rightMargin=2 * cm, leftMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Title"],
            fontSize=22, spaceAfter=20, textColor=colors.HexColor("#1a1d27"),
        )
        heading_style = ParagraphStyle(
            "CustomHeading", parent=styles["Heading2"],
            fontSize=14, spaceAfter=10, spaceBefore=20,
            textColor=colors.HexColor("#6366f1"),
        )
        body_style = ParagraphStyle(
            "CustomBody", parent=styles["Normal"],
            fontSize=10, spaceAfter=6, leading=14,
        )
        small_style = ParagraphStyle(
            "Small", parent=styles["Normal"],
            fontSize=8, textColor=colors.grey,
        )

        elements = []

        # ── Header ──
        elements.append(Paragraph(f"🌿 {self.brand}", small_style))
        elements.append(Spacer(1, 5 * mm))
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(
            f"Yaratilgan: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            small_style,
        ))
        elements.append(Spacer(1, 10 * mm))

        # ── Stats Section ──
        if stats:
            elements.append(Paragraph("📊 Profil Statistikasi", heading_style))

            p = stats.get("profile", {})
            v = stats.get("views", {})
            eng = stats.get("engagement", {})
            ov = stats.get("overview", {})

            data = [
                ["Ko'rsatkich", "Qiymat"],
                ["Followers", f"{p.get('followers', 0):,}"],
                ["Tahlil qilingan reels", str(ov.get("total_reels_analyzed", 0))],
                ["Jami views", f"{ov.get('total_views', 0):,}"],
                ["O'rtacha views", f"{v.get('average', 0):,}"],
                ["Eng yuqori views", f"{v.get('max', 0):,}"],
                ["O'rtacha ER", f"{eng.get('average_er', 0)}%"],
                ["ER bahosi", eng.get("er_benchmark", "—")],
            ]

            table = Table(data, colWidths=[8 * cm, 8 * cm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 10 * mm))

        # ── Recommendations ──
        if recommendations:
            elements.append(Paragraph("💡 Tavsiyalar", heading_style))
            for i, rec in enumerate(recommendations, 1):
                # Remove emojis for PDF compatibility
                clean_rec = rec.encode("ascii", "ignore").decode("ascii").strip()
                if clean_rec:
                    elements.append(Paragraph(f"{i}. {clean_rec}", body_style))
            elements.append(Spacer(1, 10 * mm))

        # ── Ideas ──
        if ideas:
            elements.append(Paragraph("🎬 Kontent G'oyalari", heading_style))
            for idea in ideas[:10]:
                title_text = idea.get("title", "")
                hook_text = idea.get("hook", "")
                if title_text:
                    elements.append(Paragraph(
                        f"<b>{title_text}</b>", body_style
                    ))
                if hook_text:
                    elements.append(Paragraph(
                        f"Hook: {hook_text}", small_style
                    ))
                elements.append(Spacer(1, 3 * mm))

        # ── Footer ──
        elements.append(Spacer(1, 20 * mm))
        elements.append(Paragraph(
            f"Agro AI v2.0 | {self.brand} | {datetime.now().year}",
            small_style,
        ))

        # Build PDF
        try:
            doc.build(elements)
            logger.info(f"📄 PDF yaratildi: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"PDF yaratishda xato: {e}")
            return None

    def generate_weekly_report(
        self,
        state_data: Dict,
        history: List[Dict],
        discipline: Dict,
    ) -> Optional[str]:
        """Haftalik hisobot PDF."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm, mm
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.account_id}_weekly_{timestamp}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        title_s = ParagraphStyle("T", parent=styles["Title"], fontSize=20, spaceAfter=15)
        head_s = ParagraphStyle("H", parent=styles["Heading2"], fontSize=13, spaceAfter=8,
            textColor=colors.HexColor("#6366f1"))
        body_s = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, spaceAfter=5)
        small_s = ParagraphStyle("S", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

        elements = [
            Paragraph(f"{self.brand}", small_s),
            Spacer(1, 5*mm),
            Paragraph("Haftalik Hisobot", title_s),
            Paragraph(f"{datetime.now().strftime('%Y-%m-%d')}", small_s),
            Spacer(1, 10*mm),
        ]

        # Discipline
        elements.append(Paragraph("Intizom", head_s))
        disc_data = [
            ["Ko'rsatkich", "Qiymat"],
            ["Score", f"{discipline.get('score', 0)}/100"],
            ["Streak", f"{discipline.get('streak', 0)} kun"],
            ["Izchillik", f"{discipline.get('consistency_pct', 0)}%"],
        ]
        t = Table(disc_data, colWidths=[8*cm, 8*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#6366f1")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0,0), (-1,-1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10*mm))

        # History table
        if history:
            elements.append(Paragraph("7 Kunlik Tarix", head_s))
            hist_data = [["Sana", "Post", "Followers"]]
            for h in history[-7:]:
                posted = "Ha" if h.get("posted_today") else "Yoq"
                hist_data.append([h.get("date",""), posted, str(h.get("followers",""))])
            ht = Table(hist_data, colWidths=[5*cm, 4*cm, 5*cm])
            ht.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#10b981")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ("PADDING", (0,0), (-1,-1), 5),
            ]))
            elements.append(ht)

        elements.append(Spacer(1, 15*mm))
        elements.append(Paragraph(f"Agro AI v2.0 | {self.brand}", small_s))

        try:
            doc.build(elements)
            logger.info(f"📄 Weekly PDF: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Weekly PDF xato: {e}")
            return None
