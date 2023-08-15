from ..discord.report_notification import notify
from ..discord.user_discord import save_user_discord


def saveUserDiscord(params):
    """
    Saves user's discord account data into database.
    Returns:
        400 Bad Request if the user is not logged in  
        
        204 No Content on success  

        500 Internal Server Error
    """
     
    return save_user_discord(params)


def notify_discord_on_report(reportID: str, isDecision: bool):
    """
    Tags drivers on discord involved in the report.

    Returns:
        204 No Content or 500 Internal Server Error
    """

    return notify(reportID, isDecision)

    





