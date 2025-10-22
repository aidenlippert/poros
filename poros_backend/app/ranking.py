"""
Poros Protocol - Proprietary Agent Ranking System

This is YOUR competitive advantage - how you rank agents determines
which agents get traffic, which makes you money.

Strategies included:
1. Performance-based (success rate, latency)
2. Semantic matching (query similarity to agent description)
3. Revenue-based (premium agents rank higher)
4. Hybrid ML model (combine all signals)
"""

from typing import List, Optional, Dict, Any
from .models import RegisteredAgent
import math


# ============================================
# RANKING STRATEGIES
# ============================================

class RankingStrategy:
    """Base class for ranking strategies"""

    def score(self, agent: RegisteredAgent, query: str, skill_tags: Optional[List[str]] = None) -> float:
        """Score an agent (0-100 scale)"""
        raise NotImplementedError


class PerformanceRanking(RankingStrategy):
    """
    Rank by performance metrics.

    Best for: Reliability-focused users
    Weights: Success rate (60%), Latency (30%), Popularity (10%)
    """

    def score(self, agent: RegisteredAgent, query: str, skill_tags: Optional[List[str]] = None) -> float:
        score = 0.0

        # Success rate (0-60 points)
        score += agent.success_rate * 60

        # Latency (0-30 points, lower is better)
        if agent.avg_latency_ms > 0:
            # Convert to score: 0ms=30pts, 5000ms=0pts
            latency_score = max(0, 30 - (agent.avg_latency_ms / 5000) * 30)
            score += latency_score

        # Popularity (0-10 points)
        # Logarithmic scale: popular agents get bonus
        if agent.total_calls > 0:
            popularity_score = min(10, math.log10(agent.total_calls + 1) * 2)
            score += popularity_score

        return score


class SemanticRanking(RankingStrategy):
    """
    Rank by semantic similarity between query and agent description.

    Best for: Natural language queries
    Requires: sentence-transformers library

    TODO: Install sentence-transformers for production
    """

    def __init__(self):
        # Try to load model, fallback to simple matching
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_embeddings = True
        except ImportError:
            self.use_embeddings = False
            print("[RANKING] sentence-transformers not installed, using simple keyword matching")

    def score(self, agent: RegisteredAgent, query: str, skill_tags: Optional[List[str]] = None) -> float:
        if self.use_embeddings:
            return self._score_with_embeddings(agent, query)
        else:
            return self._score_with_keywords(agent, query)

    def _score_with_embeddings(self, agent: RegisteredAgent, query: str) -> float:
        """Use semantic embeddings (requires sentence-transformers)"""
        from sentence_transformers import util

        # Embed query and agent description
        query_emb = self.model.encode(query, convert_to_tensor=True)
        desc_emb = self.model.encode(agent.description, convert_to_tensor=True)

        # Cosine similarity (0-1)
        similarity = util.cos_sim(query_emb, desc_emb).item()

        # Convert to 0-100 scale
        return similarity * 100

    def _score_with_keywords(self, agent: RegisteredAgent, query: str) -> float:
        """Simple keyword matching fallback"""
        query_lower = query.lower()
        desc_lower = agent.description.lower()
        name_lower = agent.name.lower()

        score = 0.0

        # Check if query words appear in description
        query_words = set(query_lower.split())
        desc_words = set(desc_lower.split())
        matching_words = query_words & desc_words

        # Score based on word overlap
        if len(query_words) > 0:
            overlap_ratio = len(matching_words) / len(query_words)
            score += overlap_ratio * 70

        # Bonus if query appears in name
        if any(word in name_lower for word in query_words):
            score += 30

        return min(score, 100)


class RevenueRanking(RankingStrategy):
    """
    Rank by revenue potential.

    Best for: Monetization-focused marketplace
    Premium agents (paid tier) rank higher
    """

    def score(self, agent: RegisteredAgent, query: str, skill_tags: Optional[List[str]] = None) -> float:
        score = 0.0

        # Check agent metadata for tier
        tier = agent.agent_card.get("metadata", {}).get("tier", "free")

        # Tier bonuses
        tier_scores = {
            "enterprise": 100,
            "premium": 70,
            "pro": 40,
            "free": 0
        }

        score += tier_scores.get(tier, 0)

        # Add small performance bonus (so good free agents can compete)
        score += agent.success_rate * 10

        return score


class HybridRanking(RankingStrategy):
    """
    Hybrid ML-style ranking combining multiple signals.

    This is your PRODUCTION ranking system.
    Combine performance, semantics, revenue, and skill matching.

    Weights (customizable):
    - Skill match: 40%
    - Performance: 25%
    - Semantic: 20%
    - Revenue tier: 10%
    - Freshness: 5%
    """

    def __init__(self):
        self.performance_ranker = PerformanceRanking()
        self.semantic_ranker = SemanticRanking()
        self.revenue_ranker = RevenueRanking()

        # Weights (tune these!)
        self.weights = {
            "skill_match": 0.40,
            "performance": 0.25,
            "semantic": 0.20,
            "revenue": 0.10,
            "freshness": 0.05
        }

    def score(self, agent: RegisteredAgent, query: str, skill_tags: Optional[List[str]] = None) -> float:
        # Component scores
        skill_score = self._skill_match_score(agent, skill_tags)
        performance_score = self.performance_ranker.score(agent, query, skill_tags)
        semantic_score = self.semantic_ranker.score(agent, query, skill_tags)
        revenue_score = self.revenue_ranker.score(agent, query, skill_tags)
        freshness_score = self._freshness_score(agent)

        # Weighted combination
        total_score = (
            skill_score * self.weights["skill_match"] +
            performance_score * self.weights["performance"] +
            semantic_score * self.weights["semantic"] +
            revenue_score * self.weights["revenue"] +
            freshness_score * self.weights["freshness"]
        )

        return total_score

    def _skill_match_score(self, agent: RegisteredAgent, skill_tags: Optional[List[str]]) -> float:
        """Score based on skill tag matching"""
        if not skill_tags:
            return 50  # Neutral if no tags specified

        agent_tags = set(agent.skills_tags)
        query_tags = set(skill_tags)

        if len(query_tags) == 0:
            return 50

        # Jaccard similarity
        intersection = agent_tags & query_tags
        union = agent_tags | query_tags

        if len(union) == 0:
            return 0

        similarity = len(intersection) / len(union)
        return similarity * 100

    def _freshness_score(self, agent: RegisteredAgent) -> float:
        """Newer agents get a small boost (encourages new entrants)"""
        # TODO: Calculate days since registration
        # For now, return neutral
        return 50


# ============================================
# MAIN RANKING FUNCTION
# ============================================

def rank_agents(
    agents: List[RegisteredAgent],
    query: str,
    skill_tags: Optional[List[str]] = None,
    strategy: str = "hybrid"
) -> List[RegisteredAgent]:
    """
    Rank agents using specified strategy.

    Args:
        agents: List of registered agents
        query: User query
        skill_tags: Optional skill tags to filter/rank by
        strategy: "performance", "semantic", "revenue", or "hybrid" (default)

    Returns:
        Sorted list of agents (best first)
    """
    # Select ranking strategy
    strategies = {
        "performance": PerformanceRanking(),
        "semantic": SemanticRanking(),
        "revenue": RevenueRanking(),
        "hybrid": HybridRanking()
    }

    ranker = strategies.get(strategy, HybridRanking())

    # Score all agents
    scored_agents = []
    for agent in agents:
        score = ranker.score(agent, query, skill_tags)
        scored_agents.append((agent, score))

    # Sort by score descending
    scored_agents.sort(key=lambda x: x[1], reverse=True)

    # Return sorted agents
    return [agent for agent, score in scored_agents]
