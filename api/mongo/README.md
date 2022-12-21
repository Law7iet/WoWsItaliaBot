# MongoDB Api
A simple version of MongoDB api for WoWsItalia.
[Documentation](https://www.mongodb.com/languages/python).

## Database `WoWsItaliaDB`

### Collection `clans`
```json lines
{
  $jsonSchema: {
    title: 'Clan\'s schema',
    description: 'Clan\'s data',
    bsonType: 'object',
    required: [
      '_id',
      'id',
      'name',
      'tag'
    ],
    additionalProperties: false,
    properties: {
      _id: {
        description: 'Mongo\'s identifier',
        bsonType: 'objectId'
      },
      id: {
        description: 'Clan\'s identifier',
        bsonType: 'string'
      },
      name: {
        description: 'Clan\'s name',
        bsonType: 'string'
      },
      tag: {
        description: 'Clan\'s tag',
        bsonType: 'string'
      },
      representations: {
        description: 'Discord\'s identifiers of the clan\'s representations',
        bsonType: 'array',
        minItems: 0,
        maxItems: 2,
        items: {
          bsonType: 'string'
        }
      }
    }
  }
}
```

### Collection `rank`
```json lines
{
  $jsonSchema: {
    title: 'Clan\'s Rank',
    description: 'The clan\'s rank of the clan battle',
    bsonType: 'object',
    required: [
      '_id',
      'clan',
      'season',
      'day',
      'date',
      'squad',
      'battle',
      'winrate',
      'league',
      'division',
      'score',
      'raw'
    ],
    additionalProperties: false,
    properties: {
      _id: {
        description: 'The clan\'s rank identifier',
        bsonType: 'objectId'
      },
      clan: {
        description: 'The clan\'s identifier',
        bsonType: 'string'
      },
      season: {
        description: 'The season of the clan battle',
        bsonType: 'int'
      },
      day: {
        description: 'The progressive day of the clan battle',
        bsonType: 'int'
      },
      date: {
        description: 'The date of the clan battle',
        bsonType: 'string'
      },
      squad: {
        description: 'It states if the squad is alpha',
        bsonType: 'bool'
      },
      battle: {
        description: 'The number of the battles played',
        bsonType: 'int',
        minimum: 0
      },
      winrate: {
        description: 'The win rate of the alpha team',
        bsonType: 'double',
        minimum: 0,
        maximum: 100
      },
      league: {
        description: 'The league of the alpha team',
        bsonType: 'string'
      },
      division: {
        description: 'The division of the alpha team',
        bsonType: 'int',
        minimum: 1,
        maximum: 3
      },
      score: {
        description: 'The score of the alpha team',
        bsonType: 'int',
        minimum: 0,
        maximum: 100
      },
      raw: {
        description: 'The clan global rank',
        bsonType: 'double'
      },
      promotion: {
        description: 'The promotion battle result',
        bsonType: 'array',
        minimum: 0,
        maximum: 5,
        items: {
          bsonType: 'bool'
        }
      }
    }
  }
}
```

### Collection `players`
```json lines
{
  $jsonSchema: {
    title: 'Player\'s schema',
    description: 'Player\'s personal data',
    bsonType: 'object',
    required: [
      '_id',
      'discord',
      'wows'
    ],
    properties: {
      _id: {
        description: 'Mongo\'s identifier',
        bsonType: 'objectId'
      },
      discord: {
        description: 'Discord\'s identifier',
        bsonType: 'string'
      },
      wows: {
        description: 'WoWs\' identifier',
        bsonType: 'string'
      },
      token: {
        description: 'WoWs\' token',
        bsonType: 'string'
      },
      expire: {
        description: 'Expiration date of WoWs\' token',
        bsonType: 'string'
      }
    }
  }
}
```
