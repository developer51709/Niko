# Poll System Guide

Niko's poll system lets you create polls for server decisions and discussions.

## Creating Polls

### Basic Poll
Create a simple poll:

```
.poll create <question>
```

### Poll with Options
Create a poll with custom options:

```
.poll create <question> | <option 1> | <option 2> | <option 3>
```

Example:
```
.poll create "What should our next community event be?" | "Game Night" | "Movie Watch" | "Trivia Contest"
```

## Voting

Members vote by clicking the buttons on the poll message — vote counts update live on the poll card.

## Poll Management

### End a Poll Early
```
.poll end <message id>
```

### View Poll Results
```
.poll results <message id>
```

## Poll Features

### Vote Tracking
- Each user can only vote once per poll
- Vote counts are tracked in real-time
- Results show percentage breakdowns

## Poll Commands

| Command | Description |
|---------|-------------|
| `poll create` | Create a new poll |
| `poll end` | End a poll early |
| `poll results` | View poll results |

## Tips

1. **Keep it simple**: Clear questions get better responses
2. **Use appropriate options**: Cover the main possibilities
3. **Set reasonable durations**: Give enough time but not too much
4. **Follow up**: Share results and act on feedback
5. **Use for decisions**: Polls work great for community choices
