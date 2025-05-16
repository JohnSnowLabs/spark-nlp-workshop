## Output Format

The output consists of a JSON object with the following structure:

### Example 1 Multiple Page PDF

```json
{
    "items": [
        {
            "text": "We Start With Good\nBecause all businesses should\nbe doing something good .",
            "pagenum": 1
        },
        {
            "text": "Last Wednesday\nWe had a good\nTeam building .",
            "pagenum": 2
        }
    ]
}
```

### Example 2 Single Page PDF

```json
{
    "items": [
        {
            "text": "I live in Lviv .\nEveryday I go\nto work by\nAlso I would\nlike to visit Mars .",
            "pagenum": 1
        }
    ]
}
```

### Example 3 Image File

```json
{
    "items": [
        {
            "text": "hello ,\nSimply Noted has developed\nincredible proprietary robotic\ntechnology to write your message\nand envelopes with a genuine\nreal , Penn . It is completely\nindistinguishable from a humans\nhandwriting .\nTry us today !\nsimply \" Noted"
        }
    ]
}
```