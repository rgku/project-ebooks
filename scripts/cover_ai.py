from log import logger
import config
import cover_gen as fallback_cover


def generate_cover(niche: config.Niche, output_path: str):
    logger.info("Using PIL cover generator")
    fallback_cover.generate_cover(niche, output_path)
