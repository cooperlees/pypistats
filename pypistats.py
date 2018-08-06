#!/usr/bin/env python3

import aiohttp
import asyncio
import bs4
import humanfriendly
import logging
import sys
from typing import Dict, Union

import click


LOG = logging.getLogger(__name__)


def _handle_debug(
    ctx: click.core.Context,
    param: Union[click.core.Option, click.core.Parameter],
    debug: Union[bool, int, str],
) -> Union[bool, int, str]:
    """Turn on debugging if asked otherwise INFO default"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )
    return debug


def get_file_sizes(html: str) -> Dict:
    project_sizes: Dict[str, int] = {}
    soup = bs4.BeautifulSoup(html, "html.parser")
    tds = soup.findAll("td")

    for td in tds:
        if not td:
            continue

        try:
            fs_bytes = int(td.contents[0])
        except ValueError:
            package_name = td.contents[0]
            continue

        project_sizes[package_name] = fs_bytes

    return project_sizes


async def get_stats(url: str = "https://pypi.org/stats") -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            LOG.error(f"Error HTTP get to {url}: Returned {resp.status}")
            return ''


def print_bandersnatch_ini(fs_stats: Dict) -> None:
    print("[blacklist]\npackages =")
    for pkg_name, _pkg_bytes in fs_stats.items():
        if "All of PyPI" in pkg_name:
            continue
        print(f"    {pkg_name}")


def print_humanfriendly(fs_stats: Dict) -> None:
    print("Top PyPI Disk Users:")
    top_total_bytes = 0
    for pkg_name, pkg_bytes in fs_stats.items():
        if "All of PyPI" in pkg_name:
            total_pypi_size = pkg_bytes
        else:
            top_total_bytes += pkg_bytes

        print(
            f"{pkg_name}: "
            + f"{humanfriendly.format_size(humanfriendly.parse_size(str(pkg_bytes)))}"
        )

    pct = int((top_total_bytes / total_pypi_size) * 100)
    print(
        f"\nTop Packages consume " +
        f"{humanfriendly.format_size(humanfriendly.parse_size(str(top_total_bytes)))}"
    )
    print(f"- This is {pct}% of PyPI")


async def async_main(bandersnatch_ini: bool, debug: bool) -> int:
    html = await get_stats()
    if not html:
        LOG.error(f"Unable to get stat from PyPI endpoint. Exiting")
        return 1

    fs_stats = get_file_sizes(html)
    if not fs_stats:
        LOG.error(f"Didn't get valid Package size stats. Returning")
        return 69

    if bandersnatch_ini:
        print_bandersnatch_ini(fs_stats)
    else:
        print_humanfriendly(fs_stats)

    return 0


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--bandersnatch-ini",
    is_flag=True,
    show_default=True,
    help="Generate a bandersnatch compatible .ini file to stdout",
)
@click.option(
    "--debug",
    is_flag=True,
    callback=_handle_debug,
    show_default=True,
    help="Turn on debug logging",
)
@click.pass_context
def main(ctx: click.core.Context, **kwargs) -> None:
    ret_val = 0
    LOG.info(f"Starting {sys.argv[0]}")

    loop = asyncio.get_event_loop()
    try:
        ret_val = loop.run_until_complete(async_main(**kwargs))
    finally:
        loop.close()

    ctx.exit(ret_val)


if __name__ == "__main__":
    main()
