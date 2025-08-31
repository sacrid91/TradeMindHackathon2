# Django forms
# trademind_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Trade, StrategyRule


# --- SIGNUP FORM ---
class TraderSignupForm(UserCreationForm):
    trader_type = forms.ChoiceField(
        choices=[
            ('day', 'Day Trader'),
            ('swing', 'Swing Trader'),
            ('scalper', 'Scalper'),
        ],
        widget=forms.RadioSelect,
        help_text="Select your primary trading style."
    )


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'trader_type']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a professional handle'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
        }
        help_texts = {
            'username': 'Required. 150 characters or fewer.',
            'email': 'We’ll never share your email. Used for recovery only.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters.'
        )
        self.fields['password2'].help_text = 'Enter the same password for verification.'


# --- STRATEGY RULE FORM ---
class StrategyRuleForm(forms.ModelForm):
    class Meta:
        model = StrategyRule
        fields = ['rule_text']
        widgets = {
            'rule_text': forms.TextInput(attrs={
                'class': 'rule-input',
                'placeholder': 'e.g., "RSI < 30 and price at support"',
                'maxlength': '200'
            })
        }
        help_texts = {
            'rule_text': 'Keep it specific, measurable, and actionable.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rule_text'].label = ""  # Clean UI for inline adding


# --- TRADE LOG FORM ---
class TradeLogForm(forms.ModelForm):
    # Custom fields for better control
    pre_trade_emotion = forms.ChoiceField(
        choices=[
            ('fear', '😨 Fear'),
            ('angry', '😡 Angry'),
            ('sad', '😢 Sad'),
            ('neutral', '😐 Neutral'),
            ('happy', '😊 Happy'),
            ('chill', '🧘‍♂️ Chill'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'emotion-slider'}),
        label="Pre-Trade Emotion",
        help_text="How did you feel BEFORE entering the trade?"
    )
    
    

    post_trade_emotion = forms.ChoiceField(
        choices=[
            ('fear', '😨 Fear'),
            ('angry', '😡 Angry'),
            ('sad', '😢 Sad'),
            ('neutral', '😐 Neutral'),
            ('happy', '😊 Happy'),
            ('chill', '🧘‍♂️ Chill'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'emotion-slider'}),
        label="Post-Trade Emotion",
        help_text="How did you feel AFTER exiting the trade?"
    )

    rules_followed = forms.ModelMultipleChoiceField(
        queryset=StrategyRule.objects.none(),  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'rule-checkbox'}),
        required=False,
        help_text="Check the rules you followed. Unchecked = discipline slip."
    )
    
    class Meta:
        model = Trade
        fields = [
            'date', 'session', 'pair', 'entry', 'profit', 'loss',
            'pre_trade_emotion', 'post_trade_emotion', 'rules_followed', 'reason',
            'lot_size', 'conclusion', 'screenshot'  # ← New fields
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Why did you take this trade? What was your mindset? Be honest.'
            }),
            'profit': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g., 240.50'}),
            'loss': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g., 120.00'}),
            'conclusion': forms.Textarea(attrs={'rows': 3}),
            'lot_size': forms.NumberInput(attrs={'step': '0.01'}),
        }
        help_texts = {
            'reason': 'This is where the Psychee leaks out. Be real.',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            rules = StrategyRule.objects.filter(user=user)
            print(f"[DEBUG] User {user.username} has {rules.count()} rules: {[str(r) for r in rules]}")
            # Limit rules_followed to user's own rules
            
            # Set the queryset
            self.fields['rules_followed'].queryset = StrategyRule.objects.filter(user=user)
            
            # Rebuild the choices to reflect the new queryset
            self.fields['rules_followed'].choices = [
                (rule.id, rule.rule_text) for rule in rules
            ]
            
            print(f"[DEBUG] rules_followed choices: {self.fields['rules_followed'].choices}")

        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = self.fields['date'].initial or forms.DateInput().format_value(None)

    def clean(self):
        cleaned_data = super().clean()
        profit = cleaned_data.get("profit")
        loss = cleaned_data.get("loss")

        if profit and loss:
            raise forms.ValidationError("A trade cannot be both profitable and losing.")
        if not profit and not loss:
            raise forms.ValidationError("Please enter either profit or loss.")

        return cleaned_data