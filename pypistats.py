#!/usr/bin/env python3

import aiohttp
import asyncio
import humanfriendly
import logging
import sys
from typing import Dict, List, Tuple, Union

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


async def get_stats(url: str = "https://pypi.org/stats", debug: bool = False) -> Dict:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            LOG.error(f"Error HTTP GET to {url}: Returned {resp.status}")
            if debug:
                output = await resp.text()
                LOG.debug(f"{output}")
            return {}


def print_bandersnatch_ini(fs_stats: List[Tuple[str, Dict]]) -> None:
    print("[plugins]\n    enabled = blacklist_project\n")
    print("[blacklist]")
    print("packages =")
    for pkg_name, _pkg_data in fs_stats:
        print(f"    {pkg_name}")


def print_humanfriendly(fs_stats: List[Tuple[str, Dict]], total_pypi_size: int) -> None:
    print("Top PyPI Disk Users:")
    top_total_bytes = 0
    for pkg_name, pkg_data in fs_stats:
        top_total_bytes += pkg_data["size"]

        hfs = humanfriendly.format_size(humanfriendly.parse_size(str(pkg_data["size"])))
        print(f"{pkg_name}: {hfs}")

    pct = int((top_total_bytes / total_pypi_size) * 100)
    ttb = humanfriendly.format_size(humanfriendly.parse_size(str(top_total_bytes)))
    print(f"\nTop Packages consume {ttb}\n- This is {pct}% of PyPI")


async def async_main(bandersnatch_ini: bool, debug: bool) -> int:
    stats_json = await get_stats(debug=debug)
    if not stats_json:
        LOG.error(f"Unable to get stats from PyPI endpoint. Exiting")
        return 69

    import json

    sorted_packages = sorted(
        stats_json["top_packages"].items(), key=lambda x: x[1]["size"], reverse=True
    )

    if bandersnatch_ini:
        print_bandersnatch_ini(sorted_packages)
    else:
        print_humanfriendly(sorted_packages, stats_json["total_packages_size"])

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
