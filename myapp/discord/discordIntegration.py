from ..discord.report_notification import notify
from ..discord.user_discord import save_user_discord, get_user_discord, delete_user_discord


def saveUserDiscord(params):
    """
    Saves user's discord account data into database.
    Returns:
        400 Bad Request if the user is not logged in  
        
        204 No Content on success  

        500 Internal Server Error
    """
     
    return save_user_discord(params)


def getUserDiscord(userID: str):
    """
    Selects discord account data for a specific user id.

    Returns: 
        200 OK when data is successfully retrieved

        204 No Content when no discord account exists on the user id

        404 Not Found when no account exists with given user id

        500 Internal Server Error
    """

    return get_user_discord(userID)

def deleteUserDiscord(userID: str):
    """
    Deletes discord account for a specific user id.

    Returns:
        204 No Content on succes

        404 Not Found when no user account with the user id exists

        500 Internal Server Error
    """

    return delete_user_discord(userID)



def notify_discord_on_report(reportID: str, isDecision: bool):
    """
    Tags drivers on discord involved in the report.

    Returns:
        204 No Content or 500 Internal Server Error
    """

    return notify(reportID, isDecision)

    





