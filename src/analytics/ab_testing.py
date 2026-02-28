"""
A/B Testing Engine — Automated split testing for Instagram content.

Implements data-driven content optimization by testing variations:
  - Hook styles (educational vs emotional vs curiosity)
  - CTA types (saves vs comments vs shares)
  - Caption lengths (short punchy vs long detailed)
  - Posting times (morning vs afternoon vs evening)
  - Visual styles (dark vs bright vs gradient)

Each test generates a hypothesis, creates variants, tracks results,
and auto-selects winners to continuously improve content strategy.
"""
import json
import logging
import hashlib
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

from src.config.settings import SETTINGS

logger = logging.getLogger(__name__)


class TestVariable(Enum):
    """What we're testing."""
    HOOK_STYLE = "hook_style"
    CTA_TYPE = "cta_type"
    CAPTION_LENGTH = "caption_length"
    POSTING_TIME = "posting_time"
    PSYCHOLOGY_TRIGGER = "psychology_trigger"
    CONTENT_FORMAT = "content_format"
    HASHTAG_STRATEGY = "hashtag_strategy"
    VISUAL_STYLE = "visual_style"


class TestStatus(Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    WINNER_SELECTED = "winner_selected"


@dataclass
class ABVariant:
    """A single variant in an A/B test."""
    variant_id: str
    name: str           # "Variant A" or "Variant B"
    content: Dict       # The actual content (hook, caption, cta, etc.)
    style: str          # Description of approach
    metrics: Dict = field(default_factory=lambda: {
        "impressions": 0,
        "likes": 0,
        "comments": 0,
        "saves": 0,
        "shares": 0,
        "engagement_rate": 0.0,
        "reach": 0,
    })


@dataclass
class ABTest:
    """An A/B test experiment."""
    test_id: str
    hypothesis: str
    variable: TestVariable
    topic: str
    variant_a: ABVariant
    variant_b: ABVariant
    status: TestStatus
    created_at: str
    winner: Optional[str] = None           # "a" or "b" or None
    confidence: float = 0.0
    learnings: str = ""
    min_sample_size: int = 100


class ABTestingEngine:
    """
    Automated A/B testing system for continuous content optimization.
    
    Tests are designed, executed, and analyzed automatically.
    Winning strategies are fed back into the content pipeline.
    """

    def __init__(self):
        self.active_tests: Dict[str, ABTest] = {}
        self.completed_tests: List[ABTest] = []
        self.learnings_db: List[Dict] = []  # Accumulated learnings
        self.storage_path = Path(SETTINGS.CAMPAIGN_STORAGE_PATH) / "ab_tests"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Pre-defined test templates
        self.test_templates = {
            TestVariable.HOOK_STYLE: {
                "hypothesis": "Curiosity-gap hooks drive more saves than direct-value hooks",
                "variant_a_style": "Direct value statement",
                "variant_b_style": "Curiosity gap / open loop",
                "primary_metric": "saves",
                "secondary_metric": "engagement_rate",
            },
            TestVariable.CTA_TYPE: {
                "hypothesis": "Question CTAs drive more comments than directive CTAs",
                "variant_a_style": "Directive CTA (Save this, Follow for more)",
                "variant_b_style": "Question CTA (What do you think? Comment below)",
                "primary_metric": "comments",
                "secondary_metric": "engagement_rate",
            },
            TestVariable.CAPTION_LENGTH: {
                "hypothesis": "Short captions (<100 words) get more reach than long ones",
                "variant_a_style": "Short & punchy (<100 words)",
                "variant_b_style": "Long & detailed (200+ words)",
                "primary_metric": "reach",
                "secondary_metric": "saves",
            },
            TestVariable.PSYCHOLOGY_TRIGGER: {
                "hypothesis": "Scarcity triggers drive more immediate action than social proof",
                "variant_a_style": "Social proof approach",
                "variant_b_style": "Scarcity/urgency approach",
                "primary_metric": "engagement_rate",
                "secondary_metric": "shares",
            },
            TestVariable.CONTENT_FORMAT: {
                "hypothesis": "Carousels get more saves, reels get more reach",
                "variant_a_style": "Carousel format",
                "variant_b_style": "Reel format",
                "primary_metric": "saves",
                "secondary_metric": "reach",
            },
        }

    def create_test(self, topic: str,
                     variable: TestVariable = None,
                     variant_a_content: Dict = None,
                     variant_b_content: Dict = None) -> ABTest:
        """
        Create a new A/B test for a topic.
        Can auto-generate variants or use provided content.
        """
        if variable is None:
            variable = self._select_test_variable()

        template = self.test_templates.get(variable, {})
        test_id = f"ab_{hashlib.md5(f'{topic}_{variable.value}_{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}"

        # Create variants
        variant_a = ABVariant(
            variant_id=f"{test_id}_a",
            name="Variant A",
            content=variant_a_content or {"placeholder": True},
            style=template.get("variant_a_style", "Control"),
        )

        variant_b = ABVariant(
            variant_id=f"{test_id}_b",
            name="Variant B",
            content=variant_b_content or {"placeholder": True},
            style=template.get("variant_b_style", "Challenger"),
        )

        test = ABTest(
            test_id=test_id,
            hypothesis=template.get("hypothesis", f"Testing {variable.value} for {topic}"),
            variable=variable,
            topic=topic,
            variant_a=variant_a,
            variant_b=variant_b,
            status=TestStatus.PLANNED,
            created_at=datetime.now().isoformat(),
            min_sample_size=SETTINGS.AB_TEST_MIN_SAMPLE_SIZE,
        )

        self.active_tests[test_id] = test
        self._save_test(test)

        logger.info(f"🔬 A/B test created: {test_id} | Variable: {variable.value} | "
                     f"Hypothesis: {test.hypothesis[:60]}...")
        return test

    def record_metrics(self, test_id: str, variant: str, metrics: Dict):
        """Record engagement metrics for a variant."""
        test = self.active_tests.get(test_id)
        if not test:
            logger.warning(f"⚠️ Test {test_id} not found")
            return

        target = test.variant_a if variant == "a" else test.variant_b

        for key, value in metrics.items():
            if key in target.metrics:
                target.metrics[key] = value

        # Calculate engagement rate
        impressions = target.metrics.get("impressions", 0)
        if impressions > 0:
            total_engagement = (target.metrics["likes"] + target.metrics["comments"] * 2
                                + target.metrics["saves"] * 3 + target.metrics["shares"] * 4)
            target.metrics["engagement_rate"] = total_engagement / impressions

        # Check if test has enough data to conclude
        if test.status == TestStatus.RUNNING:
            self._check_test_completion(test)

        self._save_test(test)

    def analyze_test(self, test_id: str) -> Dict:
        """Analyze A/B test results and determine winner."""
        test = self.active_tests.get(test_id)
        if not test:
            return {"error": "Test not found"}

        template = self.test_templates.get(test.variable, {})
        primary_metric = template.get("primary_metric", "engagement_rate")

        a_score = test.variant_a.metrics.get(primary_metric, 0)
        b_score = test.variant_b.metrics.get(primary_metric, 0)

        # Simple analysis (in production, use statistical significance)
        if a_score == 0 and b_score == 0:
            return {
                "status": "insufficient_data",
                "message": "Not enough data to determine a winner",
                "a_score": a_score,
                "b_score": b_score,
            }

        total = max(a_score + b_score, 1)
        a_pct = a_score / total
        b_pct = b_score / total

        winner = "a" if a_score >= b_score else "b"
        lift = abs(a_score - b_score) / max(min(a_score, b_score), 1) * 100

        # Determine confidence (simplified)
        sample_a = test.variant_a.metrics.get("impressions", 0)
        sample_b = test.variant_b.metrics.get("impressions", 0)
        total_sample = sample_a + sample_b

        confidence = min(0.99, total_sample / (test.min_sample_size * 2))

        analysis = {
            "test_id": test_id,
            "hypothesis": test.hypothesis,
            "variable": test.variable.value,
            "primary_metric": primary_metric,
            "variant_a": {
                "style": test.variant_a.style,
                "score": a_score,
                "metrics": test.variant_a.metrics,
            },
            "variant_b": {
                "style": test.variant_b.style,
                "score": b_score,
                "metrics": test.variant_b.metrics,
            },
            "winner": winner,
            "winner_style": test.variant_a.style if winner == "a" else test.variant_b.style,
            "lift_pct": round(lift, 1),
            "confidence": round(confidence, 2),
            "statistically_significant": confidence >= SETTINGS.AB_TEST_CONFIDENCE_LEVEL,
            "learning": self._generate_learning(test, winner, lift, primary_metric),
        }

        # Update test
        test.winner = winner
        test.confidence = confidence
        test.learnings = analysis["learning"]

        if analysis["statistically_significant"]:
            test.status = TestStatus.WINNER_SELECTED
            self._record_learning(analysis)

        self._save_test(test)
        logger.info(f"📊 A/B test analyzed: {test_id} | Winner: Variant {winner.upper()} | "
                     f"Lift: {lift:.1f}% | Confidence: {confidence:.0%}")
        return analysis

    def get_accumulated_learnings(self) -> List[Dict]:
        """Get all accumulated learnings from past tests."""
        return self.learnings_db

    def get_best_practices(self) -> Dict:
        """Synthesize best practices from all completed tests."""
        if not self.learnings_db:
            return {"message": "No completed tests yet — start testing!"}

        best_practices = {
            "total_tests_completed": len(self.learnings_db),
            "by_variable": {},
        }

        for learning in self.learnings_db:
            var = learning.get("variable", "unknown")
            if var not in best_practices["by_variable"]:
                best_practices["by_variable"][var] = []
            best_practices["by_variable"][var].append(learning.get("learning", ""))

        return best_practices

    def suggest_next_test(self, recent_content: List[Dict] = None) -> Dict:
        """Suggest the next A/B test to run based on what hasn't been tested."""
        tested_variables = [l.get("variable") for l in self.learnings_db]
        untested = [v for v in TestVariable if v.value not in tested_variables]

        if untested:
            next_var = untested[0]
            template = self.test_templates.get(next_var, {})
            return {
                "suggested_variable": next_var.value,
                "hypothesis": template.get("hypothesis", f"Test {next_var.value}"),
                "reason": f"Haven't tested {next_var.value} yet — potential optimization opportunity"
            }
        else:
            # Re-test the variable with lowest confidence
            lowest_confidence = min(self.learnings_db, key=lambda x: x.get("confidence", 1))
            return {
                "suggested_variable": lowest_confidence.get("variable"),
                "hypothesis": f"Re-test {lowest_confidence.get('variable')} with higher sample",
                "reason": f"Previous test had only {lowest_confidence.get('confidence', 0):.0%} confidence"
            }

    # ─── Private Methods ──────────────────────────────────────────────────

    def _select_test_variable(self) -> TestVariable:
        """Select which variable to test next."""
        tested = [l.get("variable") for l in self.learnings_db]
        untested = [v for v in TestVariable if v.value not in tested]
        return untested[0] if untested else TestVariable.HOOK_STYLE

    def _check_test_completion(self, test: ABTest):
        """Check if a test has enough data to complete."""
        a_impressions = test.variant_a.metrics.get("impressions", 0)
        b_impressions = test.variant_b.metrics.get("impressions", 0)

        if a_impressions >= test.min_sample_size and b_impressions >= test.min_sample_size:
            test.status = TestStatus.COMPLETED
            logger.info(f"✅ A/B test {test.test_id} has sufficient data — ready for analysis")

    def _generate_learning(self, test: ABTest, winner: str,
                            lift: float, metric: str) -> str:
        """Generate a human-readable learning from test results."""
        winner_variant = test.variant_a if winner == "a" else test.variant_b
        loser_variant = test.variant_b if winner == "a" else test.variant_a

        return (f"'{winner_variant.style}' outperformed '{loser_variant.style}' "
                f"by {lift:.0f}% on {metric} for {test.topic} content. "
                f"Hypothesis: {test.hypothesis}")

    def _record_learning(self, analysis: Dict):
        """Record a learning from a completed test."""
        self.learnings_db.append({
            "variable": analysis["variable"],
            "learning": analysis["learning"],
            "winner_style": analysis["winner_style"],
            "lift_pct": analysis["lift_pct"],
            "confidence": analysis["confidence"],
            "timestamp": datetime.now().isoformat(),
        })

    def _save_test(self, test: ABTest):
        """Save test to disk."""
        try:
            filepath = self.storage_path / f"{test.test_id}.json"
            data = {
                "test_id": test.test_id,
                "hypothesis": test.hypothesis,
                "variable": test.variable.value,
                "topic": test.topic,
                "status": test.status.value,
                "created_at": test.created_at,
                "winner": test.winner,
                "confidence": test.confidence,
                "learnings": test.learnings,
                "variant_a": {
                    "name": test.variant_a.name,
                    "style": test.variant_a.style,
                    "metrics": test.variant_a.metrics,
                },
                "variant_b": {
                    "name": test.variant_b.name,
                    "style": test.variant_b.style,
                    "metrics": test.variant_b.metrics,
                },
            }
            filepath.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"❌ Failed to save test: {e}")


# Global instance
ab_testing_engine = ABTestingEngine()
