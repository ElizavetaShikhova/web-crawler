import os
import pickle
from pathlib import Path
from typing import Optional

import click

from crawler import Crawler

STATE_FILE = 'crawler_state.pkl'

def save_state(crawler: Crawler) -> None:
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(crawler, f)


def load_state() -> Optional[Crawler]:
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, 'rb') as f:
            return pickle.load(f)


@click.group()
@click.pass_context
def cli(ctx) -> None:
    crawler = load_state()
    if not crawler:
        crawler = Crawler()
    ctx.obj = crawler


@cli.command()
@click.pass_context
def crawler_start(ctx: click.Context) -> None:
    crawler = ctx.obj
    try:
        crawler.crawl()
    except Exception as exc:
        click.echo(exc)
    save_state(crawler)


@cli.command()
@click.argument('start_url')
@click.pass_context
def crawler_set_start_url(ctx: click.Context, start_url: str) -> None:
    try:
        ctx.obj.set_start_url(start_url)
        click.echo(f"Start URL set to: {start_url}")
        save_state(ctx.obj)
    except Exception as exc:
        click.echo(exc)


@cli.command()
@click.argument('domain')
@click.pass_context
def crawler_set_domain(ctx: click.Context, domain: str):
    try:
        ctx.obj.set_allowed_domain(domain)
        click.echo(f"Allowed domain set to: {domain}")
        save_state(ctx.obj)
    except Exception as exc:
        click.echo(exc)


@cli.command()
def crawler_reset() -> None:
    if Path(STATE_FILE).exists():
        os.remove(STATE_FILE)
    click.echo("Crawler state reset.")
