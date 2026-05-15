import sys
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from log import logger
import analytics
import config
import content_gen
import cover_ai
import epub_gen
import notifier
import pdf_gen
import publisher
import state


def generate_market(market: dict, st: dict) -> tuple[bool, dict]:
    name = market["name"]
    niches = market["niches"]
    niche_id = state.pick_next_niche(name, [n.id for n in niches])
    niche = next(n for n in niches if n.id == niche_id)

    logger.info(f"[{name}] Generating: {niche.title} (id={niche_id})")

    content_dir = Path("content")
    content_dir.mkdir(exist_ok=True)
    md_path = content_dir / f"{niche.id}.md"

    content_md = content_gen.generate_content(niche)
    md_path.write_text(content_md, encoding="utf-8")
    logger.info(f"[{name}] Content written ({len(content_md)} chars)")
    analytics.track_generated(name, niche.id, niche.title)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    cover_path = str(output_dir / f"{niche.id}_cover.png")
    cover_ai.generate_cover(niche, cover_path)
    logger.info(f"[{name}] Cover generated")

    pdf_path = str(output_dir / f"{niche.id}.pdf")
    pdf_gen.generate_pdf(niche, content_md, cover_path, pdf_path)
    logger.info(f"[{name}] PDF generated")

    epub_path = str(output_dir / f"{niche.id}.epub")
    epub_gen.generate_epub(niche, content_md, cover_path, epub_path)
    logger.info(f"[{name}] EPUB generated")

    price = market["price"]
    currency = market["currency"]
    desc = content_gen.generate_description(niche)
    pub_ok = publisher.publish(name, pdf_path, niche.title, price, currency, description=desc, niche_title=niche.title)

    if pub_ok:
        state.mark_generated(name, niche.id)
        st[f"{name}_last_success"] = datetime.now().isoformat()
        analytics.track_published(name, niche.id, niche.title, price, currency)
        notifier.send_notification("Ebook Published", f"{niche.title} ({price/100:.2f} {currency.upper()})", True)
        logger.info(f"[{name}] Done: {niche.id}")
        return True, st

    notifier.send_notification("Ebook Skipped", f"{niche.title} - publish not configured", False)
    logger.warning(f"[{name}] Skipped (publish not configured)")
    return False, st


def main():
    os.chdir(Path(__file__).resolve().parent.parent)

    st = state.read_state()
    if not state.check_48h_elapsed(st):
        last = st.get("last_generated", "?")
        logger.info(f"Skip: less than 48h since last generation ({last})")
        return

    any_ok = False
    for market in config.MARKETS:
        try:
            ok, st = generate_market(market, st)
            any_ok = any_ok or ok
        except Exception as e:
            logger.error(f"[{market['name']}] {e}")
            import traceback
            traceback.print_exc()
            notifier.send_notification(f"Ebook Error [{market['name']}]", str(e), False)

    if any_ok:
        st["last_generated"] = datetime.now().isoformat()
        state.save_state(st)
        logger.info("All done.")
    else:
        logger.warning("Nothing published. State unchanged.")


if __name__ == "__main__":
    main()
