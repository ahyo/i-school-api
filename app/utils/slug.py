import re
from typing import Callable
from sqlalchemy.orm import Session


def buat_slug(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-") or "konten"


def slug_unik_generator(
    session: Session,
    base_slug: str,
    exists_func: Callable[[Session, str], bool],
) -> str:
    slug = base_slug
    counter = 1
    while exists_func(session, slug):
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
