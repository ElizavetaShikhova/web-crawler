import os
import pickle
import click
from Crawler import Crawler

STATE_FILE = 'crawler_state.pkl'


def save_state(crawler):
    with open(STATE_FILE, 'wb') as f:
        pickle.dump(crawler, f)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'rb') as f:
            return pickle.load(f)
    return None


@click.group()
@click.pass_context
def cli(ctx):
    crawler = load_state()
    if not crawler:
        crawler = Crawler()
    ctx.obj = crawler


@cli.command()
@click.pass_context
def crawler_start(ctx):
    crawler = ctx.obj
    try:
        crawler.crawl()
    except Exception as exc:
        print(exc)
    save_state(crawler)


@cli.command()
@click.argument('start_url')
@click.pass_context
def crawler_set_start_url(ctx, start_url):
    try:
        ctx.obj.set_start_url(start_url)
        click.echo(f"Start URL set to: {start_url}")
        save_state(ctx.obj)
    except Exception as exc:
        print(exc)


@cli.command()
@click.argument('domain')
@click.pass_context
def crawler_set_domain(ctx, domain):
    try:
        ctx.obj.set_allowed_domain(domain)
        click.echo(f"Allowed domain set to: {domain}")
        save_state(ctx.obj)
    except Exception as exc:
        print(exc)


@cli.command()
def crawler_reset():
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    click.echo("Crawler state reset.")
