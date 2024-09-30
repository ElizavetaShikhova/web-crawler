import os
from pathlib import Path
import click

from crawler import Crawler, load_state, save_state, STATE_FILE


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

@cli.command()
@click.argument('update', type=click.BOOL)
@click.pass_context
def crawler_set_update(ctx: click.Context, update: bool) -> None:
    try:
        ctx.obj.set_update(update)
        click.echo(f"Update existing pages set to: {update}")
        save_state(ctx.obj)
    except Exception as exc:
        click.echo(exc)

@cli.command()
@click.argument('update_interval', type=click.BOOL)
@click.pass_context
def crawler_set_update_interval(ctx: click.Context, update_interaval: int) -> None:
    try:
        ctx.obj.set_update_interval(update_interaval)
        click.echo(f"Update interval set to: {update_interaval}")
        save_state(ctx.obj)
    except Exception as exc:
        click.echo(exc)
