import asyncio
import re
from urllib.parse import urlparse
import aiohttp


class Shareus:
    def __init__(self, api_key: str, base_site: str = "shareus.in"):
        self.api_key = api_key
        self.base_site = base_site
        self.base_url = f"https://api.{self.base_site}/shortLink"

        if not self.api_key:
            raise Exception("API key not provided")

    async def __fetch(self, session: aiohttp.ClientSession, params: dict) -> dict:
        async with session.get(
            self.base_url, params=params, raise_for_status=True, ssl=False
        ) as response:
            result = await response.json(content_type="text/html")
            return result

    async def convert(
        self, link: str, silently_fail: bool = False, quick_link: bool = False, **kwargs
    ) -> str:
        is_short_link = await self.is_short_link(link)

        if is_short_link:
            return link

        if quick_link:
            return await self.get_quick_link(url=link)

        params = {
            "token": self.api_key,
            "link": link,
            "format": "json",
        }
        try:
            my_conn = aiohttp.TCPConnector(limit=10)
            async with aiohttp.ClientSession(connector=my_conn) as session:
                session = session
                data = await self.__fetch(session, params)

                if data["status"] == "success":
                    return data["shortlink"]

                if silently_fail:
                    return link

                raise Exception(data["message"])

        except Exception as e:
            raise Exception(e)

    async def get_quick_link(self, url: str, **kwargs) -> str:
        quick_link = "https://api.{base_site}/directLink?token={api_key}&link={url}"
        return quick_link.format(
            base_site=self.base_site,
            api_key=self.api_key,
            url=url,
        )

    async def bulk_convert(
        self, urls: list, silently_fail: bool = True, quick_link: bool = False, **kwargs
    ) -> list:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(
                self.convert(
                    link=url, silently_fail=silently_fail, quick_link=quick_link
                )
            )
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    async def convert_from_text(
        self, text: str, silently_fail: bool = True, quick_link: bool = False
    ) -> str:
        links = await self.__extract_url(text)
        shortened_links = await self.bulk_convert(
            links, silently_fail=silently_fail, quick_link=quick_link
        )

        for i, short_link in enumerate(shortened_links):
            text = text.replace(links[i], short_link)
        return text

    async def is_short_link(self, link: str) -> bool:
        domain = urlparse(link).netloc
        return self.base_site in domain

    async def __extract_url(self, string: str) -> list:
        regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        urls = re.findall(regex, string)
        return ["".join(x) for x in urls]
