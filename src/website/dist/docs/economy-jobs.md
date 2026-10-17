# Jobs and Earning Guide

Niko's job system lets members earn money through various simulated professions.

## Available Jobs

The ladder is the same in every server. Each rung pays more per shift and earns more XP, and each one unlocks at a career level:

| Job | Min level | Pay per shift | XP per shift |
| --- | --- | --- | --- |
| **Cashier** | 0 | 80 – 220 coins | +12 |
| **Baker** | 5 | 180 – 380 coins | +18 |
| **Shift Manager** | 15 | 320 – 620 coins | +28 |
| **Market Trader** | 30 | 450 – 1,100 coins | +42 |
| **Business Owner** | 50 | 800 – 2,200 coins | +60 |

Run `.job list` for the live table, `.job apply <id>` to move up, and `.job quit` to return to the bottom rung.

## Working

Use the `work` command to earn money:

```
.work
```

Each job has:
- **Base pay**: Fixed amount per work session
- **Cooldown**: Time before you can work again (1 hour)
- **Experience**: Work earns XP toward leveling

## Maximizing Earnings

### Tips for More Money
1. **Work consistently**: Use the daily reward and work commands
2. **Climb the job ladder**: Better jobs pay more
3. **Bank your money**: Earn interest on savings
4. **Build streaks**: Daily streaks give bonuses
5. **Buy upgrades**: Shop items can boost earnings
6. **Participate in lottery**: Small chance of big wins

### Cooldowns
- Work: 1 hour cooldown
- Daily: 24 hour cooldown
- Gambling: Varies by game

## Job Commands
- `.job` - See your current job
- `.job list` - View available jobs
- `.job apply <job id>` - Apply for a job
- `.job info <job id>` - View job details
- `.job quit` - Leave your current job
