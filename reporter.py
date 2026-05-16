"""
╔══════════════════════════════════════════════════════╗
║       Instagram Reels Analyzer — Reporter Module     ║
║       Hisobot yaratish: terminal + Excel + JSON      ║
╚══════════════════════════════════════════════════════╝
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import config
from analyzer import ReelIdea
from scraper import ProfileData, ReelData

logger = logging.getLogger("instagram_analyzer.reporter")


# ════════════════════════════════════════════════════════
# 📋 REPORTER
# ════════════════════════════════════════════════════════

class Reporter:
    """
    Tahlil natijalarini turli formatlarda chiqarish.
    """

    def __init__(self, profile: ProfileData, reels: List[ReelData], stats: Dict):
        self.profile = profile
        self.reels = reels
        self.stats = stats
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_name = f"{config.EXPORT_DIR}/{profile.username}_{self.timestamp}"

    # ─────────────────────────────────────────────────────
    # TERMINAL (Rich)
    # ─────────────────────────────────────────────────────

    def print_terminal_report(
        self,
        recommendations: List[str],
        ai_analysis: str = "",
    ) -> None:
        """Terminal'ga chiroyli hisobot chiqarish."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich import box
            from rich.text import Text

            console = Console()
            s = self.stats

            # ── Header ──
            console.print()
            console.print(
                Panel.fit(
                    f"[bold cyan]📊 Instagram Reels Tahlil Hisoboti[/bold cyan]\n"
                    f"[white]@{s['profile']['username']} • {datetime.now().strftime('%Y-%m-%d %H:%M')}[/white]",
                    border_style="cyan",
                )
            )

            # ── Profile ──
            profile_table = Table(box=box.ROUNDED, show_header=False, border_style="blue")
            profile_table.add_column("Key", style="bold yellow", width=20)
            profile_table.add_column("Value", style="white")

            p = s["profile"]
            profile_table.add_row("👤 Profil", f"@{p['username']} {'✅' if p['is_verified'] else ''}")
            profile_table.add_row("📛 Ism", p["full_name"] or "—")
            profile_table.add_row("👥 Followers", f"{p['followers']:,}")
            profile_table.add_row("➡️ Following", f"{p['following']:,}")
            profile_table.add_row("📸 Posts", f"{p['posts_count']:,}")

            console.print("\n[bold]👤 PROFIL MA'LUMOTLARI[/bold]")
            console.print(profile_table)

            # ── Overview ──
            ov = s["overview"]
            eng = s["engagement"]
            views = s["views"]

            overview_table = Table(box=box.ROUNDED, show_header=False, border_style="green")
            overview_table.add_column("Metrika", style="bold yellow", width=28)
            overview_table.add_column("Qiymat", style="white")

            overview_table.add_row("🎬 Tahlil qilingan reels", str(ov["total_reels_analyzed"]))
            overview_table.add_row("👁 Jami views", f"{ov['total_views']:,}")
            overview_table.add_row("❤️ Jami likes", f"{ov['total_likes']:,}")
            overview_table.add_row("💬 Jami comments", f"{ov['total_comments']:,}")
            overview_table.add_row("📈 O'rtacha views", f"{views['average']:,}")
            overview_table.add_row("📊 Median views", f"{views['median']:,}")
            overview_table.add_row("🔝 Eng ko'p views", f"{views['max']:,}")
            overview_table.add_row("📉 Eng kam views", f"{views['min']:,}")
            overview_table.add_row(
                "💡 O'rtacha ER",
                f"{eng['average_er']}%  {eng['er_benchmark']}",
            )

            console.print("\n[bold]📊 UMUMIY STATISTIKA[/bold]")
            console.print(overview_table)

            # ── Performance Tiers ──
            tiers = s["performance_tiers"]
            tier_table = Table(box=box.ROUNDED, border_style="magenta")
            tier_table.add_column("Daraja", style="bold")
            tier_table.add_column("Soni", justify="center")
            tier_table.add_column("Tavsif")

            tier_table.add_row(
                "🚀 Viral (3x+)", str(tiers.get("viral", {}).get("count", 0)),
                "O'rtachadan 3 barobar ko'p views"
            )
            tier_table.add_row(
                "✅ Yaxshi (1.5-3x)", str(tiers.get("good", {}).get("count", 0)),
                "O'rtachadan 1.5-3x yuqori"
            )
            tier_table.add_row(
                "📊 O'rtacha (0.5-1.5x)", str(tiers.get("average", {}).get("count", 0)),
                "O'rtacha atrofida"
            )
            tier_table.add_row(
                "❌ Past (<0.5x)", str(tiers.get("underperforming", {}).get("count", 0)),
                "O'rtachadan 2x past"
            )

            console.print("\n[bold]🏆 PERFORMANCE DARAJALARI[/bold]")
            console.print(tier_table)

            # ── Top Reels ──
            top = s["top_reels"]["by_views"]
            if top:
                top_table = Table(box=box.ROUNDED, border_style="yellow")
                top_table.add_column("#", width=3, justify="center")
                top_table.add_column("Views", justify="right", style="bold green")
                top_table.add_column("Likes", justify="right")
                top_table.add_column("ER%", justify="right", style="cyan")
                top_table.add_column("Caption", max_width=40)
                top_table.add_column("URL", max_width=35)

                for i, r in enumerate(top, 1):
                    top_table.add_row(
                        str(i),
                        f"{r['views']:,}",
                        f"{r['likes']:,}",
                        f"{r['engagement_rate']}%",
                        r["caption"][:40] or "—",
                        r["url"][-35:],
                    )

                console.print("\n[bold]🏅 TOP 3 REEL (VIEWS BO'YICHA)[/bold]")
                console.print(top_table)

            # ── Hashtags ──
            hashtags = s["content"]["top_hashtags"]
            if hashtags:
                ht_text = "  ".join(
                    f"[cyan]{h['tag']}[/cyan][dim]({h['count']})[/dim]"
                    for h in hashtags[:8]
                )
                console.print(f"\n[bold]#️⃣ TOP HASHTAGLAR:[/bold] {ht_text}")

            # ── Recommendations ──
            if recommendations:
                console.print("\n[bold]💡 TAVSIYALAR[/bold]")
                for i, rec in enumerate(recommendations, 1):
                    console.print(f"  [yellow]{i}.[/yellow] {rec}")

            # ── AI Analysis ──
            if ai_analysis and not ai_analysis.startswith("ℹ️"):
                console.print(
                    Panel(
                        ai_analysis,
                        title="[bold magenta]🤖 AI TAHLIL[/bold magenta]",
                        border_style="magenta",
                    )
                )

            console.print()

        except ImportError:
            # Rich yo'q bo'lsa oddiy print
            self._print_plain_report(recommendations, ai_analysis)

    def _print_plain_report(self, recommendations: List[str], ai_analysis: str = "") -> None:
        """Rich yo'q bo'lganda oddiy terminal chiqish."""
        s = self.stats
        p = s["profile"]
        ov = s["overview"]
        v = s["views"]
        eng = s["engagement"]

        print("\n" + "=" * 60)
        print(f"  Instagram Reels Tahlil: @{p['username']}")
        print("=" * 60)
        print(f"Followers: {p['followers']:,} | Posts: {p['posts_count']:,}")
        print(f"Tahlil qilingan reels: {ov['total_reels_analyzed']}")
        print(f"Jami views: {ov['total_views']:,}")
        print(f"O'rtacha views: {v['average']:,}")
        print(f"O'rtacha ER: {eng['average_er']}% — {eng['er_benchmark']}")
        print("\nTAVSIYALAR:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        if ai_analysis:
            print(f"\nAI TAHLIL:\n{ai_analysis}")
        print("=" * 60)

    # ─────────────────────────────────────────────────────
    # VIRAL IDEAS — TERMINAL
    # ─────────────────────────────────────────────────────

    def print_reel_ideas(self, ideas: List[ReelIdea]) -> None:
        """Terminal'ga 20 ta viral reel g'oyasini chiqarish."""
        if not ideas:
            return
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich import box

            console = Console()

            source = "🤖 AI tomonidan" if config.AI_ENABLED else "📐 Rule-based"
            console.print()
            console.print(
                Panel.fit(
                    f"[bold yellow]💡 VIRAL REEL G'OYALARI[/bold yellow]\n"
                    f"[dim]{source} yaratildi • {len(ideas)} ta g'oya[/dim]",
                    border_style="yellow",
                )
            )

            for idea in ideas:
                # Format badge color
                fmt_colors = {
                    "Educational": "cyan",
                    "Tutorial": "green",
                    "Storytelling": "magenta",
                    "POV": "blue",
                    "Trend": "red",
                    "Behind-scenes": "yellow",
                    "Engagement": "bright_white",
                }
                color = fmt_colors.get(idea.format, "white")

                idea_table = Table(
                    box=box.SIMPLE,
                    show_header=False,
                    padding=(0, 1),
                    border_style="dim",
                )
                idea_table.add_column("Key", style="bold", width=16)
                idea_table.add_column("Value", style="white", max_width=70)

                idea_table.add_row("🎣 Hook",        idea.hook)
                idea_table.add_row("🎬 Kontent",     idea.concept)
                idea_table.add_row("📝 Caption",     idea.caption[:120] + ("..." if len(idea.caption) > 120 else ""))
                idea_table.add_row("#️⃣ Hashtaglar",  " ".join(idea.hashtags[:6]))
                idea_table.add_row("🚀 Viral sabab", idea.viral_reason)
                idea_table.add_row("📈 Taxminiy ER", idea.estimated_er)

                console.print(
                    Panel(
                        idea_table,
                        title=f"[bold {color}]#{idea.number} — {idea.title}[/bold {color}]  "
                              f"[dim][{idea.format}][/dim]",
                        border_style=color,
                        padding=(0, 1),
                    )
                )

            console.print()

        except ImportError:
            self._print_plain_ideas(ideas)

    def _print_plain_ideas(self, ideas: List[ReelIdea]) -> None:
        """Rich yo'q bo'lganda oddiy chiqish."""
        print("\n" + "=" * 60)
        print(f"  💡 VIRAL REEL G'OYALARI ({len(ideas)} ta)")
        print("=" * 60)
        for idea in ideas:
            print(f"\n#{idea.number} [{idea.format}] — {idea.title}")
            print(f"  Hook:    {idea.hook}")
            print(f"  Kontent: {idea.concept[:100]}")
            print(f"  ER:      {idea.estimated_er}")
        print("=" * 60)

    # ─────────────────────────────────────────────────────
    # JSON EXPORT
    # ─────────────────────────────────────────────────────

    def export_json(self, ideas: List[ReelIdea] = None) -> str:
        """JSON formatda saqlash."""
        path = f"{self.base_name}.json"
        data = {
            "generated_at": datetime.now().isoformat(),
            "stats": self.stats,
            "reels": [r.to_dict() for r in self.reels],
        }
        if ideas:
            data["reel_ideas"] = [i.to_dict() for i in ideas]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"📄 JSON saqlandi: {path}")
        return path

    # ─────────────────────────────────────────────────────
    # EXCEL EXPORT
    # ─────────────────────────────────────────────────────

    def export_excel(self, ideas: List[ReelIdea] = None) -> str:
        """Excel formatda saqlash."""
        try:
            import pandas as pd

            path = f"{self.base_name}.xlsx"

            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                # Sheet 1: Reels data
                reels_data = [r.to_dict() for r in self.reels]
                if reels_data:
                    df_reels = pd.DataFrame(reels_data)
                    # Sort by views
                    df_reels = df_reels.sort_values("views", ascending=False)
                    df_reels.to_excel(writer, sheet_name="Reels", index=False)

                    # Column widths
                    ws = writer.sheets["Reels"]
                    for col in ws.columns:
                        max_len = max(len(str(cell.value or "")) for cell in col)
                        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)

                # Sheet 2: Summary stats
                s = self.stats
                summary_rows = [
                    ["PROFIL", ""],
                    ["Username", f"@{s['profile']['username']}"],
                    ["Full Name", s["profile"]["full_name"]],
                    ["Followers", s["profile"]["followers"]],
                    ["Following", s["profile"]["following"]],
                    ["Posts", s["profile"]["posts_count"]],
                    ["", ""],
                    ["STATISTIKA", ""],
                    ["Tahlil qilingan reels", s["overview"]["total_reels_analyzed"]],
                    ["Jami views", s["overview"]["total_views"]],
                    ["Jami likes", s["overview"]["total_likes"]],
                    ["Jami comments", s["overview"]["total_comments"]],
                    ["O'rtacha views", s["views"]["average"]],
                    ["Median views", s["views"]["median"]],
                    ["Max views", s["views"]["max"]],
                    ["Min views", s["views"]["min"]],
                    ["O'rtacha ER%", s["engagement"]["average_er"]],
                    ["ER bahosi", s["engagement"]["er_benchmark"]],
                    ["", ""],
                    ["PERFORMANCE DARAJALARI", ""],
                    ["Viral reels", s["performance_tiers"].get("viral", {}).get("count", 0)],
                    ["Yaxshi reels", s["performance_tiers"].get("good", {}).get("count", 0)],
                    ["O'rtacha reels", s["performance_tiers"].get("average", {}).get("count", 0)],
                    ["Past reels", s["performance_tiers"].get("underperforming", {}).get("count", 0)],
                ]

                df_summary = pd.DataFrame(summary_rows, columns=["Ko'rsatkich", "Qiymat"])
                df_summary.to_excel(writer, sheet_name="Xulosa", index=False)

                ws2 = writer.sheets["Xulosa"]
                ws2.column_dimensions["A"].width = 30
                ws2.column_dimensions["B"].width = 25

                # Sheet 3: Top hashtags
                hashtags = s["content"]["top_hashtags"]
                if hashtags:
                    df_ht = pd.DataFrame(hashtags)
                    df_ht.to_excel(writer, sheet_name="Hashtaglar", index=False)

                # Sheet 4: Viral reel ideas
                if ideas:
                    df_ideas = pd.DataFrame([i.to_dict() for i in ideas])
                    # Rename columns to Uzbek
                    df_ideas.columns = [
                        "№", "Sarlavha", "Hook (birinchi 3 soniya)",
                        "Kontent g'oyasi", "Caption", "Hashtaglar",
                        "Format", "Viral sabab", "Taxminiy ER",
                    ]
                    df_ideas.to_excel(writer, sheet_name="Reel G'oyalar", index=False)

                    ws4 = writer.sheets["Reel G'oyalar"]
                    col_widths = [5, 30, 50, 60, 60, 40, 18, 50, 15]
                    for i, width in enumerate(col_widths, 1):
                        col_letter = ws4.cell(row=1, column=i).column_letter
                        ws4.column_dimensions[col_letter].width = width

                    # Wrap text for long columns
                    from openpyxl.styles import Alignment
                    for row in ws4.iter_rows(min_row=2):
                        for cell in row:
                            cell.alignment = Alignment(wrap_text=True, vertical="top")

            logger.info(f"📊 Excel saqlandi: {path}")
            return path

        except ImportError:
            logger.warning("⚠️ pandas/openpyxl yo'q — Excel eksport o'tkazib yuborildi")
            return ""

    # ─────────────────────────────────────────────────────
    # FULL REPORT
    # ─────────────────────────────────────────────────────

    def save_all(self, recommendations: List[str], ai_analysis: str = "", ideas: List[ReelIdea] = None) -> Dict[str, str]:
        """Barcha formatlarni saqlash."""
        paths = {}

        json_path = self.export_json(ideas=ideas)
        if json_path:
            paths["json"] = json_path

        excel_path = self.export_excel(ideas=ideas)
        if excel_path:
            paths["excel"] = excel_path

        return paths
