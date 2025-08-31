from django.db import models
#User, Trade, Rule, Insight
# trademind_app/models.py
from django.db import models
from django.contrib.auth.models import User
#from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

# --- CHOICE OPTIONS ---
EMOTION_CHOICES = [
    ('fear', '😨 Fear'),
    ('angry', '😡 Angry'),
    ('sad', '😢 Sad'),
    ('neutral', '😐 Neutral'),
    ('happy', '😊 Happy'),
    ('chill', '🧘‍♂️ Chill'),
]

TRADER_TYPES = [
    ('day', 'Day Trader'),
    ('swing', 'Swing Trader'),
    ('scalper', 'Scalper'),
]

SESSION_CHOICES = [
    ('asia', 'Asia Session'),
    ('london', 'London Session'),
    ('ny', 'New York Session'),
]

PAIR_CHOICES = [
    ('BTC/USD', 'BTC/USD'),
    ('ETH/USD', 'ETH/USD'),
    ('XRP/USD', 'XRP/USD'),
    ('SOL/USD', 'SOL/USD'),
    ('Gold', 'Gold'),
    ('Oil', 'Oil'),
    ('GBP/USD','GBP/USD'),
    ('EUR/GBP','EUR/GBP'),
    ('USD/JPY','USD/JPY'),
    ('Custom', 'Custom Pair'),
    
]


# --- PROFILE: Trader Type ---
class TraderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trader_type = models.CharField(
        max_length=10,
        choices=TRADER_TYPES,
        default='day'
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_trader_type_display()}"

# Signal to auto-create profile on user signup..used to be here

        
        
# --- STRATEGY: Rule-Based Discipline Checklist ---
class StrategyRule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='strategy_rules')
    rule_text = models.CharField(
        max_length=200,
        help_text="e.g., 'RSI < 30', 'Price at support', 'Risk < 2%'"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Strategy Rule"
        verbose_name_plural = "Strategy Rules"
        ordering = ['-created_at']

    def __str__(self):
        return self.rule_text


# --- TRADE LOG: Core Data Entry ---
class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    session = models.CharField(max_length=10, choices=SESSION_CHOICES)
    pair = models.CharField(max_length=20, choices=PAIR_CHOICES)
    entry = models.CharField(max_length=4, choices=[('BUY', 'BUY'), ('SELL', 'SELL')])
    
    # Financials
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loss = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Emotions: Pre & Post Trade
    pre_trade_emotion = models.CharField(
        max_length=10,
        choices=EMOTION_CHOICES,
        help_text="Emotion BEFORE entering the trade"
    )
    post_trade_emotion = models.CharField(
        max_length=10,
        choices=EMOTION_CHOICES,
        help_text="Emotion AFTER exiting the trade"
    )

    # Discipline: Rules Followed
    rules_followed = models.ManyToManyField(
        StrategyRule,
        blank=True,
        help_text="Which rules did you follow in this trade?"
    )

    # Journal Entry
    reason = models.TextField(
        help_text="Why did you take this trade? What was your mindset?"
    )
    #Optional fields
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conclusion = models.TextField(blank=True, help_text="What did you learn from this trade?")
    screenshot = models.ImageField(upload_to='trade_screenshots/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    #Added
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.pair} | {self.entry} | {self.date}"


# --- AI INSIGHT: Behavioral Analysis ---
class AIInsight(models.Model):
    trade = models.OneToOneField(Trade, on_delete=models.CASCADE, related_name='insight')
    
    insight = models.TextField(help_text="AI-generated behavioral insight")
    risk_pattern = models.CharField(
        max_length=100,
        help_text="e.g., 'Revenge trading after loss', 'FOMO entry'"
    )
    discipline_score = models.IntegerField(
        help_text="1-10: How disciplined was this trade?",
        choices=[(i, i) for i in range(1, 11)]
    )
    coaching_tip = models.TextField(help_text="Actionable tip from AI coach")

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI Insight"
        verbose_name_plural = "AI Insights"
        ordering = ['-generated_at']

    def __str__(self):
        return f"Insight: {self.trade.pair} - {self.discipline_score}/10"
