# Bot per WoWs Italia
Scritto in Python

## TODO

0. Trust user nickname
Best way is using OAuth to authenticate the user, then saving the user's Discord ID with the user's in-game ID in the DB to avoid problems when the bot checks users' nickname (if a user changed his in-game nickname). The bot checks the user in-game nickname by its nickname (`member.display_nick`) and not the in-game ID.

1. Check user nickname
When a user join in the server, the bot sends a private message to the user asking him to change his nickname with the in-game nickname (how to trust user nickname: `0.`). If not, the guest won't be authenticated. An authenticated user has access to more channels.

2. Tag control
With a specific command triggered by a moderator, it checks if the authenticated users has the correct clan tag.
It's already implemented; need to fix it, add the feature "remove representative tag if the member changes the clan".

3. Representations
An authenticated user can ask to be the representative of his clan. Each clan can't have more than 2 representatives. It's triggered by a command and the bot has to check if the clan has already the representative.
If it's available space, the bot has to update the DB.
It needs a reverse command (remove representative). This command can be triggered by moderators.

6. CheckRole
A function to check if a user has a role. Hierarchy of the roles?

## DB
After reading the TODO paragraph, the missing data in the database are:
- a collection for authenticated user (?)
- a collection for the mapVote session
- a config file with mapVote maps, type of game (Best of ?), who can trigger the command
- a collection for the pick&ban session
- a config file with pick&ban available ships (or download it from the wows API), type of game (Best of ?), who can trigger the command