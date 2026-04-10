# Hackathon Special Tracks — Full Reference

Source: https://www.notion.so/AI-Health-Hack-2026-Special-Alan-Tracks

> You have 12 hours to build something that could change how 1M+ members take care of their health.
> Pick a challenge from one of the tracks below. The best build in each track wins a special prize.

---

## Alan Play Track (gamified prevention, 600K+ members)

### 1. Living Avatars

**In one line:** AI-generated avatars that reflect your health journey: customizable, animatable, and evolving.

**Context:** Alan members earn berries and unlock static avatar accessories, all designed by hand. The bottleneck is asset creation.

**The dream:** Avatar is AI-generated from preferences (or selfie), fully customizable, visually evolves with health activity. Meditation streak makes it glow. Consistent steps put energy in posture. Seasonal collections generated on demand.

**Hard design problem:** Avatars are social objects (leaderboards, teams, boosts). AI accessories need consistency across all members while feeling fresh. Think: "spring collection" that any member can wear, not a unique hat.

**Build in 12h:**
- Selfie/style input → personalized avatar
- One health-state transformation (baseline vs after 7-day streak)
- Generate collection from single prompt ("spring collection") working across 3+ avatars
- Bonus: animation (idle loop, celebration)
- Bonus: cost/speed estimate

**Blow us away:** Avatars personal enough to become profile pictures, accessories that feel curated and collectible.

---

### 2. Mo Studios: AI-Generated Health Content

**In one line:** Pipeline that produces personalized, medically accurate, on-brand health content in minutes.

**Context:** Alan expanding into sleep, nutrition, digital detox, tobacco, stress. Each vertical needs content but production is slow.

**The dream:** Topic → ready-to-ship piece in minutes. Personalized by member profile (experience level, active challenges, streaks).

**Build in 12h:**
- Pipeline: health topic + member context + format (meditation/article/video) → content
- Mistral generates → medical accuracy check → brand voice check
- Demo: same topic, generic vs personalized for specific member
- 5 pieces for one vertical in under 5 minutes
- Bonus: actual audio meditation with adaptive pacing
- Bonus: "brand voice scorer"

**Blow us away:** Two members, same "sleep" content, genuinely different experiences.

---

### 3. Personalized Wrapped

**In one line:** Weekly/monthly health recap that tells your story. Personal, visual, shareable.

**Context:** Alan tracks steps, challenges, streaks, berries, meditation, quiz scores, team rankings. Building "weekly wrapped" for Q2.

**The dream:** Spotify Wrapped for health. AI turns data into narrative with team and league dimensions.

**Build in 12h:**
- Sample dataset: ~50 members, 3-4 companies, 4 weeks of activity
- Pipeline: activity data → personalized narrative + visual cards
- Mistral generates story (not stats — insight, humor, nudge)
- Animated cards (Instagram stories format)
- Individual + team wrap + cross-member comparison
- Bonus: monthly wrap (arc, not average)
- Bonus: predictive nudge

**Blow us away:** Members screenshot and share on company Slack.

---

### 4. Health App in a Prompt

**In one line:** Describe a health goal → AI assembles a working micro-app from phone + Alan primitives.

**Context:** Each new challenge type requires design + engineering. AI can generate functional mini-apps from prompts.

**Available primitives:**
- Camera (meal, posture, environment analysis)
- Health data (steps, sleep, heart rate from HealthKit/Google Fit)
- Screen time API
- GPS (location, distance, route)
- Calendar (meeting density, free slots)
- Time-based triggers
- Tap-to-validate ("I drank water")
- Berries (configurable reward, weighted by impact + verificability)
- Social (share, buddy, leaderboard, boost/cheer)

**Build in 12h:**
- Prompt interface → Mistral decomposes goal into micro-app
- Demo 3+ prompts: "eat more vegetables", "take stairs", "digital detox after 9pm", "track water by meeting schedule", "run 5k in 8 weeks", "manage stress during busy weeks"
- Bonus: marketplace view
- Bonus: generated app actually works

**Blow us away:** "I described my health goal and got a personal health app in 10 seconds."

---

## Alan Precision Track (longevity, blood panels + lifestyle)

### 1. Wearables + Blood → Daily Coaching ← OUR TARGET

**In one line:** Combine blood biomarkers with daily wearable signals → personalized health protocol that adapts day by day.

**The idea:** Blood check Monday → protocol. AI refines each morning based on last night's data: HRV, sleep, steps, resting HR crossed with ferritin, cortisol, vitamin D, glucose.

**Build in 12h:**
- Pipeline: blood panel results + daily wearable data → personalized daily protocol (nutrition, activity, sleep)
- Show protocol evolves over a week as new data comes in
- Bonus: flag when biomarker trend + wearable signal together suggest something neither catches alone

---

### 2. AI-Powered Medical Intake

**In one line:** Replace 200+ question static questionnaire with adaptive AI conversation.

**The idea:** Multiple AI doctors conducting conversation, go deeper only when relevant, skip what's not.

**Build in 12h:**
- Adaptive intake conversation based on prior answers
- Two profiles → two meaningfully different conversation paths
- Bonus: specialist agents (sleep, nutrition, cardio) hand off mid-conversation

---

### 3. Agentic Health Protocols

**In one line:** Turn health recommendations into actions an AI agent executes for you.

**The idea:** Blood check says low iron + fiber → agent builds grocery list, suggests recipes, books follow-up. "Open Claw for health."

**Build in 12h:**
- Health recommendations → concrete executable actions
- 2+ recommendation-to-action flows end to end
- Bonus: real API integration (calendar, grocery, appointments)
