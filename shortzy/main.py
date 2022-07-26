import asyncio
import json
import re
import aiohttp
from urllib.parse import urlparse

class Shortzy:
    """
    A Unofficial Wrapper for Adlinkfly Site and Alternative Sites
    
    :param api_key: Your API key
    :type api_key: str
    :param base_site: The site you want to use, defaults to droplink.co
    :type base_site: str (optional)
    """
    def __init__(self, api_key:str, base_site:str='droplink.co'):
        self.__api_key = api_key
        self.__base_site = base_site
        self.__base_url = f"https://{self.__base_site}/api"

        if not self.__api_key:
            raise Exception("API key not provided")

    async def __fetch(self, session:aiohttp.ClientSession, params:dict) -> dict:
        """
        It takes a URL, a session, and a dictionary of parameters, and returns a JSON object
        
        :param url: The URL of the API endpoint we're requesting
        :param session: the aiohttp session object
        :param params: The parameters to pass to the API
        :return: A list of dictionaries.
        """
        async with session.get(self.__base_url, params=params, raise_for_status=True, ssl=False) as response:
            result = await response.json() 
            return result

    async def convert(
        self, 
        link:str, 
        alias:str='',
        silently_fail:bool = False, 
        quick_link:bool = False,) -> str:
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

        is_droplink_link = await self.is_droplink_link(link)

        if not is_droplink_link:

            if quick_link:
                return await self.get_quick_link(url=link)

            else:  
                params = {
                    'api': self.__api_key,
                    'url': link,
                    'alias': alias
                        }
                try:
                    my_conn = aiohttp.TCPConnector(limit=10)
                    async with aiohttp.ClientSession(connector=my_conn) as session:
                        session = session     
                        data = await self.__fetch(session, params)

                        if data["status"] == "success":
                            return data['shortenedUrl']
                        else:
                            print(data['message'])
                            return await self.__error_handler(url=link, silently_fail=silently_fail, exception=Exception)

                except Exception as e:
                    print(e)
                    return await self.__error_handler(url=link, silently_fail=silently_fail, exception=Exception)

        else: return link

    async def get_quick_link(self, url:str, **kwargs) -> str:
        """
        It returns the quick link for a given link
        
        :param urls: A list of urls to convert
        :alias: The alias to use for the link
        :return: The converted links.
        """
        link = f"https://{self.__base_site}/st?api={self.__api_key}&url={url}"
        return link


    async def bulk_convert(self, urls:list, silently_fail:bool=True, quick_link:bool=False, **kwargs) -> list:
        """
        It converts a list of URLs to a list of shortened URLs.
        
        :param urls: A list of urls to convert
        :type urls: list
        :param silently_fail: If True, the function will return the given link instead of raising an exception, only if the function raise an exception,
        defaults to True
        :return: A list of the converted links.
        """

        tasks = []
        for url in urls:
            task = asyncio.ensure_future(self.convert(
                link=url, 
                silently_fail=silently_fail, 
                quick_link=quick_link))
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)


    async def convert_from_text(self, text:str, silently_fail:bool=True, quick_link:bool=False) -> str:
        """
        It takes a string, finds all the links in it, converts them, and then replaces the original links
        with the converted ones
        
        :param text: The text to be converted
        :type text: str
        :param silently_fail: If True, the function will return the given link instead of raising an exception, only if the function raise an exception,
        defaults to True
        :return: A text of converted links
        """
        links = await self.__extract_url(text)
        converted_links = await self.bulk_convert(links, silently_fail=silently_fail, quick_link=quick_link)

        for i, droplink_link in enumerate(converted_links):
            text = text.replace(links[i], droplink_link)
        return text

    @staticmethod
    async def is_droplink_link(link:str) -> bool:
        """
        It checks if the link is a valid mdisk link.
        
        :param link: The link to the file
        :type link: str
        :return: True if the link is a valid mdisk link, False otherwise
        """
        domain = urlparse(link).netloc
        if 'droplink.me' in domain:
            return True
        return False

    async def __error_handler(self, url:str, silently_fail:bool, exception=Exception, message="Some error occurred during converting: %s"):
        """
        If the URL is valid, return it. If it's not, return it or raise an exception, depending on the value
        of the `silently_fail` parameter
        
        :param url: The URL to be validated
        :type url: str
        :param silently_fail: If True, then if the URL is not valid, return the original URL. If False,
        raise an exception
        :type silently_fail: bool
        :param exception: The exception to raise if the URL is not valid
        :return: The url is being returned.
        """
        if silently_fail:
            return url
        else:
            raise exception(message % url)

    async def __extract_url(self, string:str) -> list:
        regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        urls = re.findall(regex, string)
        return ["".join(x) for x in urls]
    