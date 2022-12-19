# MongoDB Api
A simple version of MongoDB api for WoWsItalia.
[Documentation](https://www.mongodb.com/languages/python).

## Database `WoWsItaliaDB`

### Collection `clans`
```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "$id": "schemas/clans/detail",
  "title": "Clan Data",
  "description": "This document records the details of a clan",
  "type": "object",
  "properties": {
    "_id": {
      "description": "A unique identifier for MongoDB (ObjectId)",
      "type": "string"
    },
    "id": {
      "description": "The WoWs' identifier of the clan",
      "type": "number"
    },
    "name": {
      "description": "The name of the clan",
      "type": "string"
    },
    "tag": {
      "description": "The tag of the clan",
      "type": "string",
      "maxLength": 5
    },
    "representation": {
      "description": "The Discord identifiers of the clan's representations",
      "type": "array",
      "minItems": 0,
      "maxItems": 2,
      "items": {
        "type": "number"
      }
    },
    "rank": {
      "description": "The clan battle's data of the clan",
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "season": {
            "description": "The season of clan battle",
            "type": "number"
          },
          "score": {
            "description": "The scores obtained during the specific season of clan battle",
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "date": {
                  "description": "The score of the clan in the end of the day",
                  "type": "string",
                  "format": "date"
                },
                "alpha": {
                  "description": "The score of the alpha team",
                  "$ref": "#/$defs/clan-battle-team"
                },
                "bravo": {
                  "description": "The score of the alpha team",
                  "$ref": "#/$defs/clan-battle-team"
                }
              },
              "required": ["date", "alpha", "bravo"]
            }
          }
        },
        "required": ["season", "score"]
      }
    }
  },
  "required": ["_id", "id", "name", "tag"],
  "$defs": {
    "clan-battle-team": {
      "type": "object",
      "properties": {
        "battle": {
          "description": "The number of the battles played",
          "type": "number",
          "minimum": 0
        }, 
        "win rate": {
          "description": "The win rate of the alpha team",
          "type": "number",
          "minimum": 0, 
          "maximum": 100
        },
        "league": {
          "description": "The league of the alpha team",
          "type": "string"
        },
        "division": {
          "description": "The division of the alpha team",
          "type": "number",
          "minimum": 1,
          "maximum": 3
        },
        "score": {
          "description": "The score of the alpha team",
          "type": "number",
          "minimum": 0,
          "maximum": 100
        },
        "promotion": {
          "description": "The promotion battle result",
          "type": "array",
          "minimum": 0,
          "maximum": 5,
          "items": {
            "type": "boolean"
          }
        }
      }
    }
  }
}
```

### Collection `players`
```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "$id": "schemas/players/detail",
  "title": "Player Data",
  "description": "This document records the details of a player",
  "type": "object",
  "properties": {
    "_id": {
      "description": "A unique identifier for MongoDB (ObjectId)",
      "type": "string"
    },
    "discord": {
      "description": "The Discord's identifier of the player",
      "type": "number"
    },
    "wows": {
      "description": "The WoWs' identifier of the player",
      "type": "number"
    },
    "token": {
      "description": "The WoWs' token of the player",
      "type": "string"
    },
    "expire": {
      "description": "The expiration day of the WoWs' token in UNIX time",
      "type": "number"
    }
  },
  "required": ["_id", "id", "discord", "wows"]
}
```

