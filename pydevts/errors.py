from loguru import logger

def catch_all_continue(func):
    """
        This is probably the most useful function I have ever written.
        It wraps any async function, and when there is an exception, it logs it and continues on like nothing ever happened.
        This works amazing for web servers. Just wrap the server handler function in this and you are good to go.
        Only requires loguru, however loguru can be switched for anything else. (Although I like it best)
        Self imports functools just in case you do not want clutter in the project.
    """
    @__import__("functools").wraps(func)
    async def _wrap(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # See this line right here? Yeah. This one:
            logger.exception(e)

            # Change it to something else to use something other than loguru.
            # Example:
            # print(e)

            # I just like loguru because it has really nice formatting

    return _wrap