from .shareus import Shareus
from .adlinkfly import Adlinkfly


class Shortzy:
    """
    A Unofficial Shortener API Wrapper for Adlinkfly Site and Alternative Sites

    :param api_key: Your API key
    :type api_key: str
    :param base_site: The site you want to use, defaults to droplink.co
    :type base_site: str (optional)
    """

    def __init__(self, api_key: str, base_site: str = "droplink.co"):
        self.api_key = api_key
        self.base_site = base_site

        if not self.api_key:
            raise Exception("API key not provided")

        if self.base_site == "shareus.in":
            self.shortener = Shareus(api_key, base_site=base_site)
        else:
            self.shortener = Adlinkfly(api_key, base_site=base_site)

    async def convert(
        self, link: str, silently_fail: bool = False, quick_link: bool = False, alias: str = "", ** kwargs
    ) -> str:
        """
        It converts a link to a short link.

        :param link: The link you want to shorten
        :type link: str

        :param alias: The alias you want to use for the link
        :type alias: str

        :param silently_fail: If this is set to True, then instead of raising an exception, it will return
        the original link, defaults to False
        :type silently_fail: bool (optional)

        :param quick_link: If you want to get a quick link, set this to True, defaults to False
        :type quick_link: bool (optional)

        :return: The shortened link is being returned.
        """
        return await self.shortener.convert(
            link=link,
            alias=alias,
            silently_fail=silently_fail,
            quick_link=quick_link,
            **kwargs,
        )

    async def shorten(self, **kwargs) -> str:
        return await self.shortener.convert(**kwargs)

    async def get_quick_link(self, link: str, alias: str = "") -> str:
        """
        It converts a link to a short link.

        :param link: The link you want to shorten
        :type link: str

        :return: The shortened link is being returned.
        """

        return await self.shortener.get_quick_link(link, alias)

    async def convert_from_text(
        self, text: str, silently_fail: bool = False, quick_link: bool = False, **kwargs
    ) -> str:
        """
        It converts all links from a text to a short link.

        :param text: The text you want to shorten links from
        :type text: str

        :param alias: The alias you want to use for the link
        :type alias: str

        :param silently_fail: If this is set to True, then instead of raising an exception, it will return
        the original link, defaults to False
        :type silently_fail: bool (optional)

        :param quick_link: If you want to get a quick link, set this to True, defaults to False
        :type quick_link: bool (optional)

        :return: The shortened link is being returned.
        """
        return await self.shortener.convert_from_text(
            text, silently_fail, quick_link, **kwargs
        )

    async def bulk_convert(self, links: list, silently_fail: bool = False, quick_link: bool = False, **kwargs) -> list:
        """
        It converts a list of links to a list of short links.

        :param links: The list of links you want to shorten
        :type links: list

        :param silently_fail: If this is set to True, then instead of raising an exception, it will return
        the original link, defaults to False
        :type silently_fail: bool (optional)

        :param quick_link: If you want to get a quick link, set this to True, defaults to False
        :type quick_link: bool (optional)

        :return: The list of shortened links is being returned.
        """
        return await self.shortener.bulk_convert(links, silently_fail=silently_fail, quick_link=quick_link, **kwargs)

    async def is_short_link(self, link: str) -> bool:
        """
        It checks if the link is a short link.

        :param link: The link you want to check
        :type link: str

        :return: True if the link is a short link, False if not.
        """
        return await self.shortener.is_short_link(link)

    @staticmethod
    def available_websites():
        available_websites = [
            "droplink.co",
            "gplinks.in",
            "tnlink.in",
            "za.gl",
            "du-link.in",
            "viplink.in",
            "shorturllink.in",
            "shareus.in",
            "All droplink.co Alternative Websites",
        ]
        return "\n".join(available_websites)
