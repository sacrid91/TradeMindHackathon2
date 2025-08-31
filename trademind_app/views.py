from django.shortcuts import render
#All views
# trademind_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction

from .forms import TraderSignupForm, TradeLogForm, StrategyRuleForm
from .models import Trade, StrategyRule, AIInsight
from django.conf import settings
#from intasend import APIService
from django.db.models import Avg, Case, When, Value, FloatField
import os

from .ai_coach import get_ai_insight,_mock_insight_on_failure #Updated import

# --- PUBLIC: Landing Page ---
def landing(request):
    """
    Public landing page. No auth required.
    Displays the psychological hook: "Your Edge Isn't Just Strategy — It's Your Psychee."
    CTA: "LOCK IN" → redirects to signup
    """
    return render(request, 'landing.html')


# --- AUTH: Signup with Trader Type ---
def signup(request):
    """
    Custom signup view that includes trader type.
    On success: creates TraderProfile, logs user in, redirects to dashboard.
    """
    if request.method == 'POST':
        form = TraderSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"[DEBUG] User created: {user.username}")  # ✅ Debug line
            login(request, user)
            messages.success(request, "Welcome to TradeMind! Your Psychee journey begins.")
            return redirect('trademind_app:dashboard')
        else:
            print(f"[DEBUG] Form errors: {form.errors}")  # ✅ See what’s failing
    else:
        form = TraderSignupForm()
    return render(request, 'signup.html', {'form': form})


# --- DASHBOARD: Main Hub ---
@login_required
def dashboard(request):
    """
    User's main hub.
    Shows:
    - Recent trades
    - Discipline score
    - Emotion trends
    - CTA: Log a new trade
    - AI Insight Nudge (if available)
    """
    trades = Trade.objects.filter(user=request.user).order_by('-date', '-created_at')[:5]
    rules = StrategyRule.objects.filter(user=request.user)
    
    total_trades = Trade.objects.filter(user=request.user).count()
    winning_trades = Trade.objects.filter(user=request.user, profit__isnull=False).count()
    losing_trades = Trade.objects.filter(user=request.user, loss__isnull=False, profit__isnull=True).count()
    
    # ✅ Calculate win rate in Python
    win_rate = 0
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
    
    context = {
        'trades': trades,
        'rules': rules,
        'total_trades': Trade.objects.filter(user=request.user).count(),
        'winning_trades': Trade.objects.filter(user=request.user, profit__isnull=False).count(),
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 1),  # e.g., 66.7
    }
    return render(request, 'dashboard.html', context)


# --- TRADE LOG: Create or Edit ---
@login_required
def trade_log(request):
    """
    Form to log a new trade.
    Pre-fills rules for the user.
    On POST: saves trade, redirects to AI insight.
    """
    if request.method == 'POST':
        form = TradeLogForm(request.POST, user=request.user)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.save()
            form.save_m2m()  # Save ManyToMany (rules_followed)
            messages.success(request, "Trade logged. Time to analyze your Psychee.")
            return redirect('trademind_app:ai_insight', trade_id=trade.id)
    else:
        form = TradeLogForm(user=request.user)
    
    return render(request, 'trade_log.html', {'form': form})


# --- AI INSIGHT: Behavioral Analysis (Monetizable) ---
@login_required
def ai_insight(request, trade_id):
    """
    Shows AI-generated insight on a trade.
    - Free: Basic insight
    - Premium (IntaSend): Deep analysis, PDF, coaching
    This is the monetization gate.
    """
    trade = get_object_or_404(Trade, id=trade_id, user=request.user)
    
    # Try to get existing insight
    insight = getattr(trade, 'insight', None)
    
    if not insight:
        # ✅ Prepare data for AI Coach
        trade_data = {
            'entry': trade.entry,
            'pair': trade.pair,
            'profit': str(trade.profit) if trade.profit else None,
            'loss': str(trade.loss) if trade.loss else None,
            'pre_trade_emotion': trade.get_pre_trade_emotion_display(),
            'post_trade_emotion': trade.get_post_trade_emotion_display(),
            'rules_followed_count': trade.rules_followed.count(),
            'rules_total': StrategyRule.objects.filter(user=request.user).count(),
            'reason': trade.reason,
        }

        # ✅ Call the real AI Coach
        try:
            insight_dict = get_ai_insight(trade_data)
            
            
            # ✅ Save to database
            insight = AIInsight.objects.create(
                trade=trade,
                insight=insight_dict['insight'],
                risk_pattern=insight_dict['risk_pattern'],
                discipline_score=insight_dict['discipline_score'],
                coaching_tip=insight_dict['coaching_tip']
            )
            messages.success(request, "AI insight generated from behavioral patterns.")
            
        except Exception as e:
            # messages.error(request, "AI temporarily busy. Try again later.")
            
            # Fallback to mock if needed
#            insight_dict = {
#                "insight": "High emotional volatility detected after losing trade.",
#                "risk_pattern": "Revenge trading",
#                "discipline_score": 4,
#                "coaching_tip": "Pause for 10 minutes after a loss. Recheck your rules before re-entering."
#            }
            insight_dict = _mock_insight_on_failure(trade_data)
            insight = AIInsight.objects.create(trade=trade, **insight_dict)

    context = {
        'trade': trade,
        'insight': insight,
        'intasend_public_key': os.getenv('INTASEND_PUBLISHABLE_KEY', 'ISPubKey_test_d2b2b1b1-d54e-4359-a693-2115db931170'),
        'insight_cost_kes': 5000,
        'debug':settings.DEBUG,
    }
    return render(request, 'ai_insight.html', context)


# --- STRATEGY RULES: Add/Delete ---
@login_required
def add_strategy_rule(request):
    """
    AJAX-friendly view to add a new rule.
    View to add a new strategy rule.
    - POST: Create the rule and redirect to trade log
    -GET: Show a simple form to add a rule
    """
    if request.method == 'POST':
        form = StrategyRuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.user = request.user
            rule.save()
            messages.success(request, "Rule added to your discipline checklist.")
            return redirect('trademind_app:trade_log')
        #If form is invalid,fall through to re-render with error
    else:
        #GET request -show empty form
        form = StrategyRuleForm()
            
    return render(request, 'add_rule.html',{'form':form})

@login_required
def edit_strategy_rule(request, rule_id):
    """
    Edit an existing strategy rule.
    """
    rule = get_object_or_404(StrategyRule, id=rule_id, user=request.user)
    
    if request.method == 'POST':
        form = StrategyRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, "Rule updated.")
            return redirect('trademind_app:dashboard')
    else:
        form = StrategyRuleForm(instance=rule)
    
    return render(request, 'edit_rule.html', {'form': form, 'rule': rule})


@login_required
def delete_strategy_rule(request, rule_id):
    """
    Delete a strategy rule (with confirmation warning via template)
    """
    rule = get_object_or_404(StrategyRule, id=rule_id, user=request.user)
    if request.method == 'POST':
        rule.delete()
        messages.success(request, "Rule removed.")
    return redirect('trademind_app:dashboard')


# --- Optional: Theme Toggle (Future) ---
# def toggle_theme(request):
#     current = request.session.get('dark_mode', True)
#     request.session['dark_mode'] = not current
#     return redirect(request.META.get('HTTP_REFERER', '/'))

# trademind_app/views.py
from django.core.paginator import Paginator
from django.db.models import Q

def trade_history(request):
    trades = Trade.objects.filter(user=request.user).order_by('-date')

    # Filters
    pair = request.GET.get('pair')
    session = request.GET.get('session')
    profit = request.GET.get('profit')
    loss = request.GET.get('loss')
    date = request.GET.get('date')

    if pair:
        trades = trades.filter(pair__icontains=pair)
    if session:
        trades = trades.filter(session=session)
    if profit:
        trades = trades.filter(profit__gte=profit)
    if loss:
        trades = trades.filter(loss__gte=loss)
    if date:
        trades = trades.filter(date=date)

    paginator = Paginator(trades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'trade_history.html', {
        'page_obj': page_obj,
        'trades': trades,  # For balance calc
        'filter_form': TradeLogForm(request.GET)  # Reuse form for filters
    })
    
    
    

@login_required
def dashboard(request):
    trades = Trade.objects.filter(user=request.user).order_by('-date', '-created_at')[:5]
    rules = StrategyRule.objects.filter(user=request.user)
    
    total_trades = Trade.objects.filter(user=request.user).count()
    winning_trades = Trade.objects.filter(user=request.user, profit__isnull=False).count()
    losing_trades = Trade.objects.filter(user=request.user, loss__isnull=False, profit__isnull=True).count()
    
    win_rate = 0
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100

    #  Calculate average P&L by pre-trade emotion
    emotion_pnl = Trade.objects.filter(user=request.user).values('pre_trade_emotion').annotate(
        avg_pnl=Avg(
            Case(
                When(profit__isnull=False, then='profit'),
                When(loss__isnull=False, then='loss'),
                output_field=FloatField()
            )
        )
    )

    # Convert to dictionary for template
    emotion_pnl_data = {
        item['pre_trade_emotion']: item['avg_pnl'] or 0
        for item in emotion_pnl
    }

    # Ensure all emotions are present
    default_emotions = ['fear', 'angry', 'sad', 'neutral', 'happy', 'chill']
    for emo in default_emotions:
        if emo not in emotion_pnl_data:
            emotion_pnl_data[emo] = 0

    context = {
        'trades': trades,
        'rules': rules,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 1),
        'emotion_pnl_data': emotion_pnl_data,  # Pass to template
    }
    return render(request, 'dashboard.html', context)