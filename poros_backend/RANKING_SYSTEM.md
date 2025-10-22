# Poros Protocol - Proprietary Ranking System

## YOUR Competitive Advantage

The ranking system determines which agents get traffic. **This is how you make money.**

---

## 🎯 How It Works

When a client query comes in, Poros:
1. Discovers matching agents (by skill tags)
2. **Ranks them using YOUR algorithm**  ← **THIS IS THE MAGIC**
3. Calls top N agents
4. Returns aggregated results

The ranking algorithm is in [app/ranking.py](app/ranking.py)

---

## 🧠 Ranking Strategies

### 1. Performance Ranking
**Best for:** Reliability-focused users

**Weights:**
- Success rate: 60%
- Latency: 30%
- Popularity: 10%

**Use case:** Enterprise clients who need guaranteed uptime

### 2. Semantic Ranking
**Best for:** Natural language queries

**How it works:**
- Embeds user query
- Embeds agent descriptions
- Ranks by cosine similarity

**Requires:** `sentence-transformers` library (optional)

**Fallback:** Keyword matching

### 3. Revenue Ranking
**Best for:** Monetization

**Tier bonuses:**
- Enterprise tier: 100 points
- Premium: 70 points
- Pro: 40 points
- Free: 0 points

Plus small performance bonus so free agents can still compete

### 4. Hybrid Ranking (DEFAULT)
**Best for:** Production

**Combines all signals:**
- Skill match: 40%
- Performance: 25%
- Semantic: 20%
- Revenue tier: 10%
- Freshness: 5%

---

## 💰 Monetization Strategy

### How to make money:

**Option 1: Marketplace Fees**
- Free agents: 0% fee
- Pro agents: 15% of earnings
- Premium: 10% (volume discount)
- Enterprise: 5% (lowest fee, highest volume)

**Option 2: Featured Placement**
- $99/mo - Rank boost of +20 points
- $499/mo - Top 3 guaranteed for matching queries
- $1,999/mo - Exclusive category

**Option 3: Performance Tiers**
Agents pay for better infrastructure:
- Free: Shared resources, slower ranking
- Pro: Dedicated ranking, priority queue
- Enterprise: Custom ranking weights

---

## 🔧 Customization

### Change Ranking Weights

Edit `poros_backend/app/ranking.py`:

```python
class HybridRanking(RankingStrategy):
    def __init__(self):
        # Tune these weights!
        self.weights = {
            "skill_match": 0.40,    # ← Change this
            "performance": 0.25,    # ← Or this
            "semantic": 0.20,
            "revenue": 0.10,        # ← Make money here
            "freshness": 0.05
        }
```

### Add Custom Signals

Want to rank by user ratings? Location? Model quality?

Add new scoring functions:

```python
def _user_rating_score(self, agent: RegisteredAgent) -> float:
    # Get rating from agent metadata
    rating = agent.agent_card.get("metadata", {}).get("rating", 0)
    return rating * 20  # 0-5 stars → 0-100 points
```

Then add to hybrid score:

```python
total_score = (
    skill_score * 0.35 +
    performance_score * 0.25 +
    semantic_score * 0.15 +
    revenue_score * 0.10 +
    user_rating_score * 0.10 +  # NEW!
    freshness_score * 0.05
)
```

---

## 🧪 A/B Testing

Test different ranking strategies:

```python
# In orchestrator.py
from .ranking import rank_agents

# A/B test: 50% hybrid, 50% performance
import random
strategy = "hybrid" if random.random() < 0.5 else "performance"

ranked_agents = rank_agents(
    matching_agents,
    request.query,
    request.skill_tags,
    strategy=strategy  # ← Pick strategy
)
```

Track which strategy generates more revenue!

---

## 📊 Metrics to Track

Add these to your analytics:

1. **Conversion rate by ranking strategy**
   - Which strategy leads to more successful agent calls?

2. **Revenue per strategy**
   - Does revenue-based ranking actually make more money?

3. **Agent churn**
   - Are low-ranked agents leaving the platform?

4. **User satisfaction**
   - Do users prefer semantic or performance ranking?

---

## 🚀 Next Steps

### Phase 1: Current (Simple)
- ✅ Hybrid ranking with tunable weights
- ✅ Multiple strategy support
- ✅ Performance metrics tracking

### Phase 2: ML Model (1-2 weeks)
- Train ranking model on historical data
- Features: query, agent metadata, past performance
- Use LightGBM or XGBoost
- Deploy as inference endpoint

### Phase 3: Personalization (1 month)
- User-specific ranking (remember preferences)
- Collaborative filtering (users like you preferred...)
- Context-aware (time, location, device)

### Phase 4: Real-time Learning (2-3 months)
- Online learning from user clicks
- Multi-armed bandit for exploration
- RL-based ranking optimization

---

## 🔒 Keep This Secret!

**This ranking system is YOUR moat.**

Don't open-source it. Don't share the weights.

This is how you:
1. Control the marketplace
2. Favor premium agents
3. Make money

---

**Current Status:** ✅ Production-ready hybrid ranking system deployed!

Next: Build frontend → Deploy → Start making money! 💰
